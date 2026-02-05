# Test Groq API connection
# --------------------------
import os
from groq import Groq
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def test_groq():
    """Test Groq API connectivity and response"""
    
    # Retrieve API key from environment variables
    api_key = os.getenv("GROQ_API_KEY")
    
    # Check if API key exists
    if not api_key:
        print("GROQ_API_KEY not found in .env file")
        return False
    
    # Display partial API key for verification (masked for security)
    print(f"API Key found: {api_key[:10]}...")
    
    # Attempt to connect to Groq API
    try:
        # Initialize Groq client with API key
        client = Groq(api_key=api_key)
        
        # Send test request to Groq API
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "user", "content": "Say hello in 3 words"}
            ],
            max_tokens=50
        )
        
        # Extract and display response
        result = response.choices[0].message.content
        print(f"Groq connected!")
        print(f"Response: '{result}'")
        return True
        
    # Handle API connection or response errors
    except Exception as e:
        print(f"Groq error: {e}")
        return False

# Execute test function when script runs directly
if __name__ == "__main__":
    test_groq()