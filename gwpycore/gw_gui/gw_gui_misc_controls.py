from PyQt5.QtWidgets import QAbstractButton, QButtonGroup

def find_button_in_group_by_text(button_group: QButtonGroup, text) -> QAbstractButton:
    for button in button_group.buttons():
        if button.text() == text:
            return button
    return None

def clear_button_group(button_group: QButtonGroup):
    button_group.setExclusive(False)
    for button in button_group.buttons():
        button.setChecked(False)
    button_group.setExclusive(True)


__all__ = ("find_button_in_group_by_text","clear_button_group")
