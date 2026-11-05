import os
import sys

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

from admin_screen import AdminWindow
from order_log import last_order_number, load_orders, load_prices, resource_path
from user_screen import UserWindow


def main():
    app = QApplication(sys.argv)

    qss_path = resource_path("style.qss")
    if os.path.exists(qss_path):
        with open(qss_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    else:
        print(f"Warning: Could not find QSS file at {qss_path}")

    icon_path = resource_path("Print icon.png")
    icon = QIcon(icon_path) if os.path.exists(icon_path) else None
    if icon:
        app.setWindowIcon(icon)

    user_win = UserWindow()
    admin_win = AdminWindow()
    user_win.admin_window = admin_win      
    admin_win.user_window = user_win

    user_win.set_prices(*load_prices())

    orders = load_orders()
    admin_win.load_existing(orders)
    for order in orders:
        user_win.add_status_row(order["id"], order["job"], order["status"])
    user_win.order_count = last_order_number(orders)

    screens = app.screens()
    if len(screens) >= 2:
        user_win.setScreen(screens[0])
        user_win.showMaximized()
        admin_win.setScreen(screens[1])
        admin_win.showMaximized()
    else:
        user_win.show()
        admin_win.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
