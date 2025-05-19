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
        "Läsk": 25.0,
        "Vatten": 15.0,
        "Juice": 30.0,
        "Slush": 40.0
    },
    "Popcorn & Chips": {
        "Liten Popcorn": 35.0,
        "Stor Popcorn": 50.0,
        "Potatischips": 20.0,
        "Nachos": 45.0
    },
    "Godis": {
        "Chokladkaka": 25.0,
        "Gelégodis": 30.0,
        "Lakrits": 27.5,
        "Godismix": 40.0
    },
    "Biobiljetter": {
        "Frost 3": 85.0,
        "Toy Story 5": 85.0,
        "Minioner: Grus Hämnd": 75.0,
        "Superhjältarna 3": 80.0,
        "Sing 3": 75.0
    }
}

# Category emoji mapping
CATEGORY_EMOJIS = {
    "Drycker": "🥤",
    "Popcorn & Chips": "🍿",
    "Godis": "🍫",
    "Biobiljetter": "🎬"
}

# Item emoji mapping
ITEM_EMOJIS = {
    "Läsk": "🥤",
    "Vatten": "💧",
    "Juice": "🧃",
    "Slush": "🧊",
    "Liten Popcorn": "🍿",
    "Stor Popcorn": "🍿",
    "Potatischips": "🥔",
    "Nachos": "🧀",
    "Chokladkaka": "🍫",
    "Gelégodis": "🍬",
    "Lakrits": "🖤",
    "Godismix": "🍭",
    "Frost 3": "❄️",
    "Toy Story 5": "🤠",
    "Minioner: Grus Hämnd": "🟡",
    "Superhjältarna 3": "🦸",
    "Sing 3": "🎤"
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

def display_cart_sidebar():
    """Display cart in the sidebar"""
    with st.sidebar:
        st.title("Varukorg")
        
        if st.session_state.cart:
            for i, cart_item in enumerate(st.session_state.cart):
                item, category = cart_item["item"], cart_item["category"]
                emoji = ITEM_EMOJIS.get(item, "📦")
                
                # Create a container for better styling
                item_col, price_col = st.columns([3, 2])
                with item_col:
                    st.write(f"{emoji} {item}")
                with price_col:
                    st.write(f"{PRODUCTS[category][item]:.2f} kr")
                
                # Add a subtle separator
                if i < len(st.session_state.cart) - 1:
                    st.markdown("<hr style='margin:2px 0; opacity:0.2;'>", unsafe_allow_html=True)
            
            # Display total
            st.markdown("---")
            st.markdown(f"### Totalt: {calculate_total():.2f} kr")
            
            # Pay and Clear buttons
            if st.button("💰 BETALA NU", key="pay_btn", use_container_width=True):
                go_to_payment()
                st.rerun()
            
            if st.button("🗑️ Töm Varukorg", key="clear_btn", use_container_width=True):
                clear_cart()
                st.rerun()
        else:
            st.info("Varukorgen är tom")

def menu_page():
    """Display the main cashier interface"""
    st.title("✨ Barnens Biokassa ✨")
    
    # Display cart in sidebar
    display_cart_sidebar()
    
    # Category buttons
    st.header("Kategorier")
    num_categories = len(PRODUCTS)
    category_cols = st.columns(num_categories)

    for i, category in enumerate(PRODUCTS.keys()):
        with category_cols[i]:
            label = f"{CATEGORY_EMOJIS[category]} {category}"
            if st.button(label, key=f"{category}_btn", use_container_width=True):
                set_category(category)
                st.rerun()
    
    # Display items from selected category
    if st.session_state.category:
        st.markdown(f"### {st.session_state.category}")
        
        # Display items in a list
        items = PRODUCTS[st.session_state.category]
        
        for item, price in items.items():
            emoji = ITEM_EMOJIS.get(item, "📦")  # Default emoji if not found
            
            # Create a container for each item for better styling
            item_container = st.container()
            with item_container:
                cols = st.columns([1, 6, 2, 3])
                with cols[0]:
                    st.markdown(f"<div style='font-size:30px; text-align:center;'>{emoji}</div>", unsafe_allow_html=True)
                with cols[1]:
                    st.markdown(f"<div style='padding-top:8px;'>{item}</div>", unsafe_allow_html=True)
                with cols[2]:
                    st.markdown(f"<div style='padding-top:8px;'>{price:.2f} kr</div>", unsafe_allow_html=True)
                with cols[3]:
                    if st.button("Lägg i varukorg", key=f"{item}_btn", use_container_width=True):
                        add_to_cart(item, st.session_state.category)
                        st.rerun()
            
            # Add a separator between items
            st.markdown("<hr style='margin:5px 0; opacity:0.3;'>", unsafe_allow_html=True)
    
    # The pay and clear buttons have been moved to the sidebar with the cart

def payment_page():
    """Display the payment page"""
    st.title("Betalning")
    
    # Show cart in sidebar
    with st.sidebar:
        st.title("Varukorg")
        if st.session_state.cart:
            st.subheader("Varor att Betala")
            for cart_item in st.session_state.cart:
                item, category = cart_item["item"], cart_item["category"]
                emoji = ITEM_EMOJIS.get(item, "📦")
                st.write(f"{emoji} {item}: {PRODUCTS[category][item]:.2f} kr")
            st.markdown("---")
            st.markdown(f"### Totalt: {calculate_total():.2f} kr")
        
        # Payment method selection (just for UI, not functional)
        payment_method = st.selectbox("Välj Betalningsmetod", ["Kontant", "Betalkort"])
        
        # Pay button
        if st.button("💳 Slutför Betalning", use_container_width=True):
            complete_payment()
            st.rerun()
        else:
            st.warning("Din varukorg är tom!")
    
    # Back button
    if st.button("⬅️ Tillbaka till Menyn", use_container_width=True):
        go_to_menu()
        st.rerun()

def success_page():
    """Display success message after payment"""
    st.title("Betalning Slutförd")
    st.success("Betalningen lyckades! Tack för ditt köp.")
    
    # Keep sidebar consistent
    with st.sidebar:
        st.title("Varukorg")
        st.info("Varukorgen är tom")
    
    # Return to menu
    st.markdown("### Vill du handla mer?")
    if st.button("✅ Tillbaka till Menyn", use_container_width=True):
        go_to_menu()
        st.rerun()

def main():
    # Configure Streamlit page
    st.set_page_config(
        page_title="Barnbutikens Kassa",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    
    # Add some custom CSS for a dreamy, fun-looking layout
    st.markdown("""
    <style>
    /* Overall page background and font */
    .main {
        background: linear-gradient(135deg, #f5f7ff 0%, #e3eeff 100%);
        font-family: 'Comic Sans MS', cursive, sans-serif;
    }
    
    /* Colorful header styling */
    h1 {
        color: #6a4c93;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        background: linear-gradient(90deg, #ffafcc, #a2d2ff);
        padding: 10px;
        border-radius: 15px;
        text-align: center;
        font-size: 3em !important;
        margin-bottom: 20px !important;
    }
    
    h2, h3 {
        color: #6a4c93;
    }
    
    /* All category buttons equally tall & wide with fun colors */
    div[data-testid="column"] > div > div > div.stButton > button {
        min-width: 100% !important;
        height: 100px !important;
        font-size: 28px !important;
        font-weight: bold !important;
        display: flex;
        justify-content: center;
        align-items: center;
        border-radius: 20px !important;
        box-shadow: 0 8px 15px rgba(0,0,0,0.1);
        transform: translateY(0);
        transition: all 0.3s ease;
        background: linear-gradient(145deg, #ffc8dd, #cdb4db);
        border: none !important;
    }
    
    div[data-testid="column"] > div > div > div.stButton > button:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.15);
        background: linear-gradient(145deg, #a2d2ff, #bde0fe);
    }
    
    /* Product item styling */
    div.stButton > button {
        border-radius: 15px !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        transition: all 0.2s ease;
    }
    
    div.stButton > button:hover {
        transform: scale(1.02);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #ffc8dd;
        border-radius: 0 20px 20px 0;
        padding: 10px;
    }
    
    [data-testid="stSidebar"] h1 {
        background: linear-gradient(90deg, #ffb3c6, #ff8fab);
        border-radius: 10px;
        padding: 10px;
        font-size: 2em !important;
    }
    
    /* Make separators more playful */
    hr {
        border: 0;
        height: 3px;
        background-image: linear-gradient(to right, transparent, #a2d2ff, transparent);
        margin: 10px 0 !important;
    }
    
    /* Container styling */
    [data-testid="stContainer"] {
        background-color: rgba(255, 255, 255, 0.8);
        border-radius: 15px;
        padding: 10px;
        margin: 10px 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);
    }
    
    /* Optional tweak for main area row spacing */
    [data-testid="column"] > div { margin-bottom: 0px !important; }
    
    /* Fun emoji size */
    [data-testid="column"] div[style*="font-size:30px"] {
        font-size: 40px !important;
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