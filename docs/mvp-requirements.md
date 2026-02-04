# MVP Requirements: Automated Inventory & Supplier Reporting System

## Goal
Deliver a simple web application that lets businesses track products and suppliers, monitor stock, record sales, and receive automated stock reports by email on a schedule.

## Users & Roles
- **Admin** (primary)
  - Manages products, suppliers, sales, and report settings.
- **Staff** (secondary)
  - Records sales and views inventory.

## Core Features (Must Have)
### 1) Authentication (Basic)
- Simple login system.
- Two roles: **Admin** and **Staff**.

### 2) Product & Inventory Management
- Add products with:
  - Product name
  - Quantity
  - Cost price
  - Selling price
- Update product quantity.
- View product list.
- Low-stock indicator (fixed threshold).

### 3) Supplier Management
- Add suppliers:
  - Supplier name
  - Phone / Email
- Link suppliers to products.

### 4) Sales Recording
- Record sales manually.
- Decrease product quantity when a sale is recorded.

### 5) Automated Reports (Basic)
Generate summary reports:
- Daily stock summary
- Weekly stock summary
- Monthly stock summary

Reports include:
- Total products
- Low stock items
- Sales total

### 6) Scheduled Report Sending
- Email reports automatically:
  - Daily at 7 PM
  - Weekly on Sunday
  - Monthly at month-end

### 7) Admin Contact Settings
- Admin can save an email address.
- Reports always sent to the saved admin email.

### 8) Basic Dashboard
Show:
- Total number of products
- Low stock items
- Today’s sales
- Current date & time

## Non-Goals (Out of Scope)
- Barcode / QR scanning
- SMS & WhatsApp delivery
- Mobile native app
- Multi-warehouse support
- Advanced analytics & charts
- Audit logs
- CSV/Excel import/export

## MVP Success Criteria
- Admin can add products & suppliers.
- Stock updates correctly after sales.
- Low stock is visible.
- Reports are sent automatically on schedule.
- System works online and on mobile browsers.
