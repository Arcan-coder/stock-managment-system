# stock-managment-system

Automated Inventory & Supplier Management System is a web-based MVP that helps businesses manage products, suppliers, and stock levels while automatically generating and emailing daily, weekly, and monthly reports through a mobile-friendly dashboard with admin and staff roles.

## MVP Features Delivered

- Basic authentication with Admin and Staff roles.
- Product and inventory management with low-stock indicators.
- Supplier management with product linkage.
- Manual sales recording that automatically reduces stock.
- Daily, weekly, and monthly report generation with email delivery.
- Admin contact settings for report delivery.
- Dashboard showing totals, low-stock alerts, and today's sales.

## Getting Started

### 1. Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Initialize the database

```bash
flask --app app.py init-db
```

This seeds default users:

- **Admin**: `admin / admin123`
- **Staff**: `staff / staff123`

### 3. Run the app

```bash
python app.py
```

Open `http://localhost:5000` in your browser.

## Report Scheduling

Reports are sent automatically:

- Daily at 7 PM
- Weekly on Sunday at 7 PM
- Monthly on the last day at 7 PM

Configure SMTP environment variables before running to enable email delivery:

```bash
export SMTP_HOST=smtp.example.com
export SMTP_PORT=587
export SMTP_USER=your_user
export SMTP_PASSWORD=your_password
export SMTP_FROM=reports@example.com
```

If SMTP variables are not set, the report content is logged to the console.
