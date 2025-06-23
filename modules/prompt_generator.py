# modules/prompt_generator.py
# This module implements the core "Prompt Generator" functionality of the PromptGPT Suite.
# It allows users to define a task, select tone, format, and apply various constraints
# to generate an optimized prompt using the Gemini AI.

import streamlit as st
import logging
from modules import shared_utils # Import shared utility functions

logger = logging.getLogger(__name__)

# ====================================================================================================
# SECTION 1: MODULE-SPECIFIC CONSTANTS AND CONFIGURATIONS
# Defines options and default values unique to the Prompt Generator module.
# ====================================================================================================

# 1.1 Prompt Customization Options
# Tones for the AI's response.
PROMPT_GENERATOR_TONES = [
    "Neutral", "Professional", "Friendly", "Formal", "Informal", "Persuasive",
    "Enthusiastic", "Empathetic", "Direct", "Concise", "Creative", "Humorous",
    "Sarcastic", "Informative", "Technical", "Casual", "Authoritative",
    "Urgent", "Calm", "Motivational", "Reflective", "Narrative", "Poetic",
    "Journalistic", "Academic", "Playful", "Skeptical", "Optimistic", "Pessimistic",
    "Inspiring", "Instructive", "Declarative", "Questioning", "Rhetorical"
]

# Formats for the AI's response.
PROMPT_GENERATOR_FORMATS = [
    "Paragraph", "Bullet Points", "Numbered List", "Short Answer", "Long Essay",
    "Code Snippet", "Poem", "Email", "Blog Post", "News Article", "Summary",
    "Dialogue", "Table", "JSON", "Markdown", "User Story", "Headline", "Review",
    "Script", "Instructions", "Recipe", "Outline", "Description", "Speech",
    "Memo", "Report", "Press Release", "Case Study", "FAQ", "Glossary",
    "Ad Copy", "Social Media Post", "Interview Questions", "Lesson Plan"
]

# Complexity levels for the generated prompt, influencing the AI's response style.
PROMPT_COMPLEXITY_LEVELS = [
    "Beginner (Simple & Direct)",
    "Intermediate (Detailed & Clear)",
    "Advanced (Nuanced & Strategic)",
    "Expert (Highly Specific & Context-Aware)"
]

# 1.2 Initial Help Message for the Prompt Generator Module
PROMPT_GENERATOR_HELP_MESSAGE = """
### Craft Your Perfect Prompt!
Use this module to engineer highly effective prompts for any AI task.
1.  **Define Your Goal:** Clearly state what you want the AI to achieve.
2.  **Customize:** Select the desired tone, format, and set constraints like word count.
3.  **Refine:** Use the 'Rewrite Prompt' feature for AI-powered suggestions.
4.  **Generate:** Click 'Generate Prompt' to get your optimized AI instruction!
"""

# ====================================================================================================
# SECTION 2: AI PROMPT CONSTRUCTION LOGIC
# Functions responsible for assembling the prompt that is sent to the Gemini AI.
# This internal prompt guides the AI to engineer the user's final prompt.
# ====================================================================================================

def construct_internal_gemini_payload_for_prompt_generation(
    user_task: str,
    tone: str,
    output_format: str,
    word_limit: int,
    complexity: str,
    rewrite_instruction: str = None
) -> str:
    """
    Constructs the detailed prompt payload that guides the Gemini AI to generate the user's prompt.
    This is the 'meta-prompt' that instructs the AI on *how* to generate a good prompt.

    Args:
        user_task (str): The user's core task description.
        tone (str): The desired tone for the AI's response.
        output_format (str): The desired format for the AI's response.
        word_limit (int): The word count limit for the AI's final response.
        complexity (str): The desired complexity level of the generated prompt.
        rewrite_instruction (str, optional): Specific instruction for rewriting if applicable.

    Returns:
        str: The complete prompt string to send to Gemini for prompt engineering.
    """
    logger.info("Constructing internal Gemini payload for prompt generation.")
    prompt_parts = [
        "You are an expert AI prompt engineer specialized in creating highly effective, clear, "
        "and comprehensive prompts for large language models (LLMs) like Gemini. "
        "Your goal is to transform a user's raw task into a perfectly optimized LLM prompt. "
        "The generated prompt should leave no ambiguity for the LLM and guide it to produce "
        "the exact desired output, adhering to all specified constraints and nuances. "
        "The final output should be ONLY the engineered prompt itself, without any conversational "
        "introductions or explanations from you (e.g., 'Here's your prompt:')."
    ]

    # Add specifics for the prompt engineering task
    prompt_parts.append(f"\n**User's Core Task/Goal:**\n{user_task}\n")
    prompt_parts.append(f"**Desired Tone for LLM's Response:** `{tone}`\n")
    prompt_parts.append(f"**Desired Output Format for LLM's Response:** `{output_format}`\n")
    prompt_parts.append(f"**Word Count Limit for LLM's Response:** Approximately `{word_limit}` words.\n")
    prompt_parts.append(f"**Complexity Level of the Engineered Prompt:** `{complexity}`\n")

    if rewrite_instruction:
        prompt_parts.append(f"**Specific Rewriting Instruction:** `{rewrite_instruction}`\n")
        prompt_parts.append("Focus solely on rewriting the provided prompt based on this instruction, "
                            "maintaining all other previous parameters (tone, format, word limit, complexity).")
    else:
        prompt_parts.append(
            "\n**Instructions for Generating the Engineered Prompt:**\n"
            "- The prompt should be self-contained and ready to be directly copied and pasted into an LLM.\n"
            "- It must clearly instruct the LLM on its role (if any), the task, the tone, the format, "
            "and any constraints (like word count).\n"
            "- For example, if the tone is 'Creative' and format is 'Poem', the prompt should say "
            "'Write a creative poem...' or similar.\n"
            "- Ensure the engineered prompt is concise yet comprehensive.\n"
            "- Do not include example LLM outputs, only the prompt itself."
        )

    return "\n".join(prompt_parts)

def generate_engineered_prompt_with_gemini(
    api_key_valid: bool,
    user_task: str,
    tone: str,
    output_format: str,
    word_limit: int,
    complexity: str,
    rewrite_instruction: str = None
) -> str:
    """
    Orchestrates the process of generating an engineered prompt using the Gemini AI.

    Args:
        api_key_valid (bool): Flag indicating if the Gemini API key is valid.
        user_task (str): The core task provided by the user.
        tone (str): The selected tone for the AI's response.
        output_format (str): The selected output format.
        word_limit (int): The word limit for the AI's output.
        complexity (str): The complexity level for the prompt.
        rewrite_instruction (str, optional): Specific instruction for rewriting if applicable.

    Returns:
        str: The generated prompt from Gemini, or an error message.
    """
    if not shared_utils.check_api_key_status(api_key_valid):
        return "" # Return empty string, as error message is already displayed.

    if not user_task.strip():
        st.error(shared_utils.MSG_TASK_MISSING)
        logger.warning("Prompt generation aborted: User task is empty.")
        return ""

    model = shared_utils.get_gemini_model(st.session_state["gemini_api_key"])
    if model is None:
        st.error(shared_utils.MSG_GENERATION_FAILED + " (Gemini model not initialized.)")
        logger.error("Prompt generation aborted: Gemini model failed to initialize.")
        return ""

    # Construct the payload for the Gemini API.
    full_gemini_payload = construct_internal_gemini_payload_for_prompt_generation(
        user_task, tone, output_format, word_limit, complexity, rewrite_instruction
    )
    logger.debug(f"Sending payload to Gemini: {full_gemini_payload[:500]}...") # Log first 500 chars

    try:
        with st.spinner(shared_utils.MSG_LOADING_AI):
            response = model.generate_content(full_gemini_payload)
            if response and response.text:
                logger.info("Prompt successfully generated by Gemini.")
                return response.text
            else:
                error_detail = "No text content in response."
                if hasattr(response, 'prompt_feedback') and response.prompt_feedback:
                    error_detail += f" Prompt feedback: {response.prompt_feedback}"
                if hasattr(response, 'candidates') and not response.candidates:
                    error_detail += " No candidates generated (potentially blocked by safety settings)."
                logger.error(f"Gemini response empty or invalid: {error_detail}")
                st.error(shared_utils.MSG_GENERATION_FAILED + f" (Details: {error_detail})")
                return ""
    except Exception as e:
        logger.error(f"Error during Gemini API call for prompt generation: {e}", exc_info=True)
        st.error(shared_utils.MSG_GENERATION_FAILED + f" (API Error: {e})")
        return ""

# ====================================================================================================
# SECTION 3: STREAMLIT UI LAYOUT AND INTERACTION
# This section defines the user interface for the Prompt Generator module.
# ====================================================================================================

def run(api_key_valid: bool):
    """
    Main function to run the Prompt Generator module's Streamlit UI.
    This function is called by app.py when the 'Prompt Generator' module is selected.
    """
    st.header("🎯 Prompt Generator")
    st.markdown("Craft precise and effective prompts for your AI tasks.")
    st.markdown("---")

    # Display initial help message if the user hasn't interacted much.
    if st.session_state.get("generated_prompt", "") == "":
        shared_utils.display_module_help(PROMPT_GENERATOR_HELP_MESSAGE)

    # 3.1 User Task Input
    st.subheader("📝 Define Your Task/Goal")
    user_task = st.text_area(
        "What do you want the AI to do? Be detailed and specific:",
        value=st.session_state.get("pg_user_task", ""), # 'pg_' prefix for Prompt Generator module state
        height=180,
        placeholder="E.g., Write a compelling blog post about the benefits of quantum computing for small businesses.",
        help="Describe the core task, any specific requirements, or background information.",
        key="pg_user_task_input"
    )
    st.session_state["pg_user_task"] = user_task # Persist in session state.

    st.markdown("---")

    # 3.2 Prompt Customization Options
    st.subheader("✨ Customize Your Prompt")
    col1, col2 = st.columns(2)

    with col1:
        # Tone Selection
        selected_tone_index = PROMPT_GENERATOR_TONES.index(st.session_state.get("pg_selected_tone", "Neutral")) \
            if st.session_state.get("pg_selected_tone", "Neutral") in PROMPT_GENERATOR_TONES else 0
        selected_tone = st.selectbox(
            "Desired Tone for AI's Response:",
            options=PROMPT_GENERATOR_TONES,
            index=selected_tone_index,
            key="pg_tone_select",
            help="Influences the emotional quality and style of the AI's output (e.g., 'Formal', 'Creative', 'Humorous')."
        )
        st.session_state["pg_selected_tone"] = selected_tone

    with col2:
        # Format Selection
        selected_format_index = PROMPT_GENERATOR_FORMATS.index(st.session_state.get("pg_selected_format", "Paragraph")) \
            if st.session_state.get("pg_selected_format", "Paragraph") in PROMPT_GENERATOR_FORMATS else 0
        selected_format = st.selectbox(
            "Desired Output Format for AI's Response:",
            options=PROMPT_GENERATOR_FORMATS,
            index=selected_format_index,
            key="pg_format_select",
            help="Defines the structure of the AI's output (e.g., 'Bullet Points', 'Code Snippet', 'JSON')."
        )
        st.session_state["pg_selected_format"] = selected_format

    col3, col4 = st.columns(2)
    with col3:
        # Word Count Limit for AI's Response
        word_limit = st.slider(
            "Approximate Word Count Limit for AI's Response:",
            min_value=50,
            max_value=2000,
            value=st.session_state.get("pg_word_limit", 500),
            step=50,
            key="pg_word_limit_slider",
            help="Set an approximate word count for the AI's final output."
        )
        st.session_state["pg_word_limit"] = word_limit

    with col4:
        # Complexity Level of the Engineered Prompt
        selected_complexity_index = PROMPT_COMPLEXITY_LEVELS.index(st.session_state.get("pg_selected_complexity", "Intermediate (Detailed & Clear)")) \
            if st.session_state.get("pg_selected_complexity", "Intermediate (Detailed & Clear)") in PROMPT_COMPLEXITY_LEVELS else 1
        selected_complexity = st.selectbox(
            "Complexity Level of Engineered Prompt:",
            options=PROMPT_COMPLEXITY_LEVELS,
            index=selected_complexity_index,
            key="pg_complexity_select",
            help="How detailed and sophisticated should the generated prompt itself be? This guides the AI in its prompt engineering."
        )
        st.session_state["pg_selected_complexity"] = selected_complexity

    st.markdown("---")

    # 3.3 Generate and Rewrite Buttons
    col_gen, col_rew, col_clear = st.columns([0.4, 0.4, 0.2])

    with col_gen:
        generate_button_clicked = st.button(
            shared_utils.MSG_GENERATE_BUTTON,
            use_container_width=True,
            key="pg_generate_button",
            help="Click to generate an optimized prompt based on your inputs."
        )

    with col_rew:
        # Dynamic Rewrite Feature
        # This button allows the user to refine an existing generated prompt.
        rewrite_button_clicked = st.button(
            "🔄 Rewrite Prompt",
            use_container_width=True,
            key="pg_rewrite_button",
            help="Use AI to refine the currently generated prompt based on new instructions.",
            disabled=st.session_state.get("pg_generated_prompt", "") == "" or st.session_state.get("pg_generated_prompt", "") == "Your engineered prompt will appear here."
        )

    with col_clear:
        # Clear Button
        clear_button_clicked = st.button(
            "🗑️ Clear",
            use_container_width=True,
            key="pg_clear_button",
            help="Clear all inputs and generated prompt.",
        )

    # Handle the clear button click
    if clear_button_clicked:
        st.session_state["pg_user_task"] = ""
        st.session_state["pg_generated_prompt"] = ""
        st.session_state["pg_selected_tone"] = "Neutral"
        st.session_state["pg_selected_format"] = "Paragraph"
        st.session_state["pg_word_limit"] = 500
        st.session_state["pg_selected_complexity"] = "Intermediate (Detailed & Clear)"
        st.experimental_rerun() # Rerun to clear inputs in the UI.

    # 3.4 Generated Prompt Display Area
    st.subheader("🧠 AI-Engineered Prompt")
    # Initialize generated_prompt in session state if not already present
    if "pg_generated_prompt" not in st.session_state:
        st.session_state["pg_generated_prompt"] = ""

    # Text area to display the generated prompt.
    display_prompt_value = st.session_state["pg_generated_prompt"] if st.session_state["pg_generated_prompt"] else "Your engineered prompt will appear here."

    generated_prompt_output = st.text_area(
        "Copy the optimized prompt below:",
        value=display_prompt_value,
        height=350,
        key="pg_generated_prompt_output",
        disabled=True # Make the text area read-only.
    )

    if st.session_state["pg_generated_prompt"]:
        shared_utils.add_copy_to_clipboard_button(st.session_state["pg_generated_prompt"], shared_utils.MSG_COPY_BUTTON)
        st.info("Click the 'Copy to Clipboard' button above to easily copy the generated prompt.")
        shared_utils.display_ai_powered_notice() # Indicate AI generation.

    # 3.5 Logic for Generate and Rewrite Actions
    if generate_button_clicked:
        logger.info("Generate prompt button clicked.")
        generated_text = generate_engineered_prompt_with_gemini(
            api_key_valid,
            user_task,
            selected_tone,
            selected_format,
            word_limit,
            selected_complexity
        )
        if generated_text:
            st.session_state["pg_generated_prompt"] = generated_text
            st.success("Prompt successfully generated!")
        else:
            st.session_state["pg_generated_prompt"] = "" # Clear on error.
        st.experimental_rerun() # Rerun to update the text area.

    if rewrite_button_clicked:
        if st.session_state["pg_generated_prompt"].strip() and st.session_state["pg_generated_prompt"] != "Your engineered prompt will appear here.":
            logger.info("Rewrite prompt button clicked.")
            # Get specific rewrite instructions from user if available.
            rewrite_instruction = st.text_input(
                "How would you like to rewrite/refine the current prompt?",
                value="",
                placeholder="E.g., 'Make it more concise', 'Add a strict word count', 'Change the tone to sarcastic'.",
                key="pg_rewrite_instruction"
            )

            if rewrite_instruction.strip():
                # Pass the existing generated prompt as the 'user_task' for rewriting logic.
                # The internal payload function handles distinguishing between initial generation and rewrite.
                st.info(f"Rewriting prompt based on: '{rewrite_instruction}'...")
                rewritten_text = generate_engineered_prompt_with_gemini(
                    api_key_valid,
                    st.session_state["pg_generated_prompt"], # The prompt to be rewritten becomes the input
                    selected_tone, # Keep previous settings
                    selected_format, # Keep previous settings
                    word_limit, # Keep previous settings
                    selected_complexity, # Keep previous settings
                    rewrite_instruction # Add the specific rewrite instruction
                )
                if rewritten_text:
                    st.session_state["pg_generated_prompt"] = rewritten_text
                    st.success("Prompt successfully rewritten!")
                else:
                    st.session_state["pg_generated_prompt"] = "" # Clear on error.
                st.experimental_rerun()
            else:
                st.warning("Please provide an instruction for rewriting the prompt.")
        else:
            st.warning("No prompt available to rewrite. Please generate one first.")

    logger.info("Prompt Generator module UI rendered.")
