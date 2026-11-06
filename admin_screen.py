import csv
 
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QComboBox, QFileDialog, QFormLayout, QFrame, QHBoxLayout, QHeaderView,
    QLabel, QLineEdit, QMainWindow, QPushButton, QSpinBox, QTabWidget,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)
 
from dialogs import CustomAlertDialog, STATUSES, UpdateStatusDialog
from order_log import (load_prices, log_order, log_status, save_orders,
                       save_prices)
 
 
class AdminWindow(QMainWindow):
    COLUMNS = ["# Order", "Customer Info", "Job Details", "Source", "Amount", "Status", "Action"]
 
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PrintSync - Admin Screen")
        self.user_window = None
        self.orders = []
        self.build_menu()
        self.init_ui()
 
    # ---------- UI ----------
    def build_menu(self):
        file_menu = self.menuBar().addMenu("&File")
        act_export = QAction("Export Orders to CSV...", self)
        act_export.triggered.connect(self.export_csv)
        act_exit = QAction("Exit", self)
        act_exit.triggered.connect(self.close)
        file_menu.addAction(act_export)
        file_menu.addAction(act_exit)
 
    def make_card(self, title, value):
        card = QFrame()
        card.setProperty("class", "card")
        layout = QVBoxLayout(card)
        lbl_title = QLabel(title)
        lbl_title.setProperty("class", "field-label")
        lbl_value = QLabel(value)
        lbl_value.setObjectName("cardValue")
        layout.addWidget(lbl_title)
        layout.addWidget(lbl_value)
        return card, lbl_value
 
    def init_ui(self):
        # Main tab: summary cards on the left, orders table on the right
        main_page = QWidget()
        main_layout = QHBoxLayout(main_page)
        main_layout.setContentsMargins(12, 8, 12, 12)
        main_layout.setSpacing(16)
        main_layout.addLayout(self.build_cards_column())
        main_layout.addWidget(self.build_orders_section(), 1)
 
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        self.tabs.addTab(main_page, "Main")
        self.tabs.addTab(self.build_price_page(), "Change Prices")
        self.refresh_table()
 
    def build_cards_column(self):
        cards = QVBoxLayout()
        cards.setSpacing(12)
        card_sales, self.label_sales = self.make_card("Total Sales", "₱0")
        card_orders, self.label_orders = self.make_card("Total Orders", "0")
        card_jobs, self.label_jobs = self.make_card("Open Jobs", "0")
        for card in (card_sales, card_orders, card_jobs):
            card.setFixedWidth(220)
            cards.addWidget(card)
        cards.addStretch()
        return cards
 
    def build_orders_section(self):
        section = QWidget()
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
 
        title = QLabel("Orders")
        title.setProperty("class", "section")
        subtitle = QLabel("Live job queue and transaction history. Use the filter to focus on a stage.")
        subtitle.setProperty("class", "field-label")
 
        filters = QHBoxLayout()
        filters.setSpacing(10)
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("Search name or order code...")
        self.combo_filter = QComboBox()
        self.combo_filter.addItems(["All Statuses"] + STATUSES)
        filters.addWidget(self.txt_search, 1)
        filters.addWidget(self.combo_filter)
 
        self.table = QTableWidget()
        self.table.setColumnCount(len(self.COLUMNS))
        self.table.setHorizontalHeaderLabels(self.COLUMNS)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.txt_search.textChanged.connect(self.refresh_table)
        self.combo_filter.currentIndexChanged.connect(self.refresh_table)
        self.table.cellClicked.connect(self.cell_clicked)
 
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addLayout(filters)
        layout.addWidget(self.table)
        return section
 
    # ---------- Orders ----------
    def load_existing(self, orders):
        self.orders = list(orders)
        self.refresh_table()
 
    def add_order(self, order):
        self.orders.append(order)
        if not (log_order(order) and save_orders(self.orders)):
            CustomAlertDialog("History Not Saved",
                              "The order was placed, but the order files could not be written.",
                              self).exec()
        self.refresh_table()
 
    def refresh_table(self):
        search = self.txt_search.text().strip().lower()
        status = self.combo_filter.currentText()
        self.table.setRowCount(0)
        sales = 0
        open_jobs = 0
 
        for order in self.orders:
            if order["status"] != "Cancelled":
                sales += order["amount"]
            if order["status"] not in ("Completed", "Cancelled"):
                open_jobs += 1
 
            matches_search = search in order["name"].lower() or search in order["id"].lower()
            matches_status = status == "All Statuses" or order["status"] == status
            if matches_search and matches_status:
                row = self.table.rowCount()
                self.table.insertRow(row)
                customer = "\n".join(x for x in (order["name"], order["phone"], order["account"]) if x)
                cells = [order["id"], customer, order["job"], order["source"],
                         f"₱{order['amount']:.0f}", order["status"], "Update"]
                for column, text in enumerate(cells):
                    self.table.setItem(row, column, QTableWidgetItem(text))
 
        self.table.resizeRowsToContents()
        self.label_sales.setText(f"₱{sales:.0f}")
        self.label_orders.setText(str(len(self.orders)))
        self.label_jobs.setText(str(open_jobs))
 
    def cell_clicked(self, row, column):
        if column == 6:
            self.update_status(self.table.item(row, 0).text())
 
    def update_status(self, order_id):
        for order in self.orders:
            if order["id"] == order_id:
                dialog = UpdateStatusDialog(order_id, order["status"], self)
                if dialog.exec():
                    order["status"] = dialog.get_selected_status()
                    log_status(order_id, order["status"])
                    save_orders(self.orders)
                    self.refresh_table()
                    self.user_window.update_status_row(order_id, order["status"])
                break
 
    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export Orders", "orders_export.csv", "CSV Files (*.csv)")
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(["Order", "Customer", "Phone", "Account", "Source", "Job", "Amount", "Status"])
                for o in self.orders:
                    writer.writerow([o["id"], o["name"], o["phone"], o["account"],
                                     o["source"], o["job"], f"{o['amount']:.2f}", o["status"]])
            CustomAlertDialog("Export Done", f"Saved {len(self.orders)} orders.", self).exec()
        except OSError:
            CustomAlertDialog("Export Failed", "The file could not be written.", self).exec()
 
    # ---------- Change Prices ----------
    def build_price_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
 
        title = QLabel("Change Prices")
        title.setProperty("class", "section")
        subtitle = QLabel("Press Save to use the new prices on the user screen.")
        subtitle.setProperty("class", "field-label")
 
        labels = ["Letter / Short and A4 paper per page", "Legal / Long paper per page",
                  "Photo Paper per page", "Black and White print per page",
                  "Full Color print per page", "Binding", "Lamination"]
        form = QFormLayout()
        self.price_spins = []
        for label, value in zip(labels, load_prices()):
            spin = QSpinBox()
            spin.setRange(0, 999)
            spin.setPrefix("₱")
            spin.setValue(value)
            form.addRow(QLabel(label), spin)
            self.price_spins.append(spin)
 
        btn_save = QPushButton("Save Prices")
        btn_save.clicked.connect(self.save_prices)
 
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addLayout(form)
        layout.addWidget(btn_save)
        layout.addStretch()
        return page
 
    def save_prices(self):
        values = [spin.value() for spin in self.price_spins]
        if not save_prices(values):
            CustomAlertDialog("Save Failed", "price.txt could not be written.", self).exec()
            return
        self.user_window.set_prices(*values)
        CustomAlertDialog("Prices Saved", "The user screen now uses the new prices.", self).exec()
 
