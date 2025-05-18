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
if "category" not in st.session_state:
    st.session_state.category = None

# Product definitions organized by category with Swedish translations
PRODUCTS = {
    "Drycker": {
        "Läsk": 2.50,
        "Vatten": 1.50,
        "Juice": 3.00,
        "Slush": 4.00
    },
    "Popcorn & Chips": {
        "Liten Popcorn": 3.50,
        "Stor Popcorn": 5.00,
        "Potatischips": 2.00,
        "Nachos": 4.50
    },
    "Godis": {
        "Chokladkaka": 2.50,
        "Gelégodis": 3.00,
        "Lakrits": 2.75,
        "Godismix": 4.00
    }
}

# Category emoji mapping
CATEGORY_EMOJIS = {
    "Drycker": "🥤",
    "Popcorn & Chips": "🍿",
    "Godis": "🍫"
}

def add_to_cart(item, category):
    """Add an item to the cart"""
    st.session_state.cart.append({"item": item, "category": category})
    # Insert into Supabase cart table
    supabase.table("cart").insert({
        "item": item,
        "price": PRODUCTS[category][item]
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

def set_category(category):
    """Set the active category"""
    st.session_state.category = category

def calculate_total():
    """Calculate total price of items in cart"""
    return sum(PRODUCTS[cart_item["category"]][cart_item["item"]] for cart_item in st.session_state.cart)

def display_large_emoji(emoji):
    """Display a large emoji using markdown"""
    st.markdown(f"<div style='font-size:50px; text-align:center;'>{emoji}</div>", unsafe_allow_html=True)

def menu_page():
    """Display the main cashier interface"""
    st.title("Barnbutikens Kassa")
    
    # Display current cart
    if st.session_state.cart:
        st.subheader("Nuvarande Varukorg")
        for cart_item in st.session_state.cart:
            item, category = cart_item["item"], cart_item["category"]
            st.write(f"{item}: {PRODUCTS[category][item]:.2f} kr")
        total = calculate_total()
        st.subheader(f"Totalt: {total:.2f} kr")
    
    # Category buttons
    st.subheader("Kategorier")
    category_cols = st.columns(len(PRODUCTS))
    
    for i, category in enumerate(PRODUCTS.keys()):
        with category_cols[i]:
            # Display large emoji above the button
            display_large_emoji(CATEGORY_EMOJIS[category])
            if st.button(f"{category}", key=f"{category}_btn", use_container_width=True):
                set_category(category)
                st.rerun()
    
    # Display items from selected category
    if st.session_state.category:
        st.markdown(f"### {st.session_state.category}")
        st.markdown(f"<div style='font-size:70px; text-align:center;'>{CATEGORY_EMOJIS[st.session_state.category]}</div>", unsafe_allow_html=True)
        
        # Create a grid of product buttons (2 columns)
        items = PRODUCTS[st.session_state.category]
        item_list = list(items.keys())
        
        # Calculate how many rows we need
        rows = (len(item_list) + 1) // 2
        
        for row in range(rows):
            cols = st.columns(2)
            for col in range(2):
                idx = row * 2 + col
                if idx < len(item_list):
                    item = item_list[idx]
                    price = items[item]
                    with cols[col]:
                        if st.button(f"{item}\n{price:.2f} kr", key=f"{item}_btn", use_container_width=True):
                            add_to_cart(item, st.session_state.category)
                            st.rerun()
    
    # Pay and Clear buttons
    col_pay, col_clear = st.columns(2)
    with col_pay:
        # Display emoji above the button
        display_large_emoji("💰")
        if st.button("BETALA NU", key="pay_btn", use_container_width=True):
            go_to_payment()
            st.rerun()
    
    with col_clear:
        # Display emoji above the button
        display_large_emoji("🗑️")
        if st.button("Töm Varukorg", key="clear_btn", use_container_width=True):
            clear_cart()
            st.rerun()

def payment_page():
    """Display the payment page"""
    st.title("Betalning")
    
    # Show cart summary
    if st.session_state.cart:
        st.subheader("Varor att Betala")
        for cart_item in st.session_state.cart:
            item, category = cart_item["item"], cart_item["category"]
            st.write(f"{item}: {PRODUCTS[category][item]:.2f} kr")
        total = calculate_total()
        st.subheader(f"Totalt: {total:.2f} kr")
        
        # Payment method selection (just for UI, not functional)
        payment_method = st.selectbox("Välj Betalningsmetod", ["Kontant", "Betalkort"])
        
        # Pay button
        display_large_emoji("💳")
        if st.button("Slutför Betalning", use_container_width=True):
            complete_payment()
            st.rerun()
    else:
        st.warning("Din varukorg är tom!")
    
    # Back button
    display_large_emoji("⬅️")
    if st.button("Tillbaka till Menyn", use_container_width=True):
        go_to_menu()
        st.rerun()

def success_page():
    """Display success message after payment"""
    st.success("Betalningen lyckades! Tack för ditt köp.")
    
    display_large_emoji("✅")
    if st.button("Tillbaka till Menyn", use_container_width=True):
        go_to_menu()
        st.rerun()

def main():
    # Configure Streamlit page
    st.set_page_config(
        page_title="Barnbutikens Kassa",
        layout="wide",
    )
    
    # Add some custom CSS for larger buttons
    st.markdown("""
    <style>
    div.stButton > button {
        font-size: 24px !important;
        height: 80px;
        padding: 10px;
        white-space: pre-wrap;
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