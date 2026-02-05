import streamlit as st

def show_login_page():
    """Display authentication interface for user login and registration"""
    
    # Display page title and subtitle
    st.title("Welcome to LifePatterns AI")
    st.subheader("Personal Behavior & Outcome Analytics")
    
    # Initialize authentication manager
    from login.auth import AuthManager
    auth = AuthManager()
    
    # Create tab interface for login vs registration
    tab1, tab2 = st.tabs(["Sign In", "Create Account"])
    
    # Tab 1: User Login
    with tab1:
        st.markdown("### Sign In to Your Account")
        
        # Create login form
        with st.form("login_form"):
            # Username input field
            username = st.text_input("Username")
            
            # Password input field (hidden with asterisks)
            password = st.text_input("Password", type="password")
            
            # Submit button for login
            submitted = st.form_submit_button("Login", type="primary", use_container_width=True)
            
            # Handle form submission
            if submitted:
                # Validate form inputs
                if not username or not password:
                    st.error("Please enter both username and password")
                else:
                    # Show loading spinner during authentication
                    with st.spinner("Checking credentials..."):
                        # Authenticate user against database
                        success, message, user = auth.authenticate_user(username, password)
                        
                        # Handle successful authentication
                        if success and user:
                            # Update session state with user data
                            st.session_state.authenticated = True
                            st.session_state.user = user
                            st.session_state.token = auth.create_access_token(user.id, user.username)
                            
                            # Display welcome message
                            st.success(f"Welcome back, {user.username}!")
                            st.balloons()
                            
                            # Refresh page to show authenticated content
                            st.rerun()
                        else:
                            # Display authentication error
                            st.error(message)
    
    # Tab 2: User Registration
    with tab2:
        st.markdown("### Create New Account")
        
        # Create registration form
        with st.form("register_form"):
            # Username input with validation hint
            new_username = st.text_input("Choose Username", placeholder="min 3 characters")
            
            # Optional email input
            new_email = st.text_input("Email (optional)")
            
            # Password input with validation requirements
            new_password = st.text_input("Password", type="password", placeholder="min 8 characters")
            
            # Password confirmation input
            confirm_password = st.text_input("Confirm Password", type="password")
            
            # Display password requirements
            st.info("Password must be at least 8 characters")
            
            # Submit button for registration
            submitted = st.form_submit_button("Create Account", type="primary", use_container_width=True)
            
            # Handle form submission
            if submitted:
                errors = []
                
                # Validate username
                if not new_username or len(new_username) < 3:
                    errors.append("Username must be at least 3 characters")
                
                # Validate password length
                if not new_password or len(new_password) < 8:
                    errors.append("Password must be at least 8 characters")
                
                # Validate password match
                if new_password != confirm_password:
                    errors.append("Passwords do not match")
                
                # Display validation errors
                if errors:
                    for error in errors:
                        st.error(error)
                else:
                    # Show loading spinner during registration
                    with st.spinner("Creating your account..."):
                        # Register new user in database
                        success, message, user = auth.register_user(new_username, new_password, new_email if new_email else None)
                        
                        # Handle successful registration
                        if success:
                            st.success(message)
                            st.balloons()
                            st.info("Now switch to Sign In tab to log in!")
                        else:
                            # Display registration error
                            st.error(message)

def show_logout_button():
    """Show logout button and user info in sidebar"""
    
    # Add visual separator in sidebar
    st.sidebar.markdown("---")
    
    # Display current user information
    st.sidebar.markdown(f"Logged in as: **{st.session_state.user.username}**")
    
    # Create logout button
    if st.sidebar.button("Logout", use_container_width=True):
        # Clear authentication session data
        st.session_state.authenticated = False
        st.session_state.user = None
        st.session_state.token = None
        
        # Refresh page to show login interface
        st.rerun()
