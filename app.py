# app.py
# Main entry point for the PromptGPT Suite Streamlit application.
# This file orchestrates the multi-page structure and global configurations.

# ====================================================================================================
# SECTION 1: GLOBAL IMPORTS AND INITIAL CONFIGURATION
# This section handles global imports, environment variable loading, and
# sets up basic logging for the entire application.
# ====================================================================================================

# 1.1 Standard Library Imports
import os
import logging # For robust logging across modules.

# 1.2 Third-Party Library Imports
try:
    import streamlit as st # The primary framework for building the web app.
    from dotenv import load_dotenv # For securely loading environment variables from .env.
except ImportError as e:
    # Error handling for missing core libraries.
    logging.error(f"Critical import error: {e}. Please ensure 'streamlit' and 'python-dotenv' are installed.")
    st.error("A critical library is missing. Please install it using pip. Error: " + str(e))
    st.stop() # Halt execution if core dependencies are not met.

# Load environment variables from .env file at the very start.
load_dotenv()

# Configure basic logging. This helps in debugging issues across different modules.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ====================================================================================================
# SECTION 2: APPLICATION CONSTANTS AND GLOBAL SETTINGS
# Defines global metadata, shared constants, and session state initialization.
# ====================================================================================================

# 2.1 Application Metadata for Streamlit Page Configuration
APP_TITLE = "PromptGPT Suite 🚀 – AI Prompt Engineering Tools"
APP_ICON = "✨" # Emoji for browser tab icon.
APP_DESCRIPTION = """
**Welcome to PromptGPT Suite!** Your comprehensive platform for engineering, managing,
and optimizing AI prompts across various use cases. Navigate through our powerful modules
using the sidebar.
"""
GITHUB_REPO_URL = "https://github.com/your-username/prompt-gpt-suite" # IMPORTANT: Update with your actual GitHub repo URL.

# 2.2 Global Session State Initialization
# Initialize session state variables that might be used across multiple modules.
# This ensures a consistent state management pattern.
if "api_key_entered" not in st.session_state:
    st.session_state["api_key_entered"] = False
if "gemini_api_key" not in st.session_state:
    st.session_state["gemini_api_key"] = os.getenv("GEMINI_API_KEY", "")

# Placeholder for currently selected module/page.
if "current_module" not in st.session_state:
    st.session_state["current_module"] = "Prompt Generator" # Default landing page.

# 2.3 Color Palette and Theming Constants
# Define a cohesive color palette for a professional and presentable look.
COLOR_PRIMARY = "#6B48FF"  # A deeper, more sophisticated purple-blue
COLOR_ACCENT = "#00D2FF"   # A bright, striking light blue
COLOR_BACKGROUND = "#F0F2F5" # Very light grey-blue for main background
COLOR_SURFACE = "#FFFFFF"  # Pure white for cards and components
COLOR_TEXT_DARK = "#2C3E50" # Dark blue-gray for main text
COLOR_TEXT_LIGHT = "#7F8C8D" # Muted grey for secondary text
COLOR_BORDER = "#E0E6ED"   # Soft, light border color
COLOR_CODE_BG = "#282C34"  # Dark background for code blocks
COLOR_CODE_TEXT = "#ABB2BF" # Light text for code blocks
COLOR_ERROR_TEXT = "#E74C3C" # Red for error messages

# ====================================================================================================
# SECTION 3: MODULE IMPORTS AND REGISTRATION
# Dynamically imports each module (which represents a page/feature set).
# This design pattern allows for easy expansion of the suite.
# ====================================================================================================

# Import individual modules from the 'modules' directory.
# Each module is expected to have a 'run()' function that encapsulates its Streamlit UI and logic.
try:
    from modules import (
        shared_utils,
        prompt_generator,
        prompt_chat_studio,
        prompt_library,
        prompt_types_toolkit,
        prompt_evaluator,
        prompt_formatter,
        prompt_builder,
        multilingual_assistant,
        secure_vault,
        analytics_reports
    )
except ImportError as e:
    logger.critical(f"Failed to import a module: {e}. Ensure all module files exist and are correctly named.")
    st.error(f"Failed to load application modules. Please check the 'modules/' directory. Error: " + str(e))
    st.stop()

# Dictionary to map module names to their respective run functions.
# This makes it easy to dispatch to the correct module based on sidebar selection.
MODULES = {
    "Prompt Generator": prompt_generator,
    "Prompt Chat Studio": prompt_chat_studio,
    "Prompt Library": prompt_library,
    "Prompt Types Toolkit": prompt_types_toolkit,
    "AI Prompt Evaluator": prompt_evaluator,
    "Prompt Formatter": prompt_formatter,
    "Prompt Builder (No-Code)": prompt_builder,
    "Multilingual Prompt Assistant": multilingual_assistant,
    "Secure Prompt Vault": secure_vault,
    "Analytics & Reports": analytics_reports,
}

# ====================================================================================================
# SECTION 4: STREAMLIT PAGE CONFIGURATION AND GLOBAL UI ELEMENTS
# Sets up the overall layout, title, and persistent UI components like the sidebar API key input.
# ====================================================================================================

# Set Streamlit page configuration. This must be the first Streamlit command in the script.
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide", # Use a wide layout to maximize content space.
    initial_sidebar_state="expanded" # Keep the sidebar expanded by default.
)

# 4.1 Global Sidebar for API Key Input and Navigation
with st.sidebar:
    st.title("⚙️ Global Settings")
    st.markdown("---")

    # API Key Input
    # Users input their Gemini API key here. It's stored in session state.
    # The input type is 'password' for security.
    current_api_key_input = st.text_input(
        "Gemini API Key",
        type="password",
        value=st.session_state["gemini_api_key"], # Pre-fill from session state or .env
        placeholder="Enter your Gemini API Key (e.g., AIza...)",
        help="Get your API key from [Google AI Studio](https://aistudio.google.com/app/apikey). "
             "You can also set it as an environment variable `GEMINI_API_KEY` or in a `.env` file."
    )

    # Update session state if the API key input changes.
    if current_api_key_input != st.session_state["gemini_api_key"]:
        st.session_state["gemini_api_key"] = current_api_key_input
        # When API key changes, force a re-evaluation of model initialization status.
        shared_utils.clear_cached_model() # Clear cached model if key changes.
        st.session_state["api_key_entered"] = bool(current_api_key_input.strip())
        logger.info("Gemini API Key updated in session state.")


    # Display API key status
    if st.session_state["gemini_api_key"].strip():
        st.success("API Key Loaded!")
        st.session_state["api_key_entered"] = True
    else:
        st.warning("Please enter your Gemini API Key to unlock all features.")
        st.session_state["api_key_entered"] = False

    st.markdown("---")
    st.subheader("🌐 Navigation")

    # Module selection using radio buttons in the sidebar.
    # This acts as the primary navigation for the multi-page application.
    selected_module = st.radio(
        "Go to Module:",
        list(MODULES.keys()),
        index=list(MODULES.keys()).index(st.session_state["current_module"]),
        key="main_module_navigation",
        help="Select a module from the PromptGPT Suite."
    )

    # Update current_module in session state if navigation changes.
    if selected_module != st.session_state["current_module"]:
        st.session_state["current_module"] = selected_module
        st.experimental_rerun() # Rerun to switch to the selected module's content.

    st.markdown("---")
    st.markdown(
        f"""
        <div class="sidebar-footer">
            <p>Built with ❤️ and Streamlit</p>
            <a href="{GITHUB_REPO_URL}" target="_blank">GitHub Repository</a>
        </div>
        """,
        unsafe_allow_html=True
    )


# ====================================================================================================
# SECTION 5: MAIN CONTENT DISPATCHER
# This section dynamically loads and runs the selected module's Streamlit UI and logic.
# ====================================================================================================

st.title(APP_TITLE)
st.markdown(APP_DESCRIPTION)
st.markdown("---")

# Retrieve the module object based on the selected module name.
current_module_obj = MODULES[st.session_state["current_module"]]

# Check if the module has a 'run' function and execute it.
if hasattr(current_module_obj, "run") and callable(current_module_obj.run):
    try:
        # Pass the global API key status to the module.
        current_module_obj.run(api_key_valid=st.session_state["api_key_entered"])
    except Exception as e:
        logger.error(f"Error running module '{st.session_state['current_module']}': {e}", exc_info=True)
        st.error(f"An error occurred in the **{st.session_state['current_module']}** module. Please try again later. (Error: {e})")
else:
    st.error(f"Module '{st.session_state['current_module']}' is not correctly configured (missing 'run' function).")
    logger.error(f"Module '{st.session_state['current_module']}' missing 'run' function.")

# ====================================================================================================
# SECTION 6: GLOBAL STYLING
# Apply custom CSS to enhance the overall look and feel of the Streamlit application.
# This CSS applies globally to all pages/modules.
# ====================================================================================================

st.markdown(
    f"""
    <style>
    /* Import Google Font - Inter for a clean, modern look */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [data-testid="stAppViewContainer"] {{
        font-family: 'Inter', sans-serif;
        color: {COLOR_TEXT_DARK};
        background-color: {COLOR_BACKGROUND};
    }}

    /* Hide Streamlit's default footer and header (including 'Deploy' button) */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    .stDeployButton {{ display: none !important; }}

    /* Adjust main content block padding for wider look */
    .css-1d391kg {{ /* Targetting the main block container */
        padding-top: 3rem;
        padding-right: 3rem;
        padding-left: 3rem;
        padding-bottom: 3rem;
        background-color: {COLOR_BACKGROUND};
    }}

    /* Header styling */
    h1 {{
        color: {COLOR_PRIMARY}; /* Primary blue for main title */
        font-weight: 700;
        border-bottom: 2px solid {COLOR_ACCENT}; /* Accent line under title */
        padding-bottom: 15px;
        margin-bottom: 30px;
        letter-spacing: -0.5px;
        font-size: 2.5em; /* Larger title */
    }}
    h2 {{
        color: {COLOR_TEXT_DARK};
        font-weight: 600;
        margin-top: 40px;
        margin-bottom: 20px;
        font-size: 1.8em;
        border-bottom: 1px solid {COLOR_BORDER}; /* Subtle border under subheaders */
        padding-bottom: 8px;
    }}
    h3, h4 {{
        color: {COLOR_TEXT_DARK};
        font-weight: 600;
        margin-top: 30px;
        margin-bottom: 15px;
        font-size: 1.4em;
    }}

    /* Buttons styling */
    button {{
        background-color: {COLOR_PRIMARY};
        color: white;
        padding: 12px 25px; /* Slightly larger padding */
        border: none;
        border-radius: 10px; /* More rounded corners */
        cursor: pointer;
        font-size: 17px; /* Slightly larger font */
        font-weight: bold;
        transition: all 0.3s ease; /* Smooth transition for all properties */
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15); /* Stronger, more prominent shadow */
        letter-spacing: 0.5px;
    }}
    button:hover {{
        background-color: #5A3CCF; /* Darker primary on hover */
        transform: translateY(-3px); /* More pronounced lift effect */
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
    }}
    button:active {{
        transform: translateY(0);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }}

    /* Specific style for secondary buttons, e.g., clear, rewrite */
    .stButton > button:nth-last-child(1), .stButton > button:nth-last-child(2) {{ /* Target last two buttons, common for clear/rewrite */
        background-color: {COLOR_TEXT_LIGHT};
        box-shadow: 0 3px 6px rgba(0, 0, 0, 0.1); /* Lighter shadow for secondary */
    }}
    .stButton > button:nth-last-child(1):hover, .stButton > button:nth-last-child(2):hover {{
        background-color: #6a7c7e;
        transform: translateY(-2px);
        box-shadow: 0 5px 10px rgba(0, 0, 0, 0.15);
    }}


    /* Text areas and inputs */
    textarea, input[type="text"], input[type="password"] {{
        border-radius: 10px; /* More rounded */
        border: 1px solid {COLOR_BORDER};
        padding: 15px; /* More padding */
        box-shadow: inset 0 2px 5px rgba(0, 0, 0, 0.05); /* Deeper inset shadow */
        font-family: 'Inter', sans-serif;
        font-size: 16px;
        background-color: {COLOR_SURFACE};
        color: {COLOR_TEXT_DARK};
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }}
    textarea:focus, input[type="text"]:focus, input[type="password"]:focus {{
        border-color: {COLOR_ACCENT}; /* Highlight on focus */
        box-shadow: inset 0 2px 5px rgba(0, 0, 0, 0.1), 0 0 0 3px {COLOR_ACCENT}30; /* Glow effect */
        outline: none;
    }}

    /* Selectbox styling */
    div[data-testid="stSelectbox"] > div {{
        border-radius: 10px;
        border: 1px solid {COLOR_BORDER};
        box-shadow: inset 0 2px 5px rgba(0, 0, 0, 0.05);
        background-color: {COLOR_SURFACE};
        color: {COLOR_TEXT_DARK};
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }}
    div[data-testid="stSelectbox"] > div:hover {{
        border-color: {COLOR_ACCENT};
    }}
    div[data-testid="stSelectbox"] div[data-baseweb="select"] {{
        background-color: {COLOR_SURFACE};
    }}
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div:first-child {{
        padding: 15px; /* Align padding with text inputs */
    }}


    /* Expander styling */
    .streamlit-expanderHeader {{
        background-color: {COLOR_SURFACE}; /* White background for expander headers */
        border-radius: 10px; /* More rounded */
        padding: 15px 20px; /* More padding */
        margin-bottom: 8px; /* More space */
        font-weight: 600;
        color: {COLOR_TEXT_DARK};
        border: 1px solid {COLOR_BORDER}; /* Border for a card-like look */
        box-shadow: 0 4px 8px rgba(0,0,0,0.08); /* Subtle shadow */
        transition: all 0.2s ease;
    }}
    .streamlit-expanderHeader:hover {{
        box-shadow: 0 6px 12px rgba(0,0,0,0.12); /* Slightly raised effect on hover */
        transform: translateY(-2px);
    }}
    .streamlit-expanderContent {{
        padding: 20px; /* More padding */
        border-left: 4px solid {COLOR_PRIMARY}; /* Primary color border */
        background-color: {COLOR_SURFACE};
        border-radius: 0 0 10px 10px; /* Match top radius */
        margin-bottom: 25px; /* More space below */
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }}

    /* Info/Success/Warning/Error messages */
    .stAlert {{
        border-radius: 10px; /* More rounded */
        font-size: 0.98em;
        padding: 18px; /* More padding */
        margin-bottom: 20px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }}
    .stAlert.info {{ background-color: #e6f7ff; border-left-color: #91d5ff; color: #08979c; }}
    .stAlert.success {{ background-color: #f6ffed; border-left-color: #b7eb8f; color: #52c41a; }}
    .stAlert.warning {{ background-color: #fffbe6; border-left-color: #ffe58f; color: #faad14; }}
    .stAlert.error {{ background-color: #fff1f0; border-left-color: #ffa39e; color: {COLOR_ERROR_TEXT}; }}


    /* Sidebar styling */
    [data-testid="stSidebar"] {{
        background-color: {COLOR_SURFACE}; /* White background for sidebar */
        box-shadow: 3px 0 15px rgba(0,0,0,0.08); /* Stronger shadow for sidebar */
    }}
    [data-testid="stSidebar"] .stRadio > label {{
        padding: 12px 20px; /* More padding */
        margin-bottom: 8px; /* More space */
        border-radius: 8px;
        transition: background-color 0.2s, transform 0.1s;
        color: {COLOR_TEXT_DARK};
        font-size: 1.05em;
    }}
    [data-testid="stSidebar"] .stRadio > label:hover {{
        background-color: {COLOR_BACKGROUND};
        transform: translateX(3px); /* Slight slide on hover */
    }}
    /* Specific styling for selected radio button */
    [data-testid="stSidebar"] .stRadio [aria-checked="true"] > div:first-child {{
        background-color: {COLOR_PRIMARY} !important;
        border-color: {COLOR_PRIMARY} !important;
    }}
    [data-testid="stSidebar"] .stRadio [aria-checked="true"] > div:first-child + div {{
        color: {COLOR_PRIMARY} !important;
        font-weight: 700; /* Bolder text for selected */
    }}

    /* Footer text in sidebar */
    .sidebar-footer {{
        font-size: 0.85em;
        color: {COLOR_TEXT_LIGHT};
        text-align: center;
        margin-top: 40px;
        padding-top: 20px;
        border-top: 1px solid {COLOR_BORDER};
    }}
    .sidebar-footer a {{
        color: {COLOR_PRIMARY};
        text-decoration: none;
        font-weight: 500;
    }}
    .sidebar-footer a:hover {{
        text-decoration: underline;
    }}

    /* Adjust Streamlit's default markdown styling for better readability */
    p {{
        line-height: 1.7;
        margin-bottom: 12px;
        color: {COLOR_TEXT_DARK};
    }}
    ul, ol {{
        margin-left: 25px; /* More indentation */
        margin-bottom: 12px;
        color: {COLOR_TEXT_DARK};
    }}
    code {{
        background-color: #E6EBF0; /* Lighter background for inline code */
        padding: 3px 6px;
        border-radius: 5px;
        font-family: 'Fira Code', 'Cascadia Code', 'Consolas', monospace;
        font-size: 0.95em;
        color: {COLOR_PRIMARY}; /* Primary color for inline code */
    }}
    pre code {{
        display: block;
        padding: 1.2em;
        overflow-x: auto;
        background-color: {COLOR_CODE_BG}; /* Dark background for code blocks */
        color: {COLOR_CODE_TEXT};
        border-radius: 10px; /* More rounded */
        box-shadow: inset 0 2px 5px rgba(0, 0, 0, 0.2); /* Inset shadow for code blocks */
    }}

    /* Responsive adjustments */
    @media (max-width: 768px) {{
        .css-1d391kg {{ /* Main block container padding */
            padding: 1rem;
        }}
        .streamlit-expanderHeader {{
            padding: 12px;
        }}
        button {{
            padding: 10px 18px;
            font-size: 15px;
        }}
        h1 {{ font-size: 2em; }}
        h2 {{ font-size: 1.5em; }}
    }}

    /* Styling for st.chat_message */
    .stChatMessage {{
        background-color: {COLOR_SURFACE};
        border-radius: 15px; /* More rounded chat bubbles */
        padding: 18px; /* More padding */
        margin-bottom: 15px; /* More space between messages */
        box-shadow: 0 2px 8px rgba(0,0,0,0.1); /* Softer, slightly larger shadow */
        line-height: 1.6;
        font-size: 1.05em;
    }}
    .stChatMessage.user {{
        background-color: {COLOR_PRIMARY}10; /* Very light tint of primary for user */
        border-left: 5px solid {COLOR_PRIMARY}; /* Stronger primary border */
        text-align: right;
        margin-left: 15%; /* Indent user messages from left */
    }}
    .stChatMessage.assistant {{
        background-color: {COLOR_BACKGROUND}; /* Use background color for assistant messages */
        border-left: 5px solid {COLOR_ACCENT}; /* Accent border for assistant */
        text-align: left;
        margin-right: 15%; /* Indent assistant messages from right */
    }}
    .stChatMessage .stMarkdown {{
        padding: 0;
    }}
    .stChatMessage.user .stMarkdown p {{
        color: {COLOR_TEXT_DARK}; /* Ensure text color is readable */
    }}
    .stChatMessage.assistant .stMarkdown p {{
        color: {COLOR_TEXT_DARK}; /* Ensure text color is readable */
    }}


    </style>
    """,
    unsafe_allow_html=True
)

logger.info("PromptGPT Suite 'app.py' loaded successfully.")
