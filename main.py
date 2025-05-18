import os
import streamlit as st
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase = create_client(supabase_url, supabase_key)

# Session state to track cart items
if "cart" not in st.session_state:
    st.session_state.cart = []
if "page" not in st.session_state:
    st.session_state.page = "menu"

# Product definitions
PRODUCTS = {
    "Popcorn": 5.00,
    "Soda": 2.50,
    "Candy": 3.00
}

def add_to_cart(item):
    """Add an item to the cart"""
    st.session_state.cart.append(item)
    # Insert into Supabase cart table
    supabase.table("cart").insert({
        "item": item,
        "price": PRODUCTS[item]
    }).execute()

def clear_cart():
    """Clear the cart"""
    st.session_state.cart = []
    # Delete all items from Supabase cart table
    supabase.table("cart").delete().neq("id", 0).execute()

def go_to_payment():
    """Switch to payment page"""
    st.session_state.page = "payment"

def go_to_menu():
    """Switch back to menu page"""
    st.session_state.page = "menu"

def complete_payment():
    """Complete the payment process"""
    # In a real app, this would integrate with a payment processor
    clear_cart()
    st.session_state.page = "success"

def menu_page():
    """Display the main cashier interface"""
    st.title("Kid's Shop Cashier")
    
    # Display current cart
    if st.session_state.cart:
        st.subheader("Current Cart")
        for item in st.session_state.cart:
            st.write(f"{item}: ${PRODUCTS[item]:.2f}")
        total = sum(PRODUCTS[item] for item in st.session_state.cart)
        st.subheader(f"Total: ${total:.2f}")
    
    # Create 3 columns for the 3 product buttons
    col1, col2, col3 = st.columns(3)
    
    # Big product buttons
    with col1:
        if st.button("🍿 Popcorn\n$5.00", key="popcorn_btn", use_container_width=True):
            add_to_cart("Popcorn")
            st.rerun()
    
    with col2:
        if st.button("🥤 Soda\n$2.50", key="soda_btn", use_container_width=True):
            add_to_cart("Soda")
            st.rerun()
            
    with col3:
        if st.button("🍫 Candy\n$3.00", key="candy_btn", use_container_width=True):
            add_to_cart("Candy")
            st.rerun()
    
    # Pay and Clear buttons
    col_pay, col_clear = st.columns(2)
    with col_pay:
        if st.button("💰 PAY NOW", key="pay_btn", use_container_width=True):
            go_to_payment()
            st.rerun()
    
    with col_clear:
        if st.button("🗑️ Clear Cart", key="clear_btn", use_container_width=True):
            clear_cart()
            st.rerun()

def payment_page():
    """Display the payment page"""
    st.title("Payment")
    
    # Show cart summary
    if st.session_state.cart:
        st.subheader("Items to Pay")
        for item in st.session_state.cart:
            st.write(f"{item}: ${PRODUCTS[item]:.2f}")
        total = sum(PRODUCTS[item] for item in st.session_state.cart)
        st.subheader(f"Total: ${total:.2f}")
        
        # Payment method selection (just for UI, not functional)
        payment_method = st.selectbox("Select Payment Method", ["Cash", "Credit Card"])
        
        # Pay button
        if st.button("Complete Payment", use_container_width=True):
            complete_payment()
            st.rerun()
    else:
        st.warning("Your cart is empty!")
    
    # Back button
    if st.button("Back to Menu", use_container_width=True):
        go_to_menu()
        st.rerun()

def success_page():
    """Display success message after payment"""
    st.success("Payment successful! Thank you for your purchase.")
    
    if st.button("Return to Menu", use_container_width=True):
        go_to_menu()
        st.rerun()

def main():
    # Add some custom CSS for larger buttons
    st.markdown("""
    <style>
    div.stButton > button {
        font-size: 24px !important;
        height: 100px;
        padding: 20px 10px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Display the appropriate page based on session state
    if st.session_state.page == "menu":
        menu_page()
    elif st.session_state.page == "payment":
        payment_page()
    elif st.session_state.page == "success":
        success_page()

if __name__ == "__main__":
    main()