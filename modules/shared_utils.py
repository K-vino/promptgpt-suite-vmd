# modules/shared_utils.py
# This file contains utility functions that are shared across multiple modules
# within the PromptGPT Suite, ensuring consistency and reusability.

import streamlit as st
import google.generativeai as genai
import logging

logger = logging.getLogger(__name__)

# ====================================================================================================
# SECTION 1: GEMINI API CONFIGURATION AND INITIALIZATION
# This section defines constants and functions for interacting with the Google Gemini API.
# ====================================================================================================

# 1.1 Gemini Model Configuration Constants
DEFAULT_GEMINI_MODEL = "gemini-pro"
AVAILABLE_GEMINI_MODELS = ["gemini-pro"] # Future: "gemini-1.5-pro", etc.

# Default generation parameters for the Gemini model.
# These can be customized or exposed in the UI for advanced users.
GEMINI_GENERATION_CONFIG = {
    "temperature": 0.7,   # Controls randomness (0.0 to 1.0). Higher values = more random.
    "top_p": 0.95,        # Nucleus sampling (0.0 to 1.0). Higher values = more diverse.
    "top_k": 60,          # Top-k sampling. Considers top-k most probable tokens.
    "max_output_tokens": 1500, # Maximum number of tokens in the AI's response.
}

# Safety settings for the Gemini model.
# These prevent the model from generating content that falls into harmful categories.
GEMINI_SAFETY_SETTINGS = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

# 1.2 Caching Mechanism for Gemini Model
# Using Streamlit's @st.cache_resource to cache the initialized model.
# This prevents re-initializing the model on every Streamlit rerun, improving performance.
@st.cache_resource(ttl=3600) # Cache for 1 hour. Adjust as needed.
def initialize_gemini_model(api_key: str, model_name: str = DEFAULT_GEMINI_MODEL):
    """
    Initializes and configures the Google Gemini GenerativeModel.

    This function is cached to prevent redundant API key configuration and model
    instantiation on every Streamlit rerun, enhancing application performance.

    Args:
        api_key (str): The API key for accessing the Gemini API.
        model_name (str): The specific Gemini model to use (e.g., "gemini-pro").

    Returns:
        genai.GenerativeModel: An initialized Gemini GenerativeModel object.
            Returns None if the API key is missing or initialization fails.
    """
    if not api_key:
        logger.warning("Attempted to initialize Gemini model without an API key.")
        return None
    try:
        # Configure the generative AI library with the provided API key.
        genai.configure(api_key=api_key)
        # Instantiate the GenerativeModel with specified configurations.
        model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=GEMINI_GENERATION_CONFIG,
            safety_settings=GEMINI_SAFETY_SETTINGS
        )
        logger.info(f"Gemini model '{model_name}' initialized successfully with API key.")
        return model
    except Exception as e:
        logger.error(f"Error initializing Gemini model '{model_name}': {e}", exc_info=True)
        # It's better to return None here and let the calling function handle the UI error.
        return None

def get_gemini_model(api_key: str):
    """
    Retrieves the initialized Gemini model. If not already initialized or if API key changes,
    it re-initializes and caches it.

    Args:
        api_key (str): The current Gemini API key from session state.

    Returns:
        genai.GenerativeModel: The initialized Gemini model, or None if key is invalid.
    """
    # Use the cached function. Streamlit handles re-running it if `api_key` changes.
    return initialize_gemini_model(api_key, st.session_state.get("selected_gemini_model", DEFAULT_GEMINI_MODEL))

def clear_cached_model():
    """
    Clears the cached Gemini model. Useful when the API key changes or when
    a fresh initialization is needed.
    """
    initialize_gemini_model.clear()
    logger.info("Cached Gemini model cleared.")


# ====================================================================================================
# SECTION 2: COMMON UI COMPONENTS AND MESSAGES
# This section defines reusable UI elements and standard messages for consistency.
# ====================================================================================================

# 2.1 Standard UI Messages
MSG_API_KEY_MISSING = "Please enter your Gemini API Key in the sidebar to enable AI features."
MSG_GENERATION_FAILED = "Failed to generate content. Please try again or check your API key/inputs."
MSG_TASK_MISSING = "Please describe your task or goal in the text area."
MSG_LOADING_AI = "AI Genius at work... crafting your response!"
MSG_GENERATE_BUTTON = "🚀 Generate AI Response"
MSG_COPY_BUTTON = "📋 Copy to Clipboard"
MSG_COPIED_SUCCESS = "Copied to clipboard!"
MSG_COPY_FAILED = "Failed to copy to clipboard. Please copy manually."
MSG_AI_POWERED_NOTICE = "Powered by Google Gemini AI"


# 2.2 Reusable UI Function for Copy to Clipboard
def add_copy_to_clipboard_button(text_to_copy: str, button_label: str = MSG_COPY_BUTTON):
    """
    Adds a button that copies a given text to the clipboard using JavaScript.
    This is a common workaround for Streamlit's lack of a direct clipboard API.

    Args:
        text_to_copy (str): The text content to be copied to the user's clipboard.
        button_label (str): The text label displayed on the copy button.
    """
    # Escape backticks in the text to ensure correct JS string literal.
    escaped_text = text_to_copy.replace('`', '\\`')
    copy_script = f"""
        <script>
            function copyToClipboard(text) {{
                navigator.clipboard.writeText(text).then(function() {{
                    // alert("{MSG_COPIED_SUCCESS}"); // Removed alert as per instructions
                    const copiedSpan = document.getElementById('copied-status');
                    if (copiedSpan) {{
                        copiedSpan.textContent = '{MSG_COPIED_SUCCESS}';
                        setTimeout(() => copiedSpan.textContent = '', 2000);
                    }}
                }}, function(err) {{
                    console.error('Could not copy text: ', err);
                    // alert("{MSG_COPY_FAILED}"); // Removed alert
                    const copiedSpan = document.getElementById('copied-status');
                    if (copiedSpan) {{
                        copiedSpan.textContent = '{MSG_COPY_FAILED}';
                        setTimeout(() => copiedSpan.textContent = '', 2000);
                    }}
                }});
            }}
        </script>
        <button onclick="copyToClipboard(`{escaped_text}`)">
            {button_label}
        </button>
        <span id="copied-status" style="margin-left: 10px; color: green;"></span>
    """
    st.markdown(copy_script, unsafe_allow_html=True)
    logger.debug("Copy to clipboard button added.")

# 2.3 Initial Help Message for Modules
def display_module_help(help_text: str):
    """
    Displays an introductory help message for a module.

    Args:
        help_text (str): The Markdown string containing the help message.
    """
    st.info(help_text)
    logger.debug("Displayed module help message.")

# 2.4 Function to check API key status and display warning
def check_api_key_status(api_key_valid: bool) -> bool:
    """
    Checks the validity of the API key and displays a warning if it's missing.

    Args:
        api_key_valid (bool): True if the API key is present and seemingly valid, False otherwise.

    Returns:
        bool: True if the API key is valid, False otherwise.
    """
    if not api_key_valid:
        st.warning(MSG_API_KEY_MISSING)
        logger.warning("API Key not provided or invalid. AI features disabled.")
        return False
    return True

# 2.5 Reusable function for displaying AI-powered notice
def display_ai_powered_notice():
    """
    Displays a small notice indicating the content is AI-powered.
    """
    st.markdown(f"<p style='font-size:0.8em; color:#777;'>{MSG_AI_POWERED_NOTICE}</p>", unsafe_allow_html=True)
    logger.debug("Displayed AI powered notice.")

logger.info("Shared utilities loaded.")
