import json
import os
import re
import sys
from datetime import datetime
 
LOG_NAME = "orders.txt"
DATA_NAME = "orders.json"
PRICE_NAME = "price.txt"
DEFAULT_PRICES = [1, 2, 15, 1, 4, 20, 10]  
 
 
def app_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))
 
 
def resource_path(name):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, name)
 
 
def _path(name):
    return os.path.join(app_dir(), name)
 
 
def _now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
 
 
def _append(text):
    try:
        with open(_path(LOG_NAME), "a", encoding="utf-8") as f:
            f.write(text)
        return True
    except OSError:
        return False
 
 
def log_order(order):
    return _append(
        f"[{_now()}] NEW ORDER {order['id']}\n"
        f"  Customer : {order['name']}\n"
        f"  Phone    : {order['phone'] or 'N/A'}\n"
        f"  Account  : {order['account'] or 'N/A'}\n"
        f"  Source   : {order['source']}\n"
        f"  Job      : {order['job']}\n"
        f"  Amount   : ₱{order['amount']:.2f}\n"
        f"  Status   : {order['status']}\n"
        f"{'-' * 60}\n"
    )
 
 
def log_status(order_id, status):
    return _append(f"[{_now()}] STATUS {order_id} -> {status}\n{'-' * 60}\n")
 
 
def save_orders(orders):
    try:
        with open(_path(DATA_NAME), "w", encoding="utf-8") as f:
            json.dump(orders, f, indent=2, ensure_ascii=False)
        return True
    except OSError:
        return False
 
 
def load_orders():
    try:
        with open(_path(DATA_NAME), "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (OSError, ValueError):
        return []
 
 
def load_prices():
    try:
        with open(_path(PRICE_NAME), "r", encoding="utf-8") as f:
            values = [int(line.strip()) for line in f if line.strip()]
        if len(values) == 7:
            return values
    except (OSError, ValueError):
        pass
    return list(DEFAULT_PRICES)
 
 
def save_prices(values):
    try:
        with open(_path(PRICE_NAME), "w", encoding="utf-8") as f:
            for value in values:
                f.write(f"{value}\n")
        return True
    except OSError:
        return False
 
 
def last_order_number(orders=None, default=1000):
    """Continue order codes after a restart (PS-1004 comes after PS-1003)."""
    numbers = [default]
    for order in orders or []:
        match = re.search(r"PS-(\d+)", str(order.get("id", "")))
        if match:
            numbers.append(int(match.group(1)))
    try:
        with open(_path(LOG_NAME), "r", encoding="utf-8") as f:
            numbers += [int(n) for n in re.findall(r"NEW ORDER PS-(\d+)", f.read())]
    except OSError:
        pass
    return max(numbers)
 
