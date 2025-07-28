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
# Using st.session_state to hold our data and user login status.
# In a real-world app, this would be a persistent database.

# Initialize product data with image URLs if it doesn't exist
if 'products' not in st.session_state:
    st.session_state.products = [
        {
            'id': 'tomato-vendora', 'name': 'Fresh Tomatoes', 'price': 2.50, 'quantity': 50, 'vendor_id': 'VendorA',
            'image_url': 'https://images.unsplash.com/photo-1561155653-295af1c2a6c6?w=400'
        },
        {
            'id': 'carrot-vendorb', 'name': 'Organic Carrots', 'price': 3.00, 'quantity': 30, 'vendor_id': 'VendorB',
            'image_url': 'https://images.unsplash.com/photo-1590868309235-ea34bed7bd7f?w=400'
        },
        {
            'id': 'lettuce-vendora', 'name': 'Crisp Lettuce', 'price': 1.75, 'quantity': 40, 'vendor_id': 'VendorA',
            'image_url': 'https://images.unsplash.com/photo-1556801712-9c1d5e419e34?w=400'
        },
        {
            'id': 'broccoli-vendorb', 'name': 'Green Broccoli', 'price': 4.50, 'quantity': 25, 'vendor_id': 'VendorB',
            'image_url': 'https://images.unsplash.com/photo-1587351177733-a03efcae3ebc?w=400'
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

# Initialize login state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.username = None

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

def logout():
    """Resets the session state to log the user out."""
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.username = None
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
        # Display products in a responsive grid
        cols = st.columns(3)
        for i, product in enumerate(filtered_products):
            col = cols[i % 3]
            with col:
                with st.container(border=True):
                    # Display the product image
                    st.image(product['image_url'], use_column_width=True)
                    st.subheader(product['name'])
                    st.markdown(f"**Vendor:** {product['vendor_id']}")
                    
                    # Price and Quantity in one line
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric(label="Price", value=f"${product['price']:.2f}")
                    with col2:
                        st.metric(label="Stock", value=product['quantity'])

                    # Buy button
                    is_disabled = product['quantity'] == 0
                    if st.button("Buy 1", key=f"buy_{product['id']}", disabled=is_disabled, use_container_width=True):
                        product_index = find_product_index(product['id'])
                        if product_index is not None:
                            st.session_state.products[product_index]['quantity'] -= 1
                            st.toast(f"You bought 1 {product['name']}!")
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
        product_image_url = st.text_input("Image URL", placeholder="https://example.com/image.jpg")
        
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
            with col1:
                st.write(product['name'])
            with col2:
                st.write(f"${product['price']:.2f}")
            with col3:
                st.write(product['quantity'])
            with col4:
                if st.button("🗑️", key=f"del_{product['id']}", help=f"Delete {product['name']}"):
                    product_index_to_delete = find_product_index(product['id'])
                    if product_index_to_delete is not None:
                        del st.session_state.products[product_index_to_delete]
                        st.toast(f"Removed {product['name']} from your listings.")
                        st.rerun()

# --- Main App Logic ---

if not st.session_state.logged_in:
    login_screen()
else:
    # --- Main Application UI after login ---
    st.sidebar.title(f"Welcome, {st.session_state.username}!")
    st.sidebar.markdown(f"**Role:** {st.session_state.user_role}")
    st.sidebar.button("Logout", on_click=logout)

    st.title("🥕 Market Eaze")

    if st.session_state.user_role == "Buyer":
        buyer_view()
    elif st.session_state.user_role == "Vendor":
        vendor_view()
