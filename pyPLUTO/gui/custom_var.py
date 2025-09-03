# pypluto_custom_var_singlefile.py
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QVBoxLayout,
)

SENTINEL = "Custom var..."


# ---- Minimal dialog: name (1 line) + expression (multi-line) ----
class CustomVarDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Custom Variable")
        self.setModal(True)
        self.setMinimumWidth(420)

        self.name_edit = QLineEdit(self)
        self.name_edit.setPlaceholderText("variable name")

        self.expr_edit = QPlainTextEdit(self)
        self.expr_edit.setPlaceholderText("variable expression")
        self.expr_edit.setMinimumHeight(140)

        form = QFormLayout()
        form.addRow(QLabel("Variable name:"), self.name_edit)
        form.addRow(QLabel("Variable expression:"), self.expr_edit)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel,
            Qt.Orientation.Horizontal,
            self,
        )
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

        self._name = None
        self._expr = None

        self.name_edit.returnPressed.connect(self.expr_edit.setFocus)

    def _on_accept(self):
        name = self.name_edit.text().strip()
        expr = self.expr_edit.toPlainText().strip()
        if name and expr:
            self._name, self._expr = name, expr
            self.accept()
        elif not name:
            self.name_edit.setFocus()
        else:
            self.expr_edit.setFocus()

    @property
    def values(self):
        return self._name, self._expr


# ---- Combo hook ----
def setup_var_selector(var_selector: QComboBox, D):
    """Attach once after you add items (including 'Custom var...')."""
    if not getattr(var_selector, "_custom_var_connected", False):
        var_selector.activated[int].connect(
            lambda idx: _on_var_selector_activated(var_selector, idx, D)
        )
        var_selector._custom_var_connected = True
        var_selector._last_real_index = 0 if var_selector.count() > 0 else -1


def _on_var_selector_activated(combo: QComboBox, idx: int, D):
    if combo.itemText(idx) != SENTINEL:
        combo._last_real_index = idx
        return

    if getattr(combo, "_last_real_index", -1) >= 0:
        combo.setCurrentIndex(combo._last_real_index)

    dlg = CustomVarDialog(combo.window())
    if dlg.exec() != QDialog.DialogCode.Accepted:
        return

    name, expr = dlg.values
    if not name:
        return

    # if duplicate, just select
    existing = _find_case_insensitive(combo, name)
    if existing != -1:
        combo.setCurrentIndex(existing)
        combo._last_real_index = existing
        return

    # --- 🔽 HERE: set attribute on dataset D ---
    evaluate_custom_var(D, name, expr)

    # keep sentinel last
    sentinel_idx = _find_exact(combo, SENTINEL)
    insert_at = sentinel_idx if sentinel_idx != -1 else combo.count()
    combo.insertItem(insert_at, name)
    combo.setItemData(insert_at, expr, role=Qt.ItemDataRole.UserRole)
    combo.setCurrentIndex(insert_at)
    combo._last_real_index = insert_at


def _find_case_insensitive(combo: QComboBox, text: str) -> int:
    t = text.lower()
    for i in range(combo.count()):
        if combo.itemText(i).lower() == t:
            return i
    return -1


def _find_exact(combo: QComboBox, text: str) -> int:
    for i in range(combo.count()):
        if combo.itemText(i) == text:
            return i
    return -1


def get_selected_variable(combo: QComboBox):
    idx = combo.currentIndex()
    if idx < 0:
        return None, None
    name = combo.itemText(idx)
    if name == SENTINEL:
        return None, None
    expr = combo.itemData(idx, role=Qt.ItemDataRole.UserRole)
    return name, expr


def evaluate_custom_var(D, name: str, expr: str):
    """
    Evaluate a custom expression in the context of D and attach it as D.<name>.
    Example:
        evaluate_custom_var(D, "B2", "Bx1**2 + Bx2**2 + Bx3**2")
    """
    # Build context: D and all its attributes
    ctx = {"D": D}
    ctx.update(D.__dict__)  # expose D.Bx1, D.Bx2, ... directly

    try:
        result = eval(
            expr, {"__builtins__": {}}, ctx
        )  # disable builtins for safety
    except Exception as e:
        raise ValueError(f"Failed to evaluate expression {expr!r}: {e}") from e

    setattr(D, name, result)
    return result
