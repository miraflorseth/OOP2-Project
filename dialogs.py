from PyQt6.QtWidgets import (
    QComboBox, QDialog, QFormLayout, QFrame, QHBoxLayout, QLabel,
    QPushButton, QVBoxLayout,
)

STATUSES = ["Pending", "Printing", "Ready for Pickup", "Completed", "Cancelled"]


class ConfirmOrderDialog(QDialog):
    """Lets the customer review the order before it is submitted."""

    def __init__(self, customer_name, phone, source, job_details="", total_cost="", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Confirm Order Submission")
        self.setMinimumWidth(380)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        title = QLabel("Confirm Your Order")
        title.setObjectName("dialogTitle")
        layout.addWidget(title)

        card = QFrame()
        card.setObjectName("dialogCard")
        form = QFormLayout(card)
        form.setSpacing(8)
        form.addRow(self._label("Customer Name:"), QLabel(customer_name))
        form.addRow(self._label("Contact Number:"), QLabel(phone if phone else "N/A"))
        form.addRow(self._label("File Source:"), QLabel(source))
        if job_details:
            lbl_job = QLabel(job_details)
            lbl_job.setWordWrap(True)
            form.addRow(self._label("Order Details:"), lbl_job)
        if total_cost:
            lbl_cost = QLabel(total_cost)
            lbl_cost.setObjectName("totalLabel")
            form.addRow(self._label("Total Cost:"), lbl_cost)
        layout.addWidget(card)

        buttons = QHBoxLayout()
        btn_cancel = QPushButton("Cancel")
        btn_cancel.setObjectName("secondaryButton")
        btn_cancel.clicked.connect(self.reject)
        btn_confirm = QPushButton("Confirm & Submit")
        btn_confirm.clicked.connect(self.accept)
        buttons.addWidget(btn_cancel)
        buttons.addWidget(btn_confirm)
        layout.addLayout(buttons)

    @staticmethod
    def _label(text):
        lbl = QLabel(text)
        lbl.setProperty("class", "field-label")
        return lbl


class CustomAlertDialog(QDialog):
    """Simple message popup with an OK button."""

    def __init__(self, title_text, message_text, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title_text)
        self.setMinimumWidth(300)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        lbl_title = QLabel(title_text)
        lbl_title.setObjectName("dialogTitle")
        layout.addWidget(lbl_title)

        lbl_msg = QLabel(message_text)
        lbl_msg.setWordWrap(True)
        layout.addWidget(lbl_msg)

        btn_ok = QPushButton("OK")
        btn_ok.clicked.connect(self.accept)
        layout.addWidget(btn_ok)


class UpdateStatusDialog(QDialog):
    """Lets the admin change an order's status."""

    def __init__(self, order_id, current_status="Pending", parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Update Order {order_id}")
        self.setMinimumWidth(320)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        title = QLabel(f"Order #{order_id}")
        title.setObjectName("dialogTitle")
        layout.addWidget(title)

        
        self.combo_status = QComboBox()
        self.combo_status.addItems(STATUSES)
        self.combo_status.setCurrentText(current_status)

        form = QFormLayout()
        lbl = QLabel("Set Status:")
        lbl.setProperty("class", "field-label")
        form.addRow(lbl, self.combo_status)
        layout.addLayout(form)

        buttons = QHBoxLayout()
        btn_cancel = QPushButton("Cancel")
        btn_cancel.setObjectName("secondaryButton")
        btn_cancel.clicked.connect(self.reject)
        btn_save = QPushButton("Save")
        btn_save.clicked.connect(self.accept)
        buttons.addWidget(btn_cancel)
        buttons.addWidget(btn_save)
        layout.addLayout(buttons)

    def get_selected_status(self) -> str:
        """Getter: returns the status chosen in the combo box."""
        return self.combo_status.currentText()

