import streamlit as st
import pandas as pd

# --- Page Configuration ---
st.set_page_config(
    page_title="Market Eaze",
    page_icon="🥕",
    layout="centered",
    initial_sidebar_state="auto",
)

# --- App State Initialization ---
# Using st.session_state to hold our data, login status, and cart.
# In a real-world app, this would be a persistent database.

# Initialize product data with user-provided image URLs
if 'products' not in st.session_state:
    st.session_state.products = [
        {
            'id': 'tomato-vendora', 'name': 'Fresh Tomatoes', 'price': 2.50, 'quantity': 50, 'vendor_id': 'VendorA',
            'image_url': 'https://images.unsplash.com/photo-1582284540020-8acbe03f4924?w=400'
        },
        {
            'id': 'carrot-vendorb', 'name': 'Organic Carrots', 'price': 3.00, 'quantity': 30, 'vendor_id': 'VendorB',
            'image_url': 'https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?w=400'
        },
        {
            'id': 'lettuce-vendora', 'name': 'Crisp Lettuce', 'price': 1.75, 'quantity': 40, 'vendor_id': 'VendorA',
            'image_url': 'https://images.unsplash.com/photo-1515356956468-873dd257f911?q=80&w=400'
        },
        {
            'id': 'broccoli-vendorb', 'name': 'Green Broccoli', 'price': 4.50, 'quantity': 25, 'vendor_id': 'VendorB',
            'image_url': 'https://plus.unsplash.com/premium_photo-1668618249843-e343f5b2447f?w=400'
        },
        {
            'id': 'onion-vendora', 'name': 'Red Onions', 'price': 1.50, 'quantity': 60, 'vendor_id': 'VendorA',
            'image_url': 'https://images.unsplash.com/photo-1587374290079-69274851532d?w=400'
        },
        {
            'id': 'potato-vendorb', 'name': 'Russet Potatoes', 'price': 2.00, 'quantity': 100, 'vendor_id': 'VendorB',
            'image_url': 'https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=400'
        }
    ]

# Initialize login state and shopping cart
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.username = None
if 'cart' not in st.session_state:
    st.session_state.cart = []


# --- Helper Functions ---

def find_product_index(product_id):
    """Finds the index of a product in the session state list by its ID."""
    for i, product in enumerate(st.session_state.products):
        if product['id'] == product_id:
            return i
    return None

def generate_product_id(name, vendor_id):
    """Generates a simple, unique ID for a product."""
    return f"{name.lower().replace(' ', '-')}-{vendor_id.lower()}"

def add_to_cart(product):
    """Adds a product to the shopping cart."""
    product_index = find_product_index(product['id'])
    if product_index is None:
        st.error("Product not found!")
        return

    # Decrement stock
    st.session_state.products[product_index]['quantity'] -= 1

    # Check if item is already in cart
    for item in st.session_state.cart:
        if item['id'] == product['id']:
            item['quantity'] += 1
            st.toast(f"Added another {product['name']} to cart!")
            return

    # If not in cart, add it
    new_cart_item = product.copy()
    new_cart_item['quantity'] = 1
    st.session_state.cart.append(new_cart_item)
    st.toast(f"Added {product['name']} to cart!")

def logout():
    """Resets the session state to log the user out."""
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.username = None
    st.session_state.cart = [] # Clear cart on logout
    st.rerun()

# --- UI Components ---

def login_screen():
    """Displays the login UI."""
    st.title("Welcome to 🥕 Market Eaze")
    st.markdown("Please log in to continue.")

    with st.form("login_form"):
        role = st.selectbox("I am a:", ["Buyer", "Vendor"])
        username = st.text_input("Username", help="If you are a Buyer, you can leave this blank.")
        
        submitted = st.form_submit_button("Login")
        if submitted:
            if role == "Vendor" and not username:
                st.error("Vendor must provide a username.")
            else:
                st.session_state.logged_in = True
                st.session_state.user_role = role
                st.session_state.username = username if role == "Vendor" else "Buyer"
                st.rerun()

def buyer_view():
    """Displays the UI for buyers with a visual product browser."""
    st.header("Browse Our Fresh Vegetables")
    
    search_term = st.text_input("Search for vegetables...", key="buyer_search")

    if search_term:
        filtered_products = [
            p for p in st.session_state.products if search_term.lower() in p['name'].lower()
        ]
    else:
        filtered_products = st.session_state.products

    if not filtered_products:
        st.info("No products found. The market might be empty or your search term didn't match.")
    else:
        cols = st.columns(3)
        for i, product in enumerate(filtered_products):
            col = cols[i % 3]
            with col:
                with st.container(border=True):
                    # Standardize image size
                    st.image(product['image_url'], width=200)
                    st.subheader(product['name'])
                    st.markdown(f"**Vendor:** {product['vendor_id']}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric(label="Price", value=f"${product['price']:.2f}")
                    with col2:
                        st.metric(label="Stock", value=product['quantity'])

                    is_disabled = product['quantity'] == 0
                    if st.button("Add to Cart", key=f"add_{product['id']}", disabled=is_disabled, use_container_width=True):
                        add_to_cart(product)
                        st.rerun()

def vendor_view():
    """Displays the UI for vendors."""
    vendor_id = st.session_state.username
    st.header(f"Manage Your Stall ({vendor_id})")

    with st.form("vendor_form", clear_on_submit=True):
        st.subheader("Add / Update a Product")
        product_name = st.text_input("Product Name")
        product_price = st.number_input("Price (per kg/unit)", min_value=0.01, format="%.2f")
        product_quantity = st.number_input("Quantity in Stock", min_value=0, step=1)
        product_image_url = st.text_input("Image URL", placeholder="https://images.unsplash.com/your-image-url")
        
        submitted = st.form_submit_button("Save Product")
        if submitted:
            if not product_name or not product_image_url:
                st.warning("Please provide a product name and an image URL.")
            else:
                product_id = generate_product_id(product_name, vendor_id)
                existing_product_index = find_product_index(product_id)
                
                if existing_product_index is not None:
                    st.session_state.products[existing_product_index]['price'] = product_price
                    st.session_state.products[existing_product_index]['quantity'] = product_quantity
                    st.session_state.products[existing_product_index]['image_url'] = product_image_url
                    st.success(f"Updated {product_name}!")
                else:
                    new_product = {
                        'id': product_id, 'name': product_name, 'price': product_price,
                        'quantity': product_quantity, 'vendor_id': vendor_id, 'image_url': product_image_url
                    }
                    st.session_state.products.append(new_product)
                    st.success(f"Added {product_name} to the market!")

    st.divider()

    st.subheader("Your Current Listings")
    vendor_products = [p for p in st.session_state.products if p['vendor_id'] == vendor_id]

    if not vendor_products:
        st.info("You haven't listed any products yet. Use the form above to add one.")
    else:
        for product in vendor_products:
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            with col1: st.write(product['name'])
            with col2: st.write(f"${product['price']:.2f}")
            with col3: st.write(product['quantity'])
            with col4:
                if st.button("🗑️", key=f"del_{product['id']}", help=f"Delete {product['name']}"):
                    product_index_to_delete = find_product_index(product['id'])
                    if product_index_to_delete is not None:
                        del st.session_state.products[product_index_to_delete]
                        st.toast(f"Removed {product['name']} from your listings.")
                        st.rerun()

def shopping_cart_view():
    """Displays the shopping cart in the sidebar."""
    st.sidebar.subheader("🛒 Your Cart")
    if not st.session_state.cart:
        st.sidebar.info("Your cart is empty.")
        return

    total_cost = 0
    for item in st.session_state.cart:
        subtotal = item['price'] * item['quantity']
        total_cost += subtotal
        st.sidebar.text(f"{item['name']} (x{item['quantity']}) - ${subtotal:.2f}")
    
    st.sidebar.divider()
    st.sidebar.metric("Total Cost", f"${total_cost:.2f}")

    if st.sidebar.button("Checkout", use_container_width=True):
        st.success("Checkout successful! Thank you for your purchase.")
        # Restore stock (for prototype purposes)
        for cart_item in st.session_state.cart:
            product_index = find_product_index(cart_item['id'])
            if product_index is not None:
                 # In a real app, this logic would be different (e.g., order fulfillment)
                 pass
        st.session_state.cart = [] # Clear the cart
        st.rerun()


# --- Main App Logic ---

if not st.session_state.logged_in:
    login_screen()
else:
    # --- Main Application UI after login ---
    st.sidebar.title(f"Welcome, {st.session_state.username}!")
    st.sidebar.markdown(f"**Role:** {st.session_state.user_role}")
    st.sidebar.button("Logout", on_click=logout)
    st.sidebar.divider()

    st.title("🥕 Market Eaze")

    if st.session_state.user_role == "Buyer":
        shopping_cart_view()
        buyer_view()
    elif st.session_state.user_role == "Vendor":
        vendor_view()
