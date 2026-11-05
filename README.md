# PrintSync

PrintSync is an offline, local printing shop management system built with Python and PyQt6. The application features separate user and admin screens designed for a dual-monitor setup.

## Project Structure
```text
OOP2B-Final-Project/
├── main.py
├── user_screen.py
├── admin_screen.py
├── dialogs.py
├── order_log.py
├── style.qss
├── price.txt
└── README.md
```

## Features

- **Dual-Monitor Interface** – Separate user and admin screens.
- **Order Management** – Record printing orders, search them, filter by status, and update each order's status.
- **Order Summary** – Display paper sizes, quantities, printing modes, add-ons, and individual prices.
- **Automatic Pricing** – Calculate costs based on paper size, quantity, printing type, binding, and lamination.
- **Editable Prices** – Change prices from the admin screen; the order form updates immediately.
- **Saved Records** – Orders are saved to local files and reload when the app is reopened.
- **File Submission Tracking** – Specify whether customers sent their files through Gmail or Facebook.
- **Customer Information** – Record the customer's name, Facebook account, email address, and phone number.
- **Sales Summary** – Cards for total sales, total orders, and open jobs, plus CSV export.
- **Offline Operation** – Runs locally without requiring an internet connection.

## Technologies Used

- Python
- PyQt6
- Qt Style Sheets (QSS)

## How to Run

```text
pip install PyQt6
python main.py
```

## Default Pricing

| Item | Price |
|---|---:|
| Letter / Short and A4 paper | ₱2.00 per page |
| Legal / Long paper | ₱3.00 per page |
| Photo paper | ₱25.00 per page |
| Black and white printing | +₱2.00 per page |
| Colored printing | +₱3.00 per page |
| Binding | ₱30.00 |
| Lamination | ₱15.00 |

*Prices can be adjusted in the Change Prices tab based on the printing shop's actual rates.*

## Purpose

This project was developed as an Object-Oriented Programming 2 final project to demonstrate GUI development, order management, and object-oriented programming concepts using Python and PyQt6.

## Made By
[ Miraflor, Seth Carlo.T]
