"""Custom variable GUI widgets and combo integration."""

import re
from typing import cast

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QPlainTextEdit,
    QTextEdit,
    QVBoxLayout,
)

from .custom_var_engine import (
    evaluate_custom_var,
)
from .custom_var_engine import (
    validate_lines_sequential as _validate_lines_sequential,
)

SENTINEL = "Custom var..."


# --- Dialog: now a single textbox with one-or-more "name = expr" lines -------
_LINE_RE = re.compile(r"^\s*(!?[A-Za-z_]\w*)\s*=\s*(.+?)\s*$")


class CustomVarDialog(QDialog):
    def __init__(self, Data, parent=None):
        super().__init__(parent)
        self.Data = Data
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
        """Return a list of tuples.

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
            _validate_lines_sequential(self.Data, seq)
        except Exception as ex:
            self.err.setText(f"Invalid definitions: {ex}")
            return
        self._pairs = pairs
        self.accept()

    @property
    def values(self):
        # Backwards-compatible name (used by _on_activated)
        return self._pairs


def setup_var_selector(combo: QComboBox, Data):
    """Set up a QComboBox to handle custom variable creation and re-apply."""
    if combo.property("_cv_connected"):
        # still re-apply on each load
        _reapply_custom_vars(combo, Data)
        return
    combo.setProperty("_cv_connected", True)
    combo.setProperty("_last", 0 if combo.count() else -1)
    if combo.property("_cv_defs") is None:
        combo.setProperty("_cv_defs", [])  # list[(name, expr)]
    combo.activated.connect(lambda i: _on_activated(combo, int(i), Data))
    _reapply_custom_vars(combo, Data)


def _on_activated(combo: QComboBox, idx: int, Data):
    # Always use the live Data from the main window if available
    Data = getattr(combo.window(), "Data", Data)

    if combo.itemText(idx) != SENTINEL:
        combo.setProperty("_last", idx)
        return
    last = combo.property("_last")
    if last is not None and last >= 0:
        combo.setCurrentIndex(last)
    dlg = CustomVarDialog(Data, combo.window())
    if dlg.exec() != QDialog.DialogCode.Accepted:
        return

    # tuples: (display_name, expr_display, hidden, clean_name, expr_clean)
    pairs = dlg.values or []
    stored = list(combo.property("_cv_defs") or [])

    for display_name, expr_display, hidden, clean_name, expr_clean in pairs:
        # evaluate & assign on Data using clean values
        try:
            evaluate_custom_var(Data, clean_name, expr_clean, assign=True)
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
        info = cast(QTextEdit, top.info_label)
        lines = []
        for tup in stored:
            if len(tup) == 3:
                disp_name, _clean, disp_expr = tup
                lines.append(f"{disp_name} = {disp_expr}")
            else:
                # backward-compat if older pairs (name, expr)
                n, e = tup
                lines.append(f"{n} = {e}")
        old_text = info.toPlainText()
        base = old_text.split("\n\nCustom variables:")[0]
        info.setPlainText(f"{base}\n\nCustom variables:\n" + "\n".join(lines))


def _reapply_custom_vars(combo: QComboBox, Data):
    """Recreate previously defined session custom vars on new Data, silently skipping failures."""
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
            evaluate_custom_var(Data, clean_name, expr_clean, assign=True)
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
