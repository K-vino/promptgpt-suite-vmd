# modules/prompt_chat_studio.py
# This module implements the "Prompt Chat Studio" feature, allowing users to
# interact with the Gemini AI in a conversational manner for prompt optimization
# and content generation. It supports chat history and basic prompt chaining.

import streamlit as st
import logging
from modules import shared_utils # Import shared utility functions

logger = logging.getLogger(__name__)

# ====================================================================================================
# SECTION 1: MODULE-SPECIFIC CONSTANTS AND CONFIGURATIONS
# Defines options and default values unique to the Prompt Chat Studio module.
# ====================================================================================================

# 1.1 Initial Chat Instructions
CHAT_STUDIO_HELP_MESSAGE = """
### Welcome to the Prompt Chat Studio!
Engage in a live conversation with Gemini to refine your prompts or generate content.
* **Type your message** in the input box at the bottom.
* **Press Enter** or click 'Send' to get an AI response.
* The conversation history will be displayed above.
* You can restart the chat anytime by clicking 'Clear Chat'.
"""

# 1.2 Chat Model System Instruction
# This initial instruction sets the persona and goal for the Gemini model within the chat.
SYSTEM_INSTRUCTION = """
You are 'PromptGPT Chat Assistant', an expert in crafting and refining AI prompts,
and generating high-quality content. You will respond to user queries, help them
optimize their prompts, generate creative or factual text based on their needs,
and maintain a helpful, concise, and professional tone throughout the conversation.
If a user asks for a prompt, provide a clear and actionable prompt.
If they ask for content, provide the content directly.
"""

# ====================================================================================================
# SECTION 2: CHAT LOGIC AND GEMINI INTERACTION
# Functions responsible for managing chat history and communicating with the Gemini AI.
# ====================================================================================================

def initialize_chat_history():
    """
    Initializes the chat history in Streamlit's session state.
    Each message is a dictionary with 'role' ('user' or 'model') and 'content'.
    """
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
        logger.info("Chat history initialized.")

def get_chat_model(api_key: str):
    """
    Retrieves and initializes the Gemini conversational model.
    Unlike text generation, chat models handle multi-turn conversations.
    """
    model = shared_utils.get_gemini_model(api_key)
    if model:
        # Create a GenerativeModel instance for chat.
        # This allows for the start_chat method.
        # Note: If the model itself is not compatible with start_chat (e.g., a pure text model),
        # this might need adjustment. gemini-pro generally supports it.
        if "chat_session" not in st.session_state:
            try:
                st.session_state.chat_session = model.start_chat(history=[])
                logger.info("New chat session started with Gemini model.")
            except Exception as e:
                logger.error(f"Failed to start chat session with Gemini: {e}", exc_info=True)
                st.error("Could not start chat session. Please check your API key and model compatibility.")
                del st.session_state.chat_session # Clear invalid session
                return None
        return st.session_state.chat_session
    return None

def send_message_to_gemini_chat(chat_session, user_message: str):
    """
    Sends a user message to the Gemini chat session and retrieves the model's response.

    Args:
        chat_session: The active Gemini chat session object.
        user_message (str): The message from the user.

    Returns:
        str: The AI's response text, or an error message if generation fails.
    """
    if not chat_session:
        return shared_utils.MSG_GENERATION_FAILED + " (Chat session not active.)"

    try:
        with st.spinner(shared_utils.MSG_LOADING_AI):
            # Send the message to the generative model and get the response.
            # The chat session manages the history internally.
            response = chat_session.send_message(user_message)
            if response and response.text:
                logger.info("Gemini chat response received.")
                return response.text
            else:
                error_detail = "No text content in chat response."
                if hasattr(response, 'prompt_feedback') and response.prompt_feedback:
                    error_detail += f" Prompt feedback: {response.prompt_feedback}"
                if hasattr(response, 'candidates') and not response.candidates:
                    error_detail += " No candidates generated (potentially blocked by safety settings)."
                logger.error(f"Gemini chat response empty or invalid: {error_detail}")
                return shared_utils.MSG_GENERATION_FAILED + f" (Details: {error_detail})"
    except Exception as e:
        logger.error(f"Error during Gemini chat API call: {e}", exc_info=True)
        return shared_utils.MSG_GENERATION_FAILED + f" (API Error: {e})"

# ====================================================================================================
# SECTION 3: STREAMLIT UI LAYOUT AND INTERACTION
# This section defines the user interface for the Prompt Chat Studio module.
# ====================================================================================================

def run(api_key_valid: bool):
    """
    Main function to run the Prompt Chat Studio module's Streamlit UI.
    This function is called by app.py when the 'Prompt Chat Studio' module is selected.
    """
    st.header("💬 Prompt Chat Studio")
    st.markdown("Interact live with Gemini to refine prompts or generate content.")
    st.markdown("---")

    initialize_chat_history() # Ensure chat history is set up.

    if not shared_utils.check_api_key_status(api_key_valid):
        st.session_state["chat_history"] = [] # Clear history if API key becomes invalid.
        if "chat_session" in st.session_state:
            del st.session_state.chat_session # Clear chat session too.
        return

    # 3.1 Chat Control Buttons
    col_clear, col_export = st.columns([0.8, 0.2])
    with col_clear:
        if st.button("🗑️ Clear Chat History", help="Clears all messages in the current chat session."):
            st.session_state["chat_history"] = []
            if "chat_session" in st.session_state:
                del st.session_state.chat_session # Reset the chat session to start fresh.
            st.experimental_rerun() # Force a rerun to clear the display.
            logger.info("Chat history cleared by user.")
    with col_export:
        # Export Chat History (Conceptual)
        # For a full implementation, this would generate a downloadable file (Markdown, JSON, TXT)
        # This button is mostly for demonstrating a conceptual feature.
        export_chat_clicked = st.button("📤 Export Chat", help="Export the current conversation history.")
        if export_chat_clicked:
            chat_markdown = "## PromptGPT Chat Studio Conversation Log\n\n"
            for message in st.session_state["chat_history"]:
                if message["role"] == "user":
                    chat_markdown += f"**You:** {message['content']}\n\n"
                else: # role == "model"
                    chat_markdown += f"**AI:** {message['content']}\n\n"
            # In a real app, you'd use st.download_button or a more complex export.
            st.download_button(
                label="Download Chat as Markdown",
                data=chat_markdown,
                file_name="prompt_chat_studio_log.md",
                mime="text/markdown",
                key="download_chat_button"
            )
            st.success("Chat history prepared for download.")


    st.markdown("---")

    # 3.2 Display Chat Messages
    chat_container = st.container(height=500, border=True) # Use a container with fixed height for chat scroll
    with chat_container:
        # Display the help message if no chat history yet
        if not st.session_state["chat_history"]:
            shared_utils.display_module_help(CHAT_STUDIO_HELP_MESSAGE)

        # Iterate through the chat history and display messages
        for message in st.session_state["chat_history"]:
            if message["role"] == "user":
                with st.chat_message("user"):
                    st.markdown(message["content"])
            else: # role == "model"
                with st.chat_message("assistant"):
                    st.markdown(message["content"])

    # 3.3 Chat Input Box
    st.markdown("---")
    user_input = st.chat_input(
        "Type your message here...",
        key="chat_input_box",
        on_submit=lambda: _process_chat_input(api_key_valid) # Callback to handle input
    )
    # The on_submit callback handles the main logic.
    shared_utils.display_ai_powered_notice() # Indicate AI generation.


def _process_chat_input(api_key_valid: bool):
    """
    Internal function to process the chat input when the user submits a message.
    This is called by the `on_submit` callback of `st.chat_input`.
    """
    user_message = st.session_state.chat_input_box.strip()
    if user_message:
        logger.info(f"User message received: {user_message[:100]}...") # Log first 100 chars

        # Append user message to history
        st.session_state["chat_history"].append({"role": "user", "content": user_message})

        chat_session = get_chat_model(st.session_state["gemini_api_key"])

        if chat_session:
            ai_response = send_message_to_gemini_chat(chat_session, user_message)

            if ai_response:
                # Append AI response to history
                st.session_state["chat_history"].append({"role": "model", "content": ai_response})
            else:
                # If AI response failed, add an error message to chat history
                st.session_state["chat_history"].append({"role": "model", "content": shared_utils.MSG_GENERATION_FAILED})
        else:
            # If chat session couldn't be initialized, add an error message
            st.session_state["chat_history"].append({"role": "model", "content": shared_utils.MSG_GENERATION_FAILED + " (Could not start chat session.)"})

        # Rerun the app to update the chat display.
        st.experimental_rerun()
    else:
        st.warning("Please type a message before sending.")
        logger.warning("Empty chat input submitted.")

logger.info("Prompt Chat Studio module loaded.")
