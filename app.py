import streamlit as st
import sqlite3
import pandas as pd

# ---------------- CONFIG ----------------
st.set_page_config(page_title="O2C SAP System", page_icon="💼", layout="wide")

# ---------------- CSS ----------------
st.markdown("""
<style>
body {
    background-color: #f4f6f9;
}

h1 {
    color: #1f2d3d;
    text-align: center;
    font-weight: 700;
}

.section {
    background-color: white;
    padding: 20px;
    border-radius: 12px;
    margin-bottom: 20px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.08);
}

.kpi {
    background: linear-gradient(135deg, #4facfe, #00f2fe);
    color: white;
    padding: 20px;
    border-radius: 12px;
    text-align: center;
}

.kpi2 {
    background: linear-gradient(135deg, #43e97b, #38f9d7);
    color: white;
    padding: 20px;
    border-radius: 12px;
    text-align: center;
}

.kpi3 {
    background: linear-gradient(135deg, #fa709a, #fee140);
    color: white;
    padding: 20px;
    border-radius: 12px;
    text-align: center;
}

.stButton>button {
    background: linear-gradient(135deg, #0072ff, #00c6ff);
    color: white;
    border-radius: 6px;
    height: 2.8em;
    width: auto;
    padding: 0 20px;
    font-weight: 600;
}

.footer {
    text-align:center;
    font-size:12px;
    color:gray;
    margin-top:30px;
}

/* -------- SIDEBAR NAVIGATION BIGGER -------- */

section[data-testid="stSidebar"] .stRadio > div {
    gap: 10px;
}

section[data-testid="stSidebar"] label {
    font-size: 16px !important;
    padding: 10px;
    border-radius: 8px;
    display: block;
    transition: 0.2s;
}

section[data-testid="stSidebar"] label:hover {
    background-color: #e6f0ff;
}

section[data-testid="stSidebar"] input:checked + div {
    background-color: #0072ff !important;
    color: white !important;
    border-radius: 8px;
    padding: 10px;
}

</style>
""", unsafe_allow_html=True)

# ---------------- HEADER BAR ----------------
st.markdown("""
<div style='
    background: linear-gradient(90deg, #1e3c72, #2a5298);
    padding: 15px 30px;
    border-radius: 10px;
    color: white;
    margin-bottom: 20px;
'>
    <h2 style='margin:0;'>💼 SAP O2C System</h2>
    <p style='margin:0; font-size:14px;'>Enterprise Sales Cycle Simulation</p>
</div>
""", unsafe_allow_html=True)

# ---------------- DB ----------------
conn = sqlite3.connect('database.db', check_same_thread=False)
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer TEXT,
    product TEXT,
    quantity INTEGER,
    total REAL)''')

c.execute('''CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER,
    amount REAL,
    mode TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE,
    price REAL
)''')

conn.commit()

# ---------------- SIDEBAR ----------------
st.sidebar.title("📌 Navigation")
menu = st.sidebar.radio(" ", ["📊 Dashboard", "⚙️ Operations"])

# ---------------- LOAD DATA ----------------
customers = pd.read_sql("SELECT * FROM customers", conn)
orders = pd.read_sql("SELECT * FROM orders", conn)
payments = pd.read_sql("SELECT * FROM payments", conn)
products = pd.read_sql("SELECT * FROM products", conn)

# ================= DASHBOARD =================
if menu == "📊 Dashboard":

    st.title("💼 O2C Dashboard")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="kpi">
            <div>Total Customers</div>
            <h2>{len(customers)}</h2>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="kpi2">
            <div>Total Orders</div>
            <h2>{len(orders)}</h2>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        revenue = orders['total'].sum() if not orders.empty else 0
        st.markdown(f"""
        <div class="kpi3">
            <div>Total Revenue</div>
            <h2>₹{revenue}</h2>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    st.write("### 📊 Analytics")

    col4, col5 = st.columns(2)

    with col4:
        st.markdown('<div class="section">', unsafe_allow_html=True)
        st.write("#### 📦 Sales Distribution")

        if not orders.empty:
            chart = orders.groupby('product')['total'].sum()
            st.bar_chart(chart, use_container_width=True)
        else:
            st.markdown("<p style='text-align:center;'>📭 No sales data</p>", unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    with col5:
        st.markdown('<div class="section">', unsafe_allow_html=True)
        st.write("#### 💳 Payment Methods")

        if not payments.empty:
            chart2 = payments['mode'].value_counts()
            st.bar_chart(chart2, use_container_width=True)
        else:
            st.markdown("<p style='text-align:center;'>📭 No payment data</p>", unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

# ================= OPERATIONS =================
if menu == "⚙️ Operations":

    st.title("⚙️ O2C Operations")

    col6, col7 = st.columns(2)

    # ---- CUSTOMER FORM ----
    with col6:
        st.markdown('<div class="section">', unsafe_allow_html=True)
        st.subheader("👤 Create Customer")
        
        if "customer_added" in st.session_state:
            st.success("✅ Customer Added Successfully")
            del st.session_state["customer_added"]
    
        with st.form("customer_form"):
            name = st.text_input("Customer Name")
            submit_customer = st.form_submit_button("Add Customer")

            if submit_customer:

                if not name.strip():
                    st.warning("⚠️ Customer name cannot be empty")

                else:
                    # 🔥 CHECK DUPLICATE
                    existing = pd.read_sql(
                        f"SELECT * FROM customers WHERE LOWER(name)=LOWER('{name}')", conn
                    )

                    if not existing.empty:
                        st.error("❌ Customer already exists!")

                    else:
                        c.execute("INSERT INTO customers (name) VALUES (?)", (name,))
                        conn.commit()
                        st.session_state["customer_added"] = True
                        st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    # ---- ORDER FORM ----
    with col7:
        st.markdown('<div class="section">', unsafe_allow_html=True)
        st.subheader("🛒 Create Order")

        if not customers.empty:
            with st.form("order_form"):
                cust = st.selectbox("Customer", customers['name'])
                
                product_list = list(products['name']) + ["Other"] if not products.empty else ["Other"]
                selected_product = st.selectbox("Product", product_list)

                if selected_product == "Other":
                    product = st.text_input("Enter Product")
                else:
                    product = selected_product 
    
                qty = st.number_input("Quantity", min_value=1)
                submit_order = st.form_submit_button("Create Order")

            if submit_order:

                if not product.strip():
                    st.warning("⚠️ Product name cannot be empty")

                elif qty <= 0:
                    st.warning("⚠️ Quantity must be greater than 0")

                else:
                    # 🔥 DYNAMIC PRICING
                    price_row = products[products['name'] == product.upper()]

                    if not price_row.empty:
                        price = float(price_row['price'].iloc[0])
                    else:
                        price = 100  # fallback

                    total = qty * price

                    c.execute(
                        "INSERT INTO orders (customer, product, quantity, total) VALUES (?, ?, ?, ?)",
                        (cust, product.upper(), qty, total)
                    )
                    conn.commit()

                    st.success(f"✅ Order Created | Total = ₹{total}")
                    st.rerun()
        else:
            st.info("Add customer first")

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    
    # ---- PRODUCT MASTER ----
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.subheader("📦 Product Master")

    with st.form("product_form"):
        pname = st.text_input("Product Name")
        price = st.number_input("Price", min_value=1.0)

        submit_product = st.form_submit_button("Add Product")

        if submit_product:

            if not pname.strip():
                st.warning("⚠️ Enter product name")

            else:
                existing = pd.read_sql(
                    f"SELECT * FROM products WHERE LOWER(name)=LOWER('{pname}')", conn
                )

                if not existing.empty:
                    st.error("❌ Product already exists")

                else:
                    c.execute(
                        "INSERT INTO products (name, price) VALUES (?, ?)",
                        (pname.upper(), price)
                    )
                    conn.commit()
                    st.success("✅ Product Added")
                    st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    # ---- ORDERS ----
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.subheader("📄 Orders")

    orders = pd.read_sql("SELECT * FROM orders", conn)
    st.dataframe(orders, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

       # ---- PAYMENT FORM ----
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.subheader("💳 Process Payment")

    # 🔥 REFRESH DATA HERE (IMPORTANT FIX)
    orders = pd.read_sql("SELECT * FROM orders", conn)
    payments = pd.read_sql("SELECT * FROM payments", conn)

    if not orders.empty:

        with st.form("payment_form"):

            oid = st.selectbox("Order ID", orders['id'])

            # ✅ SAFE ORDER FETCH (FIXED BUG)
            order_row = orders[orders['id'] == oid]

            if not order_row.empty:

                order_total = float(order_row['total'].iloc[0])

                paid_data = pd.read_sql(
                    f"SELECT SUM(amount) as paid FROM payments WHERE order_id={oid}", conn
                )

                already_paid = paid_data['paid'].iloc[0] or 0

                remaining = order_total - already_paid

                st.info(f"Order Total: ₹{order_total} | Paid: ₹{already_paid} | Remaining: ₹{remaining}")

                amt = st.number_input("Amount", min_value=0.0)
                mode = st.selectbox("Mode", ["UPI", "Card", "Cash"])

                submit_payment = st.form_submit_button("Make Payment")

                if submit_payment:

                    if remaining <= 0:
                        st.warning("⚠️ This order is already fully paid")

                    elif amt <= 0:
                        st.warning("⚠️ Enter valid payment amount")

                    elif amt > remaining:
                        st.error(f"❌ Cannot pay more than remaining ₹{remaining}")

                    else:
                        c.execute(
                            "INSERT INTO payments (order_id, amount, mode) VALUES (?, ?, ?)",
                            (oid, amt, mode)
                        )
                        conn.commit()

                        st.success(f"✅ Payment Successful: ₹{amt}")
                        st.rerun()
    else:
        st.info("No orders available")

    st.markdown('</div>', unsafe_allow_html=True)