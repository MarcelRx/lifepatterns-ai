<<<<<<< Updated upstream
# Import required libraries
import streamlit as st
import os
=======
# LifePatterns AI - Main Application
# -----------------------------------
import streamlit as st
>>>>>>> Stashed changes
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure Streamlit page settings
st.set_page_config(
    page_title="LifePatterns AI",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Initialize session state for user authentication
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False  # Authentication status flag
if "user" not in st.session_state:
    st.session_state.user = None  # User object with profile data
if "token" not in st.session_state:
    st.session_state.token = None  # JWT token for API authentication

<<<<<<< Updated upstream
# Create sidebar for system status
st.sidebar.header("System Status")

# Test database connection
try:
    from data.database import test_connection
    db_ok = test_connection()
    st.sidebar.success("Database Connected")
except Exception as e:
    st.sidebar.error(f"Database Error: {e}")

# Add separator in sidebar
st.sidebar.markdown("---")

# Test Groq API connection
try:
    from models.groq_client import test_groq
    groq_ok = test_groq()
    st.sidebar.success("Groq API Connected")
except Exception as e:
    st.sidebar.error(f"Groq Error: {e}")

# Add separator in main content
st.markdown("---")

# Create daily input form section
st.header("Daily Entry")

# Create form for daily entries
with st.form("daily_entry"):
    # Create two columns for form layout
    col1, col2 = st.columns(2)
    
    # Left column inputs
=======

def show_main_app():
    """Display main application interface when user is authenticated"""
    
    # Get current user from session state
    user = st.session_state.user
    
    # SIDEBAR SECTION 
    st.sidebar.title(" LifePatterns AI")
    st.sidebar.caption(f" {user.username}")
    st.sidebar.markdown("---")  # Visual separator
    
    # Navigation menu
    st.sidebar.markdown("### Navigation")
    page = st.sidebar.radio(
        "Select Page",
        ["Home", "Daily Input", "Pattern Discovery", 
         "Outcome Forecast", "Daily Insights", "Reports", "Settings"],
        label_visibility="collapsed"  # Hide label for cleaner UI
    )
    st.sidebar.markdown("---")  # Visual separator
    
    # Quick Statistics section
    st.sidebar.markdown("### Quick Stats")
    try:
        # Import and display user statistics
        from utils.database import get_user_stats
        stats = get_user_stats(user.id)
        
        # Create two-column layout for stats display
        col1, col2 = st.sidebar.columns(2)
        col1.metric("Entries", stats['total_entries'])
        col2.metric("Mood", f"{stats['avg_mood']}/10")
    except:
        # Show informational message if no stats available
        st.sidebar.info("Add entries to see stats!")
    
    # Logout button (imported from auth module)
    from login.auth_page import show_logout_button
    show_logout_button()
    
    # MAIN CONTENT 
    # Route to appropriate page based on navigation selection
    if page == "Home":
        show_home(user)
    elif page == "Daily Input":
        import pages.Daily_Input as p
        p.show_page(user) if hasattr(p, 'show_page') else p.main()
    elif page == "Pattern Discovery":
        import pages.Pattern_Discovery as p
        p.show_page(user)
    elif page == "Outcome Forecast":
        import pages.Outcome_Forecast as p
        p.show_page(user)
    elif page == "Daily Insights":
        import pages.Daily_Insights as p
        p.show_page(user)
    elif page == "Reports":
        import pages.reports_view as p
        p.show_page(user)
    elif page == "Settings":
        show_settings(user)


def show_home(user):
    """Display home dashboard with welcome message and overview"""
    
    st.title("Welcome to LifePatterns AI")
    st.subheader(f"Hello, {user.username}! ")
    
    # Application introduction and features
    st.markdown("""
    ### Start your wellness journey today
    
    LifePatterns AI helps you understand yourself better through intelligent analysis:
    
    -  **Daily Input** - Track mood, energy, sleep, and journal entries
    -  **AI Analysis** - NLP engine analyzes your journal for emotions and insights  
    -  **Pattern Discovery** - Discover hidden patterns in your behavior
    -  **Outcome Forecast** - AI-powered predictions of your wellbeing trajectory
    -  **Daily Insights** - Personalized recommendations based on your data
    -  **Reports** - Visual analytics and trends
    """)
    
    # Display user statistics if available
    try:
        from utils.database import get_user_stats
        stats = get_user_stats(user.id)
        
        st.markdown("### Your Overview")
        
        # Create four-column layout for statistics display
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Entries", stats['total_entries'])
        with col2:
            st.metric("Avg Mood", f"{stats['avg_mood']}/10")
        with col3:
            st.metric("Avg Energy", f"{stats['avg_energy']}/10")
        with col4:
            st.metric("Avg Sleep", f"{stats['avg_sleep']}h")
    except:
        # Show prompt if no statistics available yet
        st.info("Start adding daily entries to see your statistics!")
    
    # Decorative image
    st.image("https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=800", 
             caption="Mindful tracking for better wellbeing")


def show_settings(user):
    """Display user settings page with account management options"""
    
    st.title("Settings")
    
    # Create two-column layout for settings
    col1, col2 = st.columns(2)
    
    # Column 1: Account Information
>>>>>>> Stashed changes
    with col1:
        st.markdown("### Account Info")
        st.write(f"**Username:** {user.username}")
        st.write(f"**Email:** {user.email or 'Not set'}")
        st.write(f"**Member since:** {user.created_at.strftime('%Y-%m-%d')}")
    
<<<<<<< Updated upstream
    # Right column inputs
    with col2:
        sleep = st.number_input("Sleep hours", 0.0, 12.0, 7.0, 0.5)
        activities = st.multiselect(
            "Activities",
            ["Exercise", "Work", "Social", "Reading", "Meditation", "Gaming"]
        )
    
    # Journal text area
    journal = st.text_area(
        "Journal Entry",
        placeholder="How was your day? Write your thoughts here..."
    )
    
    # Submit button
    submitted = st.form_submit_button("Save Entry", use_container_width=True)
    
    # Handle form submission
    if submitted:
        st.success("Entry saved! (Test mode - not actually saving yet)")
        st.balloons()

# Add footer separator
st.markdown("---")
st.caption("LifePatterns AI")
=======
    # Column 2: Password Change Form
    with col2:
        st.markdown("### Change Password")
        with st.form("change_password"):
            old_pass = st.text_input("Current Password", type="password")
            new_pass = st.text_input("New Password", type="password")
            confirm_pass = st.text_input("Confirm New Password", type="password")
            
            # Password change submission
            if st.form_submit_button("Update Password", type="primary"):
                if new_pass != confirm_pass:
                    st.error("New passwords do not match")
                else:
                    # Import authentication manager
                    from login.auth import AuthManager
                    auth = AuthManager()
                    
                    # Attempt password change
                    success, message = auth.change_password(user.id, old_pass, new_pass)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
    
    # Account deletion section (expanded for safety)
    st.markdown("---")
    with st.expander("Delete Account"):
        st.warning("This will permanently delete your account and all data!")
        
        # Password confirmation for deletion
        password = st.text_input("Enter password to confirm deletion", type="password")
        
        # Delete account button with confirmation
        if st.button("Delete My Account", type="primary"):
            from login.auth import AuthManager
            auth = AuthManager()
            
            # Attempt account deletion
            success, message = auth.delete_user(user.id, password)
            if success:
                # Clear session state and redirect to login
                st.session_state.authenticated = False
                st.session_state.user = None
                st.rerun()
            else:
                st.error(message)


# APPLICATION ENTRY POINT 
if __name__ == "__main__":
    # Check authentication status and show appropriate interface
    if st.session_state.authenticated:
        show_main_app()
    else:
        # Show login page if not authenticated
        from login.auth_page import show_login_page
        show_login_page()
>>>>>>> Stashed changes
