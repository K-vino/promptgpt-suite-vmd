# modules/prompt_formatter.py
# This module is a placeholder for the "Prompt Formatter" feature.
# It will allow users to convert their prompts into various structured formats
# like JSON, Markdown, plaintext, API-compatible strings, etc.

import streamlit as st
import logging
import json # For JSON formatting
from modules import shared_utils # Import shared utility functions

logger = logging.getLogger(__name__)

# ====================================================================================================
# SECTION 1: MODULE-SPECIFIC CONSTANTS AND CONFIGURATIONS
# Defines formats and help messages.
# ====================================================================================================

FORMATTER_HELP_MESSAGE = """
### Format Your Prompts for Any Use Case! (Coming Soon!)
This module will help you transform your prompts into the perfect format.
**Envisioned Features:**
* **Convert to JSON:** For API requests or structured data.
* **Convert to Markdown:** For documentation and rich text display.
* **Convert to Plaintext:** Simple, unformatted text.
* **Slack/Discord-friendly:** Optimizes for messaging platforms.
* **API-compatible:** Adds necessary wrappers for direct API calls.
* **Add Variable Tags:** Insert placeholders like `{{topic}}` for templates.
* **Export as PDF:** Generate a downloadable PDF of the formatted prompt.
* **Code Comment Style:** Format prompts for inline code comments.
* **Auto-format for Chatbot Dev:** Specific formats for chatbot frameworks.

Get ready to streamline your prompt integration!
"""

FORMAT_OPTIONS = [
    "Plaintext",
    "Markdown",
    "JSON (basic)",
    "API-compatible (conceptual)",
    "Slack-friendly (conceptual)",
    "Code Comment (conceptual)"
]

# ====================================================================================================
# SECTION 2: CONCEPTUAL FORMATTING LOGIC
# These functions represent how prompts would be transformed.
# ====================================================================================================

def apply_format_transformation(original_prompt: str, target_format: str, **kwargs) -> str:
    """
    (Conceptual) Applies the chosen formatting transformation to the prompt.

    Args:
        original_prompt (str): The prompt string to format.
        target_format (str): The desired output format (e.g., "JSON", "Markdown").
        **kwargs: Additional parameters for specific formats (e.g., variable tags).

    Returns:
        str: The formatted prompt string.
    """
    if not original_prompt.strip():
        return ""

    formatted_output = ""
    logger.info(f"Applying conceptual format '{target_format}' to prompt.")

    if target_format == "Plaintext":
        formatted_output = original_prompt # No change
    elif target_format == "Markdown":
        # Simple Markdown formatting
        formatted_output = f"```\n{original_prompt}\n```"
    elif target_format == "JSON (basic)":
        try:
            # Simple JSON encapsulation, assuming prompt is just a string
            formatted_output = json.dumps({"prompt": original_prompt, "format_applied": "JSON"}, indent=2)
        except Exception as e:
            logger.error(f"Error converting to JSON: {e}")
            formatted_output = f"Error converting to JSON. Prompt:\n{original_prompt}"
    elif target_format == "API-compatible (conceptual)":
        # FIX: Using json.dumps for the prompt content to handle escaping correctly
        formatted_output = (
            "{\n"
            '  "contents": [\n'
            '    {\n'
            '      "role": "user",\n'
            f'      "parts": [ {{ "text": {json.dumps(original_prompt)} }} ]\n' # Corrected line
            '    }\n'
            '  ]\n'
            '}'
        )
    elif target_format == "Slack-friendly (conceptual)":
        formatted_output = f"```\n{original_prompt}\n```\n_Send this to your favorite AI bot!_"
    elif target_format == "Code Comment (conceptual)":
        comment_style = kwargs.get("comment_style", "#")
        lines = original_prompt.split('\n')
        formatted_output = f"{comment_style} --- START AI PROMPT ---\n"
        formatted_output += "\n".join([f"{comment_style} {line}" for line in lines])
        formatted_output += f"\n{comment_style} --- END AI PROMPT ---"
    else:
        formatted_output = f"Unsupported format: {target_format}\nOriginal Prompt:\n{original_prompt}"

    return formatted_output

# ====================================================================================================
# SECTION 3: STREAMLIT UI LAYOUT AND INTERACTION
# This section defines the user interface for the Prompt Formatter module.
# ====================================================================================================

def run(api_key_valid: bool):
    """
    Main function to run the Prompt Formatter module's Streamlit UI.
    This function is called by app.py when the 'Prompt Formatter' module is selected.
    """
    st.header("🔧 Prompt Formatter")
    st.markdown("Transform your prompts into various structured and platform-specific formats.")
    st.markdown("---")

    shared_utils.display_module_help(FORMATTER_HELP_MESSAGE)

    st.warning("This module is under development. The formatting features are conceptual and will be fully implemented in future updates.")
    st.markdown("---")

    # Input for the prompt to be formatted
    st.subheader("📝 Enter Prompt to Format")
    original_prompt = st.text_area(
        "Paste the prompt you want to format:",
        value=st.session_state.get("pf_original_prompt", "Write a blog post about the future of AI. The tone should be optimistic."),
        height=150,
        placeholder="Enter your prompt here...",
        key="pf_original_prompt_input"
    )
    st.session_state["pf_original_prompt"] = original_prompt

    # Select desired format
    st.subheader("🔗 Select Output Format")
    selected_format_index = FORMAT_OPTIONS.index(st.session_state.get("pf_selected_format", "Plaintext")) \
        if st.session_state.get("pf_selected_format", "Plaintext") in FORMAT_OPTIONS else 0
    selected_format = st.selectbox(
        "Choose the format:",
        options=FORMAT_OPTIONS,
        index=selected_format_index,
        key="pf_format_select",
        help="Select the desired output format for your prompt."
    )
    st.session_state["pf_selected_format"] = selected_format

    # Additional options for specific formats (conceptual)
    if selected_format == "Code Comment (conceptual)":
        comment_style = st.selectbox(
            "Choose comment style:",
            options=["#", "//", "<!--", "/*"],
            key="pf_comment_style",
            help="Select the programming language comment style."
        )
        st.session_state["pf_comment_style"] = comment_style
        format_kwargs = {"comment_style": comment_style}
    else:
        format_kwargs = {}

    st.markdown("---")
    col_format, col_clear = st.columns([0.8, 0.2])

    with col_format:
        format_button_clicked = st.button("✨ Apply Formatting", use_container_width=True, key="pf_format_button")
    with col_clear:
        clear_button_clicked = st.button(
            "🗑️ Clear",
            use_container_width=True,
            key="pf_clear_button",
            help="Clear all inputs and formatted output."
        )

    # Handle clear button click
    if clear_button_clicked:
        st.session_state["pf_original_prompt"] = ""
        st.session_state["pf_formatted_output"] = ""
        st.session_state["pf_selected_format"] = "Plaintext"
        st.session_state["pf_comment_style"] = "#" # Reset default for comment style
        st.experimental_rerun()

    # Output display area
    st.subheader("➡️ Formatted Prompt Output")
    if "pf_formatted_output" not in st.session_state:
        st.session_state["pf_formatted_output"] = "The formatted prompt will appear here."

    formatted_output_display = st.text_area(
        "Formatted Prompt:",
        value=st.session_state["pf_formatted_output"],
        height=300,
        key="pf_formatted_output_area",
        disabled=True
    )

    if st.session_state["pf_formatted_output"] and st.session_state["pf_formatted_output"] != "The formatted prompt will appear here.":
        shared_utils.add_copy_to_clipboard_button(st.session_state["pf_formatted_output"], shared_utils.MSG_COPY_BUTTON)
        st.info("The prompt has been formatted. Copy it or select a different format.")
    else:
        st.info("Enter a prompt and select a format to get started.")

    # Logic for formatting
    if format_button_clicked:
        if not original_prompt.strip():
            st.error("Please enter a prompt to format.")
            return

        logger.info(f"Formatting prompt to '{selected_format}'.")
        formatted_text = apply_format_transformation(original_prompt, selected_format, **format_kwargs)
        st.session_state["pf_formatted_output"] = formatted_text
        st.success(f"Prompt successfully formatted to {selected_format}!")
        st.experimental_rerun()

    shared_utils.display_ai_powered_notice()
    logger.info("Prompt Formatter module UI rendered (conceptual).")
