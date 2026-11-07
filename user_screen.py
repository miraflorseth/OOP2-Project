import re
 
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QButtonGroup, QCheckBox, QComboBox, QHBoxLayout, QHeaderView, QLabel,
    QLineEdit, QMainWindow, QPushButton, QSpinBox, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget,
)
 
from dialogs import ConfirmOrderDialog, CustomAlertDialog
from order_log import DEFAULT_PRICES
 
PHONE_RE = re.compile(r"^\+?[\d\-\s]{7,15}$")
 
 
class UserWindow(QMainWindow):
    SIZES = [("Letter / Short", "paper"), ("A4", "paper"),
             ("Legal / Long", "legal"), ("Photo Paper", "photo")]
    COLORS = [("B&W", "bw"), ("Full Color", "color")]
 
    def __init__(self):
        super().__init__()
        self.admin_window = None
        self.order_count = 1000
        self.prices = dict(zip(
            ["paper", "legal", "photo", "bw", "color", "binding", "lamination"],
            DEFAULT_PRICES))
        self.setWindowTitle("PrintSync - User Screen")
        self.build_menu()
        self.init_ui()
        self.set_prices(*DEFAULT_PRICES)
 
    # UI
    def build_menu(self):
        file_menu = self.menuBar().addMenu("&File")
        act_clear = QAction("Clear Form", self)
        act_clear.triggered.connect(self.clear_form)
        act_exit = QAction("Exit", self)
        act_exit.triggered.connect(self.close)
        file_menu.addAction(act_clear)
        file_menu.addAction(act_exit)
 
        help_menu = self.menuBar().addMenu("&Help")
        act_about = QAction("About", self)
        act_about.triggered.connect(lambda: CustomAlertDialog(
            "About PrintSync",
            "PrintSync - offline order management for small printing shops.", self).exec())
        help_menu.addAction(act_about)
 
    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)
 
        title = QLabel("New Print Order Form")
        title.setObjectName("Title")
        root.addWidget(title)
        subtitle = QLabel("Fill in the form, then check the price and order status below.")
        subtitle.setProperty("class", "field-label")
        root.addWidget(subtitle)
 
        # Top: the order form
        root.addLayout(self.build_form())
 
        # Bottom: price on the left, order status table on the right
        bottom = QHBoxLayout()
        bottom.setSpacing(16)
        bottom.addLayout(self.build_price_panel(), 1)
        bottom.addLayout(self.build_status_panel(), 2)
        root.addLayout(bottom, 1)
 
    def labeled(self, text, widget):
        column = QVBoxLayout()
        column.setSpacing(6)
        label = QLabel(text)
        label.setProperty("class", "field-label")
        column.addWidget(label)
        column.addWidget(widget)
        return column
 
    def build_form(self):
        form = QVBoxLayout()
        form.setSpacing(12)
 
        # customer details
        self.txt_name = QLineEdit()
        self.txt_name.setPlaceholderText("e.g. Juan Dela Cruz")
        self.txt_phone = QLineEdit()
        self.txt_phone.setPlaceholderText("0917-XXX-XXXX")
        self.txt_account = QLineEdit()
        self.txt_account.setPlaceholderText("Email or FB Username")
 
        info = QHBoxLayout()
        info.setSpacing(12)
        info.addLayout(self.labeled("Customer Name *", self.txt_name), 1)
        info.addLayout(self.labeled("Contact Number", self.txt_phone), 1)
        info.addLayout(self.labeled("Email / FB Account", self.txt_account), 1)
        form.addLayout(info)
 
        # file source buttons and add-ons
        source_box = QVBoxLayout()
        source_box.setSpacing(6)
        lbl_source = QLabel("File Submission Source")
        lbl_source.setProperty("class", "field-label")
        source_box.addWidget(lbl_source)
 
        source_row = QHBoxLayout()
        source_row.setSpacing(8)
        self.source_group = QButtonGroup(self)
        self.source_group.setExclusive(True)
        self.button_gmail = QPushButton("Gmail")
        self.button_fb = QPushButton("Facebook / Messenger")
        for button in (self.button_gmail, self.button_fb):
            button.setObjectName("sourceButton")
            button.setCheckable(True)
            button.setFixedHeight(36)
            self.source_group.addButton(button)
            source_row.addWidget(button, 1)
        self.button_gmail.setChecked(True)
        source_box.addLayout(source_row)
 
        self.chk_binding = QCheckBox("Binding")
        self.chk_binding.toggled.connect(self.calculate_total)
        self.chk_lamination = QCheckBox("Lamination")
        self.chk_lamination.toggled.connect(self.calculate_total)
        addon_box = QVBoxLayout()
        addon_box.setSpacing(6)
        lbl_addons = QLabel("Add-ons")
        lbl_addons.setProperty("class", "field-label")
        addon_box.addWidget(lbl_addons)
        addons = QHBoxLayout()
        addons.setSpacing(16)
        addons.addWidget(self.chk_binding)
        addons.addWidget(self.chk_lamination)
        addons.addStretch()
        addon_box.addLayout(addons)
 
        row2 = QHBoxLayout()
        row2.setSpacing(24)
        row2.addLayout(source_box, 1)
        row2.addLayout(addon_box, 1)
        form.addLayout(row2)
 
        # print specifications
        self.combo_color = QComboBox()
        for name, key in self.COLORS:
            self.combo_color.addItem(name, key)
        self.combo_color.currentIndexChanged.connect(self.calculate_total)
 
        self.combo_size = QComboBox()
        for name, key in self.SIZES:
            self.combo_size.addItem(name, key)
        self.combo_size.currentIndexChanged.connect(self.calculate_total)
 
        self.spin_pages = QSpinBox()
        self.spin_pages.setRange(1, 1000)
        self.spin_pages.setValue(10)
        self.spin_pages.valueChanged.connect(self.calculate_total)
        self.spin_copies = QSpinBox()
        self.spin_copies.setRange(1, 100)
        self.spin_copies.setValue(1)
        self.spin_copies.valueChanged.connect(self.calculate_total)
 
        lbl_spec = QLabel("Print Specifications")
        lbl_spec.setProperty("class", "section")
        form.addWidget(lbl_spec)
 
        specs = QHBoxLayout()
        specs.setSpacing(12)
        specs.addLayout(self.labeled("Color Mode", self.combo_color), 2)
        specs.addLayout(self.labeled("Paper Size", self.combo_size), 2)
        specs.addLayout(self.labeled("Pages", self.spin_pages), 1)
        specs.addLayout(self.labeled("Copies", self.spin_copies), 1)
        form.addLayout(specs)
        return form
 
    def build_price_panel(self):
        panel = QVBoxLayout()
        panel.setSpacing(12)
 
        lbl_price = QLabel("Price Breakdown")
        lbl_price.setProperty("class", "section")
        panel.addWidget(lbl_price)
 
        self.lbl_breakdown = QLabel()
        self.lbl_breakdown.setObjectName("breakdown")
        panel.addWidget(self.lbl_breakdown)
 
        self.lbl_total = QLabel("₱0")
        self.lbl_total.setObjectName("totalLabel")
        panel.addWidget(self.lbl_total)
 
        self.btn_place_order = QPushButton("Place Order")
        self.btn_place_order.clicked.connect(self.place_order)
        panel.addWidget(self.btn_place_order)
        panel.addStretch()
        return panel
 
    def build_status_panel(self):
        panel = QVBoxLayout()
        panel.setSpacing(12)
 
        lbl_status = QLabel("Order Status")
        lbl_status.setProperty("class", "section")
        panel.addWidget(lbl_status)
 
        self.status_table = QTableWidget()
        self.status_table.setColumnCount(3)
        self.status_table.setHorizontalHeaderLabels(["Order", "Job", "Status"])
        self.status_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.status_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        panel.addWidget(self.status_table)
        return panel
 
    # Logic 
    def calculate_total(self) -> float:
        p = self.prices
        size_key = self.combo_size.currentData()
        paper_cost = p.get(size_key, p["paper"])
        color_key = self.combo_color.currentData()
        print_cost = p["color"] if color_key == "color" else p["bw"]
        color_name = "Full Color" if color_key == "color" else "B&W"
 
        pages = self.spin_pages.value()
        copies = self.spin_copies.value()
        base_paper_total = pages * paper_cost
        color_total = pages * print_cost
 
        addon_cost = 0
        addons = []
        if self.chk_binding.isChecked():
            addon_cost += p["binding"]
            addons.append("Binding")
        if self.chk_lamination.isChecked():
            addon_cost += p["lamination"]
            addons.append("Lamination")
 
        subtotal = base_paper_total + color_total + addon_cost
        total = subtotal * copies
 
        self.lbl_breakdown.setText(
            f"• Base Paper ({self.combo_size.currentText().split(' — ')[0]}): "
            f"{pages} pgs × ₱{paper_cost:.2f} = ₱{base_paper_total:.2f}\n"
            f"• Color Option ({color_name}): {pages} pgs × ₱{print_cost:.2f} = ₱{color_total:.2f}\n"
            f"• Add-ons: {', '.join(addons) if addons else 'None'} = ₱{addon_cost:.2f}\n"
            f"• Multiplier: ₱{subtotal:.2f} × {copies} copy"
        )
        self.lbl_total.setText(f"₱{total:.0f}")
        return total
 
    def place_order(self):
        name = self.txt_name.text().strip()
        phone = self.txt_phone.text().strip()
        account = self.txt_account.text().strip()
        source = self.source_group.checkedButton().text()
 
        if not name:
            CustomAlertDialog("Missing Info", "Please enter the customer name.", self).exec()
            return
        if phone and not PHONE_RE.match(phone):
            CustomAlertDialog("Invalid Contact Number",
                              "Use 7 to 15 digits (spaces, dashes and a leading + are allowed).",
                              self).exec()
            return
 
        pages = self.spin_pages.value()
        copies = self.spin_copies.value()
        size = self.combo_size.currentText().split(" — ")[0]
        color = "Full Color" if self.combo_color.currentData() == "color" else "B&W"
        extras = [text for text, box in (("Binding", self.chk_binding),
                                         ("Lamination", self.chk_lamination)) if box.isChecked()]
        job = ", ".join([f"{pages} pgs", color, size, f"{copies} copy"] + extras)
        total_amount = self.calculate_total()
 
        if not ConfirmOrderDialog(name, phone, source, job, f"₱{total_amount:.2f}", self).exec():
            return
 
        self.order_count += 1
        order_id = f"PS-{self.order_count}"
        order = {"id": order_id, "name": name, "phone": phone, "account": account,
                 "source": source, "job": job, "amount": total_amount, "status": "Pending"}
        self.admin_window.add_order(order)
        self.add_status_row(order_id, job, "Pending")
 
        CustomAlertDialog("Order Placed", f"Your order {order_id} was submitted.", self).exec()
        self.clear_form()
 
    def clear_form(self):
        for box in (self.txt_name, self.txt_phone, self.txt_account):
            box.clear()
 
    def add_status_row(self, order_id, job, status):
        row = self.status_table.rowCount()
        self.status_table.insertRow(row)
        for column, text in enumerate((order_id, job, status)):
            self.status_table.setItem(row, column, QTableWidgetItem(text))
 
    def update_status_row(self, order_id, status):
        for row in range(self.status_table.rowCount()):
            if self.status_table.item(row, 0).text() == order_id:
                self.status_table.item(row, 2).setText(status)
 
    def set_prices(self, paper, legal, photo, bw, color, binding, lamination):
        self.prices = {"paper": paper, "legal": legal, "photo": photo, "bw": bw,
                       "color": color, "binding": binding, "lamination": lamination}
       
        self.combo_size.setItemText(0, f"Letter / Short — ₱{paper:.2f}/pg")
        self.combo_size.setItemText(1, f"A4 — ₱{paper:.2f}/pg")
        self.combo_size.setItemText(2, f"Legal / Long — ₱{legal:.2f}/pg")
        self.combo_size.setItemText(3, f"Photo Paper — ₱{photo:.2f}/pg")
        self.combo_color.setItemText(0, f"B&W — +₱{bw:.2f}/pg")
        self.combo_color.setItemText(1, f"Full Color — +₱{color:.2f}/pg")
        self.chk_binding.setText(f"Binding (+₱{binding})")
        self.chk_lamination.setText(f"Lamination (+₱{lamination})")
        self.calculate_total()
