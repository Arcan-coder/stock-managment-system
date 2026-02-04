# Architecture Outline

## Suggested Stack
- **Frontend:** React (or HTML/CSS/JS) with responsive layout.
- **Backend:** Node.js (Express) with REST APIs.
- **Database:** PostgreSQL (or MySQL).
- **Scheduling:** Cron-based scheduler (e.g., node-cron) to trigger report emails.
- **Email Delivery:** SMTP provider (e.g., SendGrid, Mailgun).

## High-Level Components
- **Web UI**
  - Authentication pages
  - Dashboard
  - Product list & detail
  - Supplier list & detail
  - Sales entry form
  - Admin settings (report email)

- **API Service**
  - Auth endpoints
  - Product CRUD
  - Supplier CRUD
  - Sales recording
  - Report generation
  - Admin settings

- **Scheduler**
  - Daily report job (7 PM)
  - Weekly report job (Sunday)
  - Monthly report job (month-end)

## Data Model (Minimal)
- **User**: id, name, email, password_hash, role
- **Product**: id, name, quantity, cost_price, selling_price, low_stock_threshold
- **Supplier**: id, name, phone, email
- **ProductSupplier**: product_id, supplier_id
- **Sale**: id, product_id, quantity, total_price, sold_at
- **AdminSetting**: id, report_email

## API Endpoints (Draft)
- `POST /api/auth/login`
- `GET /api/dashboard`
- `GET /api/products`
- `POST /api/products`
- `PATCH /api/products/:id`
- `GET /api/suppliers`
- `POST /api/suppliers`
- `POST /api/sales`
- `GET /api/reports/daily`
- `GET /api/reports/weekly`
- `GET /api/reports/monthly`
- `GET /api/admin-settings`
- `PUT /api/admin-settings`
