import os
import smtplib
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, flash, redirect, render_template, request, url_for
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "inventory.db")
LOW_STOCK_DEFAULT = 10

app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ.get("SECRET_KEY", "dev-secret"),
    SQLALCHEMY_DATABASE_URI=f"sqlite:///{DB_PATH}",
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

product_supplier = db.Table(
    "product_supplier",
    db.Column("product_id", db.Integer, db.ForeignKey("product.id"), primary_key=True),
    db.Column("supplier_id", db.Integer, db.ForeignKey("supplier.id"), primary_key=True),
)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    cost_price = db.Column(db.Float, nullable=False, default=0.0)
    selling_price = db.Column(db.Float, nullable=False, default=0.0)
    low_stock_threshold = db.Column(db.Integer, nullable=False, default=LOW_STOCK_DEFAULT)
    suppliers = db.relationship(
        "Supplier",
        secondary=product_supplier,
        back_populates="products",
    )


class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(40))
    email = db.Column(db.String(120))
    products = db.relationship(
        "Product",
        secondary=product_supplier,
        back_populates="suppliers",
    )


class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    product = db.relationship("Product")


class Setting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    admin_email = db.Column(db.String(120), nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.cli.command("init-db")
def init_db_command():
    db.create_all()
    if not User.query.filter_by(username="admin").first():
        admin = User(
            username="admin",
            password_hash=generate_password_hash("admin123"),
            role="admin",
        )
        staff = User(
            username="staff",
            password_hash=generate_password_hash("staff123"),
            role="staff",
        )
        db.session.add_all([admin, staff])
        db.session.commit()
    if not Setting.query.first():
        db.session.add(Setting(admin_email="admin@example.com"))
        db.session.commit()
    print("Initialized the database with default users.")


@app.route("/")
@login_required
def dashboard():
    total_products = Product.query.count()
    low_stock_items = Product.query.filter(Product.quantity <= Product.low_stock_threshold).all()
    start_of_day = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_sales = Sale.query.filter(Sale.created_at >= start_of_day).all()
    today_sales_total = sum(sale.total_price for sale in today_sales)
    return render_template(
        "dashboard.html",
        total_products=total_products,
        low_stock_items=low_stock_items,
        today_sales_total=today_sales_total,
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("dashboard"))
        flash("Invalid credentials. Please try again.", "error")
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/products", methods=["GET", "POST"])
@login_required
def products():
    if request.method == "POST":
        product = Product(
            name=request.form.get("name"),
            quantity=int(request.form.get("quantity", 0)),
            cost_price=float(request.form.get("cost_price", 0)),
            selling_price=float(request.form.get("selling_price", 0)),
            low_stock_threshold=int(request.form.get("low_stock_threshold", LOW_STOCK_DEFAULT)),
        )
        db.session.add(product)
        db.session.commit()
        flash("Product added.", "success")
        return redirect(url_for("products"))

    products_list = Product.query.all()
    return render_template("products.html", products=products_list)


@app.route("/products/<int:product_id>/adjust", methods=["POST"])
@login_required
def adjust_product(product_id):
    product = Product.query.get_or_404(product_id)
    adjust_quantity = int(request.form.get("adjust_quantity", 0))
    product.quantity = max(product.quantity + adjust_quantity, 0)
    db.session.commit()
    flash("Product quantity updated.", "success")
    return redirect(url_for("products"))


@app.route("/suppliers", methods=["GET", "POST"])
@login_required
def suppliers():
    if request.method == "POST":
        supplier = Supplier(
            name=request.form.get("name"),
            phone=request.form.get("phone"),
            email=request.form.get("email"),
        )
        db.session.add(supplier)
        db.session.commit()
        flash("Supplier added.", "success")
        return redirect(url_for("suppliers"))

    suppliers_list = Supplier.query.all()
    products_list = Product.query.all()
    return render_template(
        "suppliers.html",
        suppliers=suppliers_list,
        products=products_list,
    )


@app.route("/suppliers/link", methods=["POST"])
@login_required
def link_supplier():
    supplier_id = int(request.form.get("supplier_id"))
    product_id = int(request.form.get("product_id"))
    supplier = Supplier.query.get_or_404(supplier_id)
    product = Product.query.get_or_404(product_id)
    if product not in supplier.products:
        supplier.products.append(product)
        db.session.commit()
        flash("Supplier linked to product.", "success")
    return redirect(url_for("suppliers"))


@app.route("/sales", methods=["GET", "POST"])
@login_required
def sales():
    if request.method == "POST":
        product_id = int(request.form.get("product_id"))
        quantity = int(request.form.get("quantity", 0))
        product = Product.query.get_or_404(product_id)
        if quantity <= 0:
            flash("Quantity must be greater than zero.", "error")
            return redirect(url_for("sales"))
        if product.quantity < quantity:
            flash("Not enough stock to record this sale.", "error")
            return redirect(url_for("sales"))
        product.quantity -= quantity
        total_price = quantity * product.selling_price
        sale = Sale(product=product, quantity=quantity, total_price=total_price)
        db.session.add(sale)
        db.session.commit()
        flash("Sale recorded.", "success")
        return redirect(url_for("sales"))

    sales_list = Sale.query.order_by(Sale.created_at.desc()).all()
    products_list = Product.query.all()
    return render_template(
        "sales.html",
        sales=sales_list,
        products=products_list,
    )


@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    setting = Setting.query.first()
    if request.method == "POST":
        admin_email = request.form.get("admin_email")
        if setting:
            setting.admin_email = admin_email
        else:
            setting = Setting(admin_email=admin_email)
            db.session.add(setting)
        db.session.commit()
        flash("Admin email updated.", "success")
        return redirect(url_for("settings"))
    return render_template("settings.html", setting=setting)


@app.route("/reports/preview/<period>")
@login_required
def preview_report(period):
    report = generate_report(period)
    return render_template("report.html", report=report, period=period)


def get_period_range(period):
    now = datetime.utcnow()
    if period == "daily":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "weekly":
        start = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "monthly":
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        raise ValueError("Invalid period")
    return start, now


def generate_report(period):
    start, end = get_period_range(period)
    total_products = Product.query.count()
    low_stock = Product.query.filter(Product.quantity <= Product.low_stock_threshold).all()
    sales = Sale.query.filter(Sale.created_at >= start, Sale.created_at <= end).all()
    sales_total = sum(sale.total_price for sale in sales)
    return {
        "start": start,
        "end": end,
        "total_products": total_products,
        "low_stock": low_stock,
        "sales_total": sales_total,
    }


def build_report_email(report, period):
    low_stock_rows = "".join(
        f"<tr><td>{item.name}</td><td>{item.quantity}</td></tr>" for item in report["low_stock"]
    )
    return f"""
    <h2>{period.title()} Stock Summary</h2>
    <p>Period: {report['start'].strftime('%Y-%m-%d')} to {report['end'].strftime('%Y-%m-%d')}</p>
    <p>Total products: {report['total_products']}</p>
    <p>Sales total: ${report['sales_total']:.2f}</p>
    <h3>Low Stock Items</h3>
    <table border="1" cellpadding="6" cellspacing="0">
        <tr><th>Product</th><th>Quantity</th></tr>
        {low_stock_rows or '<tr><td colspan="2">No low stock items.</td></tr>'}
    </table>
    """


def send_report(period):
    setting = Setting.query.first()
    if not setting:
        app.logger.warning("No admin email configured; skipping report.")
        return
    report = generate_report(period)
    body = build_report_email(report, period)
    smtp_host = os.environ.get("SMTP_HOST")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USER")
    smtp_password = os.environ.get("SMTP_PASSWORD")
    smtp_from = os.environ.get("SMTP_FROM", smtp_user)
    if not smtp_host or not smtp_user or not smtp_password or not smtp_from:
        app.logger.warning("SMTP settings missing; report content logged instead.")
        app.logger.info(body)
        return

    message = MIMEMultipart("alternative")
    message["Subject"] = f"{period.title()} Stock Summary"
    message["From"] = smtp_from
    message["To"] = setting.admin_email
    message.attach(MIMEText(body, "html"))

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(message)
        app.logger.info("Sent %s report to %s", period, setting.admin_email)


def configure_scheduler():
    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(lambda: send_report("daily"), "cron", hour=19, minute=0)
    scheduler.add_job(lambda: send_report("weekly"), "cron", day_of_week="sun", hour=19, minute=0)
    scheduler.add_job(lambda: send_report("monthly"), "cron", day="last", hour=19, minute=0)
    scheduler.start()


@app.before_first_request
def start_scheduler():
    configure_scheduler()


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
