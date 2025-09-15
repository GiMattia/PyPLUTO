"""A custom variable evaluator for PyPLUTO."""

import os
import re
import tempfile

import numexpr as ne
import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QPlainTextEdit,
    QVBoxLayout,
)

SENTINEL = "Custom var..."

# --- tiny normalizer ---------------------------------------------------------
# Allow both D.something and bare names; allow np./numpy. prefixes.
_NORM_PATTERNS = [
    (re.compile(r"\bD\."), ""),  # D.Bx1 -> Bx1
    (re.compile(r"\bnp\."), ""),  # np.sqrt -> sqrt
    (re.compile(r"\bnumpy\."), ""),  # numpy.sqrt -> sqrt
]


def _normalize_expr(expr: str) -> str:
    s = expr.strip()
    for pat, repl in _NORM_PATTERNS:
        s = pat.sub(repl, s)
    return s


def _frozen_var_names(D):
    """Names that must never be overridden by custom vars."""
    names = set(map(str, getattr(D, "_load_vars", [])))  # loaded-from-file vars
    names.update({"x1", "x2", "x3"})  # base grid
    g = (getattr(D, "geom", "") or "").upper()
    if g == "CARTESIAN":
        names.update({"x", "y", "z"})
    elif g == "POLAR":
        names.update({"R", "phi", "z", "x", "y", "xr", "yr"})
    elif g == "SPHERICAL":
        names.update({"r", "theta", "phi", "R", "z", "rt", "zt"})
    return names


def _apply_grid_shaping(local, D):
    """
    Reshape only x1/x2/x3 if they are 1-D so they broadcast with D.nshp.
    PyPLUTO order: 1D -> (nx1,), 2D -> (nx1, nx2), 3D -> (nx1, nx2, nx3)
    x1 aligns to axis 0, x2 to axis 1, x3 to axis 2.
    """
    nshp = D.nshp if isinstance(D.nshp, tuple) else tuple(D.nshp)
    for axis, name in enumerate(("x1", "x2", "x3")[: D.dim]):
        v = local.get(name)
        if (
            isinstance(v, np.ndarray)
            and v.ndim == 1
            and v.shape[0] == nshp[axis]
        ):
            try:
                # make a singleton shape on other axes, then broadcast to D.nshp
                pattern = [1] * D.dim
                pattern[axis] = v.shape[0]  # axis-aligned length
                v_view = v.reshape(tuple(pattern))
                local[name] = np.broadcast_to(
                    v_view, nshp
                )  # FINAL SHAPE == D.nshp
            except Exception:
                pass  # stay quiet per your policy

    if D.geom == "CARTESIAN":
        local["x"] = local["x1"]
        local["y"] = local["x2"]
        local["z"] = local["x3"]
    elif D.geom == "POLAR":
        local["R"] = local["x1"]
        local["phi"] = local["x2"]
        local["z"] = local["x3"]
        local["x"] = D.x1c.T[:, :, None] if D.dim == 3 else D.x1c.T
        local["y"] = D.x2c.T[:, :, None] if D.dim == 3 else D.x2c.T
    elif D.geom == "SPHERICAL":
        local["r"] = local["x1"]
        local["theta"] = local["x2"]
        local["phi"] = local["x3"]
        local["R"] = D.x1p.T[:, :, None] if D.dim == 3 else D.x1p.T
        local["z"] = D.x2p.T[:, :, None] if D.dim == 3 else D.x2p.T
        if D.dim == 3:
            local["rt"] = D.x1t.T[:, None, :]
            local["zt"] = D.x3t.T[:, None, :]


# --- evaluator ---------------------------------------------------------------
def evaluate_custom_var(D, name: str, expr: str, *, assign: bool = True):
    """
    numexpr-only, memmap output for arrays, scalar stays scalar.
    Accepts D.foo or foo; np.func/numpy.func or func directly.
    """
    expr = _normalize_expr(expr)

    # Do not allow overriding loaded or grid variables
    if name in _frozen_var_names(D):
        raise ValueError(f"protected name: {name}")

    # Build locals from D (public, non-callable) + constants
    local = {"pi": float(np.pi), "e": float(np.e)}
    for k, v in D.__dict__.items():
        if not k.startswith("_") and not callable(v):
            local[k] = v

    _apply_grid_shaping(local, D)  # <<< add this

    # Parse/compile (syntax check)
    try:
        compiled = ne.NumExpr(expr)
    except Exception as e:
        raise ValueError(f"compile error: {e}")

    # Validate cheaply on only the used names (1-element views)
    names = compiled.input_names
    tiny = {}
    for n in names:
        v = local.get(n)
        if v is None:
            raise ValueError(f"unknown name: {n}")
        tiny[n] = v.reshape(-1)[:1] if isinstance(v, np.ndarray) else v
    try:
        tiny_res = ne.evaluate(expr, local_dict=tiny, global_dict={})
    except Exception as e:
        raise ValueError(f"validation error: {e}")

    # Infer shape from arrays actually referenced (broadcasting)
    arrs = [local[n] for n in names if isinstance(local[n], np.ndarray)]
    if not arrs:
        # Scalar result
        try:
            res = ne.evaluate(expr, local_dict=local, global_dict={})
        except Exception as e:
            raise ValueError(f"evaluate error: {e}")
        if isinstance(res, np.ndarray) and res.shape == ():
            res = res.item()
    else:
        out_shape = np.broadcast(
            *[np.empty(a.shape, dtype=[]) for a in arrs]
        ).shape
        out_dtype = getattr(tiny_res, "dtype", arrs[0].dtype)
        # Tempfile-backed memmap keeps result on disk
        tmp = tempfile.NamedTemporaryFile(
            prefix=f"{name}_", suffix=".dat", delete=False
        )
        tmp_path = tmp.name
        tmp.close()
        try:
            out = np.memmap(
                tmp_path, mode="w+", dtype=out_dtype, shape=out_shape
            )
            ne.evaluate(expr, local_dict=local, global_dict={}, out=out)
            res = out
        except Exception as e:
            try:
                if "out" in locals():
                    del out
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
            except Exception:
                pass
            raise ValueError(f"evaluate error: {e}")

    if assign:
        setattr(D, name, res)
    return res


# --- Dialog: now a single textbox with one-or-more "name = expr" lines -------
_LINE_RE = re.compile(r"^\s*(!?[A-Za-z_]\w*)\s*=\s*(.+?)\s*$")


class CustomVarDialog(QDialog):
    def __init__(self, D, parent=None):
        super().__init__(parent)
        self.D = D
        self.setWindowTitle("Add Custom Variables")
        self.setMinimumWidth(460)

        self.exprs = QPlainTextEdit()
        self.exprs.setPlaceholderText("Define variables:\nA = ...\nB = ...")
        self.exprs.setMinimumHeight(160)

        self.err = QLabel("")
        self.err.setStyleSheet("color:#b00020;")
        self.err.setWordWrap(True)

        form = QFormLayout()
        form.addRow("Variables:", self.exprs)

        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(self._accept)
        btns.rejected.connect(self.reject)

        lay = QVBoxLayout(self)
        lay.addLayout(form)
        lay.addWidget(self.err)
        lay.addWidget(btns)

        self._pairs: list[tuple[str, str]] = []
        self.exprs.textChanged.connect(lambda: self.err.setText(""))

    def _parse_lines(self, text: str):
        """
        Returns a list of tuples:
        (display_name, expr_display, hidden, clean_name, expr_clean)
        - display_name: what the user typed for the name (may start with '!')
        - expr_display: right-hand side exactly as typed (keeps '# comment')
        - hidden: True if name starts with '!'
        - clean_name: display_name without leading '!' (actual Python attribute)
        - expr_clean: expr_display with trailing comment stripped (before evaluation)
        """
        pairs = []
        for raw in text.splitlines():
            if not raw.strip():
                continue
            m = _LINE_RE.match(raw)
            if not m:
                raise ValueError(f"invalid line: {raw!r} (use NAME = EXPR)")
            display_name, expr_display = m.group(1), m.group(2).strip()
            hidden = display_name.startswith("!")
            clean_name = display_name[1:] if hidden else display_name
            expr_clean = expr_display.split("#", 1)[
                0
            ].strip()  # ignore comments when evaluating
            if not expr_clean:
                raise ValueError(
                    f"empty expression after comment stripping in line: {raw!r}"
                )
            pairs.append(
                (display_name, expr_display, hidden, clean_name, expr_clean)
            )
        if not pairs:
            raise ValueError("Please enter at least one 'NAME = EXPR' line.")
        return pairs

    def _accept(self):
        text = self.exprs.toPlainText()
        try:
            pairs = self._parse_lines(text)
            # validate sequentially using clean_name / expr_clean
            seq = [(p[3], p[4]) for p in pairs]  # (clean_name, expr_clean)
            _validate_lines_sequential(self.D, seq)
        except Exception as ex:
            self.err.setText(f"Invalid definitions: {ex}")
            return
        self._pairs = pairs
        self.accept()

    @property
    def values(self):
        # Backwards-compatible name (used by _on_activated)
        return self._pairs


def setup_var_selector(combo: QComboBox, D):
    """Set up a QComboBox to handle custom variable creation and re-apply."""
    if combo.property("_cv_connected"):
        # still re-apply on each load
        _reapply_custom_vars(combo, D)
        return
    combo.setProperty("_cv_connected", True)
    combo.setProperty("_last", 0 if combo.count() else -1)
    if combo.property("_cv_defs") is None:
        combo.setProperty("_cv_defs", [])  # list[(name, expr)]
    combo.activated[int].connect(lambda i: _on_activated(combo, i, D))
    _reapply_custom_vars(combo, D)


def _build_locals(D):
    local = {"pi": float(np.pi), "e": float(np.e)}
    for k, v in D.__dict__.items():
        if not k.startswith("_") and not callable(v):
            local[k] = v
    return local


def _validate_lines_sequential(D, pairs):
    """Cheap, sequential validation using 1-element array views."""
    base = _build_locals(D)
    _apply_grid_shaping(base, D)  # <<< add this
    # tiny env: scalars unchanged, arrays -> 1 element
    tiny = {
        k: (v.reshape(-1)[:1] if isinstance(v, np.ndarray) else v)
        for k, v in base.items()
    }
    tiny["pi"], tiny["e"] = float(np.pi), float(np.e)
    for name, expr in pairs:
        s = _normalize_expr(expr)
        compiled = ne.NumExpr(s)
        names = compiled.input_names
        # ensure all symbols exist
        env = {}
        for n in names:
            if n not in tiny:
                raise ValueError(f"unknown name: {n}")
            env[n] = tiny[n]
            if name in _frozen_var_names(D):
                raise ValueError(
                    f"'{name}' is protected and cannot be redefined"
                )
        try:
            res = ne.evaluate(s, local_dict=env, global_dict={})
        except Exception as e:
            raise ValueError(f"error in '{name} = {expr}': {e}")
        # store the tiny result for subsequent lines
        tiny[name] = res


def _on_activated(combo: QComboBox, idx: int, D):
    if combo.itemText(idx) != SENTINEL:
        combo.setProperty("_last", idx)
        return
    last = combo.property("_last")
    if last is not None and last >= 0:
        combo.setCurrentIndex(last)
    dlg = CustomVarDialog(D, combo.window())
    if dlg.exec() != QDialog.DialogCode.Accepted:
        return

    # tuples: (display_name, expr_display, hidden, clean_name, expr_clean)
    pairs = dlg.values or []
    stored = list(combo.property("_cv_defs") or [])

    for display_name, expr_display, hidden, clean_name, expr_clean in pairs:
        # evaluate & assign on D using clean values
        try:
            evaluate_custom_var(D, clean_name, expr_clean, assign=True)
        except Exception:
            continue  # silent skip per requirement

        # add to combo only if not hidden
        if not hidden:
            # duplicate? select existing
            for i in range(combo.count()):
                if combo.itemText(i).lower() == clean_name.lower():
                    combo.setCurrentIndex(i)
                    combo.setProperty("_last", i)
                    break
            else:
                # insert before sentinel
                sent = next(
                    (
                        i
                        for i in range(combo.count())
                        if combo.itemText(i) == SENTINEL
                    ),
                    -1,
                )
                pos = sent if sent != -1 else combo.count()
                combo.insertItem(pos, clean_name)
                combo.setItemData(
                    pos, expr_clean, role=Qt.ItemDataRole.UserRole
                )
                combo.setCurrentIndex(pos)
                combo.setProperty("_last", pos)

        # store triple so we can reapply (expr_clean) and display comments (expr_display)
        stored.append((display_name, expr_clean, expr_display))

    combo.setProperty("_cv_defs", stored)

    # Refresh info panel if present (shows the display expr with comments)
    top = combo.window()
    if hasattr(top, "info_label") and stored:
        lines = []
        for tup in stored:
            if len(tup) == 3:
                disp_name, _clean, disp_expr = tup
                lines.append(f"{disp_name} = {disp_expr}")
            else:
                # backward-compat if older pairs (name, expr)
                n, e = tup
                lines.append(f"{n} = {e}")
        old_text = top.info_label.toPlainText()
        base = old_text.split("\n\nCustom variables:")[0]
        top.info_label.setPlainText(
            f"{base}\n\nCustom variables:\n" + "\n".join(lines)
        )


def _reapply_custom_vars(combo: QComboBox, D):
    """Recreate previously defined session custom vars on the new D, silently skipping failures."""
    defs = list(combo.property("_cv_defs") or [])
    if not defs:
        return
    for item in defs:
        # Support both (name, expr) legacy pairs and (display_name, expr_clean, expr_display) triples
        if len(item) == 3:
            display_name, expr_clean, _expr_display = item
        else:
            display_name, expr_clean = item
        hidden = display_name.startswith("!")
        clean_name = display_name[1:] if hidden else display_name

        try:
            evaluate_custom_var(D, clean_name, expr_clean, assign=True)
        except Exception:
            continue  # silent skip

        if not hidden and not any(
            combo.itemText(i) == clean_name for i in range(combo.count())
        ):
            sent = next(
                (
                    i
                    for i in range(combo.count())
                    if combo.itemText(i) == SENTINEL
                ),
                -1,
            )
            pos = sent if sent != -1 else combo.count()
            combo.insertItem(pos, clean_name)
            combo.setItemData(pos, expr_clean, role=Qt.ItemDataRole.UserRole)
