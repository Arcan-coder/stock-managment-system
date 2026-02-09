const STORAGE_KEYS = {
  products: "sms.products",
  suppliers: "sms.suppliers",
  transactions: "sms.transactions",
  users: "sms.users",
  auth: "sms.auth",
};

const seedData = {
  products: [
    {
      id: "PRD-001",
      name: "Arabica Beans",
      description: "Premium roast",
      supplier: "Greenleaf Farms",
      costPrice: 18,
      sellingPrice: 28,
      quantity: 120,
      reorderLevel: 30,
      dateAdded: "2024-05-12",
    },
    {
      id: "PRD-002",
      name: "Cold Brew Bottles",
      description: "330ml glass bottles",
      supplier: "Vecta Logistics",
      costPrice: 1.2,
      sellingPrice: 3.5,
      quantity: 45,
      reorderLevel: 40,
      dateAdded: "2024-05-20",
    },
  ],
  suppliers: [
    {
      id: "SUP-101",
      name: "Vecta Logistics",
      phone: "+1 555-0199",
      email: "orders@vecta.io",
      address: "742 Harbor St, Seattle",
      products: "Packaging, cups, lids",
    },
    {
      id: "SUP-102",
      name: "Greenleaf Farms",
      phone: "+1 555-2233",
      email: "hello@greenleaf.com",
      address: "91 Meadow Rd, Portland",
      products: "Beans, syrups",
    },
  ],
  users: [
    {
      id: "USR-01",
      name: "Rita Mensah",
      email: "rita@stockms.com",
      role: "Admin",
      status: "Online",
    },
    {
      id: "USR-02",
      name: "Samuel Otieno",
      email: "samuel@stockms.com",
      role: "Manager",
      status: "Active",
    },
  ],
  transactions: [
    {
      id: "TX-9001",
      productId: "PRD-001",
      type: "OUT",
      quantity: 15,
      date: "2024-06-01",
    },
  ],
};

const formatCurrency = (value) => `$${Number(value).toFixed(2)}`;

const loadData = (key, fallback) => {
  const raw = localStorage.getItem(key);
  if (!raw) {
    localStorage.setItem(key, JSON.stringify(fallback));
    return fallback;
  }
  try {
    return JSON.parse(raw);
  } catch (error) {
    return fallback;
  }
};

const saveData = (key, value) => {
  localStorage.setItem(key, JSON.stringify(value));
};

const ensureSeed = () => {
  Object.entries(seedData).forEach(([key, value]) => {
    const storageKey = STORAGE_KEYS[key];
    if (!localStorage.getItem(storageKey)) {
      localStorage.setItem(storageKey, JSON.stringify(value));
    }
  });
};

const getAuth = () => loadData(STORAGE_KEYS.auth, { role: "Admin" });

const setAuth = (role) => {
  saveData(STORAGE_KEYS.auth, { role });
};

const renderDashboard = () => {
  const products = loadData(STORAGE_KEYS.products, []);
  const suppliers = loadData(STORAGE_KEYS.suppliers, []);
  const transactions = loadData(STORAGE_KEYS.transactions, []);

  const lowStock = products.filter((product) => product.quantity <= product.reorderLevel);

  const statProducts = document.getElementById("statProducts");
  const statLowStock = document.getElementById("statLowStock");
  const statSuppliers = document.getElementById("statSuppliers");
  const statReports = document.getElementById("statReports");

  if (statProducts) statProducts.textContent = products.length;
  if (statLowStock) statLowStock.textContent = lowStock.length;
  if (statSuppliers) statSuppliers.textContent = suppliers.length;
  if (statReports) statReports.textContent = Math.max(1, transactions.length);
};

const renderProducts = () => {
  const products = loadData(STORAGE_KEYS.products, []);
  const tbody = document.getElementById("productsTableBody");
  if (!tbody) return;

  tbody.innerHTML = products
    .map(
      (product) => `
      <tr>
        <td>${product.id}</td>
        <td>${product.name}</td>
        <td>${product.supplier}</td>
        <td>${formatCurrency(product.costPrice)} / ${formatCurrency(product.sellingPrice)}</td>
        <td>${product.quantity}</td>
        <td>${product.reorderLevel}</td>
      </tr>`
    )
    .join("");
};

const renderSuppliers = () => {
  const suppliers = loadData(STORAGE_KEYS.suppliers, []);
  const tbody = document.getElementById("suppliersTableBody");
  if (!tbody) return;

  tbody.innerHTML = suppliers
    .map(
      (supplier) => `
      <tr>
        <td>${supplier.id}</td>
        <td>${supplier.name}</td>
        <td>${supplier.phone}</td>
        <td>${supplier.email}</td>
        <td>${supplier.products}</td>
      </tr>`
    )
    .join("");
};

const renderTransactions = () => {
  const transactions = loadData(STORAGE_KEYS.transactions, []);
  const tbody = document.getElementById("transactionsTableBody");
  if (!tbody) return;

  tbody.innerHTML = transactions
    .map(
      (tx) => `
      <tr>
        <td>${tx.id}</td>
        <td>${tx.productId}</td>
        <td>${tx.type}</td>
        <td>${tx.quantity}</td>
        <td>${tx.date}</td>
      </tr>`
    )
    .join("");
};

const renderUsers = () => {
  const users = loadData(STORAGE_KEYS.users, []);
  const tbody = document.getElementById("usersTableBody");
  if (!tbody) return;

  tbody.innerHTML = users
    .map(
      (user) => `
      <tr>
        <td>${user.id}</td>
        <td>${user.name}</td>
        <td>${user.role}</td>
        <td>${user.status}</td>
      </tr>`
    )
    .join("");
};

const renderReports = () => {
  const products = loadData(STORAGE_KEYS.products, []);
  const transactions = loadData(STORAGE_KEYS.transactions, []);
  const tbody = document.getElementById("reportsTableBody");
  if (!tbody) return;

  const lowStockCount = products.filter((product) => product.quantity <= product.reorderLevel).length;
  const salesCount = transactions.filter((tx) => tx.type === "OUT").length;

  const reportRows = [
    {
      name: "Daily stock report",
      status: `${products.length} products tracked`,
      notes: `${lowStockCount} low-stock items`,
    },
    {
      name: "Sales report",
      status: `${salesCount} sales logged`,
      notes: "Auto-updated after each stock out",
    },
    {
      name: "Supplier report",
      status: "2 suppliers active",
      notes: "Next review on Friday",
    },
  ];

  tbody.innerHTML = reportRows
    .map(
      (report) => `
      <tr>
        <td>${report.name}</td>
        <td>${report.status}</td>
        <td>${report.notes}</td>
      </tr>`
    )
    .join("");
};

const bindLogin = () => {
  const loginForm = document.getElementById("loginForm");
  const loginOverlay = document.getElementById("loginOverlay");

  if (!loginForm) return;

  loginForm.addEventListener("submit", (event) => {
    event.preventDefault();
    const role = new FormData(loginForm).get("role") || "admin";
    setAuth(role);
    if (loginOverlay) {
      loginOverlay.classList.add("show");
    }
    setTimeout(() => {
      window.location.href = "/dashboard.html";
    }, 1400);
  });
};

const bindProductForm = () => {
  const form = document.getElementById("productForm");
  if (!form) return;

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const data = new FormData(form);
    const products = loadData(STORAGE_KEYS.products, []);
    products.push({
      id: data.get("productId"),
      name: data.get("productName"),
      description: data.get("description"),
      supplier: data.get("supplier"),
      costPrice: Number(data.get("costPrice")),
      sellingPrice: Number(data.get("sellingPrice")),
      quantity: Number(data.get("quantity")),
      reorderLevel: Number(data.get("reorderLevel")),
      dateAdded: data.get("dateAdded"),
    });
    saveData(STORAGE_KEYS.products, products);
    form.reset();
    renderProducts();
  });
};

const bindSupplierForm = () => {
  const form = document.getElementById("supplierForm");
  if (!form) return;

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const data = new FormData(form);
    const suppliers = loadData(STORAGE_KEYS.suppliers, []);
    suppliers.push({
      id: data.get("supplierId"),
      name: data.get("supplierName"),
      phone: data.get("phone"),
      email: data.get("email"),
      address: data.get("address"),
      products: data.get("products"),
    });
    saveData(STORAGE_KEYS.suppliers, suppliers);
    form.reset();
    renderSuppliers();
  });
};

const bindTransactionForm = () => {
  const form = document.getElementById("transactionForm");
  if (!form) return;

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const data = new FormData(form);
    const transactions = loadData(STORAGE_KEYS.transactions, []);
    const products = loadData(STORAGE_KEYS.products, []);
    const productId = data.get("productId");
    const quantity = Number(data.get("quantity"));
    const type = data.get("type");

    const product = products.find((item) => item.id === productId);
    if (product) {
      product.quantity += type === "IN" ? quantity : -quantity;
    }

    transactions.push({
      id: `TX-${Date.now()}`,
      productId,
      type,
      quantity,
      date: data.get("date"),
    });

    saveData(STORAGE_KEYS.transactions, transactions);
    saveData(STORAGE_KEYS.products, products);
    form.reset();
    renderTransactions();
    renderProducts();
  });
};

const bindUserForm = () => {
  const form = document.getElementById("userForm");
  if (!form) return;

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const data = new FormData(form);
    const users = loadData(STORAGE_KEYS.users, []);
    users.push({
      id: data.get("userId"),
      name: data.get("userName"),
      email: data.get("userEmail"),
      role: data.get("userRole"),
      status: "Active",
    });
    saveData(STORAGE_KEYS.users, users);
    form.reset();
    renderUsers();
  });
};

const bindReportRefresh = () => {
  const button = document.getElementById("refreshReports");
  if (!button) return;

  button.addEventListener("click", () => {
    renderReports();
  });
};

const initPage = () => {
  ensureSeed();
  bindLogin();
  bindProductForm();
  bindSupplierForm();
  bindTransactionForm();
  bindUserForm();
  bindReportRefresh();

  renderDashboard();
  renderProducts();
  renderSuppliers();
  renderTransactions();
  renderUsers();
  renderReports();

  const roleBadge = document.getElementById("roleBadge");
  if (roleBadge) {
    const auth = getAuth();
    roleBadge.textContent = `Role: ${auth.role}`;
  }
};

document.addEventListener("DOMContentLoaded", initPage);
