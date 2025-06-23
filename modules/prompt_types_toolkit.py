# modules/prompt_types_toolkit.py
# This module implements the "Prompt Types Toolkit" feature of the PromptGPT Suite.
# It allows users to apply various prompt engineering strategies (like Zero-shot, Few-shot,
# Chain-of-thought, Role-play) to a base prompt, enhancing its effectiveness for LLMs.

import streamlit as st
import logging
from modules import shared_utils # Import shared utility functions

logger = logging.getLogger(__name__)

# ====================================================================================================
# SECTION 1: MODULE-SPECIFIC CONSTANTS AND CONFIGURATIONS
# Defines the available prompt types and their associated instructions.
# ====================================================================================================

# 1.1 Prompt Type Definitions
# Each key represents a prompt strategy, and its value is a dictionary
# containing a description and the "prefix" or "instruction" to add to the base prompt.
PROMPT_STRATEGIES = {
    "Zero-shot": {
        "description": "Provides a direct instruction to the AI without any examples. Assumes the AI has sufficient prior knowledge.",
        "instruction": "Based on the following request, provide a direct answer or complete the task:"
    },
    "Few-shot": {
        "description": "Guides the AI with a few examples (input-output pairs) before the final request. Useful for specific formatting or nuanced tasks.",
        "instruction": "I will provide a few examples of input-output pairs. Understand the pattern and apply it to my final request.\n\n"
                      "**Examples:**\n"
                      "Input: [Example Input 1]\nOutput: [Example Output 1]\n\n"
                      "Input: [Example Input 2]\nOutput: [Example Output 2]\n\n"
                      "**Your Turn:**"
    },
    "Chain-of-thought (CoT)": {
        "description": "Instructs the AI to think step-by-step, showing its reasoning process before giving the final answer. Improves accuracy for complex problems.",
        "instruction": "Let's think step by step. First, analyze the problem, then outline your reasoning, and finally provide the solution. Your output should clearly separate the thinking process from the final answer."
    },
    "Role-play": {
        "description": "Asks the AI to adopt a specific persona or role when generating content. Enhances relevance and tone.",
        "instruction": "You are a [ROLE, e.g., seasoned marketing expert / helpful teaching assistant / critical literary critic]. Act in this role when responding to the following request:"
    },
    "Constraint-based": {
        "description": "Applies strict rules or limitations to the AI's output (e.g., word count, specific keywords, forbidden phrases).",
        "instruction": "Your response must strictly adhere to the following constraints:\n"
                      "- [Constraint 1, e.g., Max 100 words]\n"
                      "- [Constraint 2, e.g., Use only formal language]\n"
                      "- [Constraint 3, e.g., Do not mention brand names]\n"
                      "Here is the request:"
    },
    "Persona Embedding": {
        "description": "Guides the AI to adopt a specific identity, background, or style. More detailed than simple role-play.",
        "instruction": "Adopt the persona of a [PERSONA DESCRIPTION, e.g., witty, sarcastic, and highly intelligent AI who enjoys wordplay]. Ensure your responses reflect this persona. Here is your task:"
    },
    "System + User + Assistant Format": {
        "description": "Structures the prompt for multi-turn conversations, defining distinct roles for clarity in complex interactions.",
        "instruction": "You will participate in a multi-turn conversation. Here is the context and your role definition:\n"
                      "**System:** [Overall instructions for the AI for the entire conversation, e.g., You are a customer support agent helping users with technical issues.]\n"
                      "**User:** [The user's initial query or instruction]\n"
                      "**Assistant:** [Your first response should be based on this initial query and system instructions. Future responses will follow.]"
    }
}

# 1.2 Initial Help Message for the module
PROMPT_TYPES_TOOLKIT_HELP_MESSAGE = """
### Boost Your Prompts with Advanced Strategies!
This toolkit helps you enhance your basic prompts by applying powerful prompt engineering techniques.
1.  **Enter Your Base Prompt:** Start with a simple, clear instruction.
2.  **Select a Strategy:** Choose from Zero-shot, Chain-of-thought, Role-play, and more.
3.  **Refine (if needed):** Some strategies like Few-shot or Role-play might require additional input.
4.  **Generate:** See how your prompt is transformed for better AI performance!
"""

# ====================================================================================================
# SECTION 2: PROMPT TRANSFORMATION LOGIC
# Functions responsible for modifying the base prompt based on selected strategies.
# ====================================================================================================

def apply_prompt_strategy(base_prompt: str, strategy_key: str, **kwargs) -> str:
    """
    Applies a selected prompt engineering strategy to a base prompt.

    Args:
        base_prompt (str): The initial prompt provided by the user.
        strategy_key (str): The key identifying the chosen strategy (e.g., "Chain-of-thought").
        **kwargs: Additional arguments specific to certain strategies (e.g., examples for Few-shot, role for Role-play).

    Returns:
        str: The transformed prompt with the strategy applied.
    """
    if strategy_key not in PROMPT_STRATEGIES:
        logger.warning(f"Attempted to apply unknown prompt strategy: {strategy_key}")
        return base_prompt # Return original if strategy is unknown

    instruction_template = PROMPT_STRATEGIES[strategy_key]["instruction"]
    transformed_prompt = ""

    if strategy_key == "Few-shot":
        examples = kwargs.get("examples", [])
        example_string = ""
        for i, ex in enumerate(examples):
            example_string += f"Input {i+1}: {ex.get('input', '')}\nOutput {i+1}: {ex.get('output', '')}\n\n"
        transformed_prompt = instruction_template.replace("**Examples:**", f"**Examples:**\n{example_string.strip()}\n\n**Your Turn:**\n{base_prompt}")
    elif strategy_key == "Role-play":
        role = kwargs.get("role", "general AI assistant")
        transformed_prompt = instruction_template.replace("[ROLE, e.g., seasoned marketing expert / helpful teaching assistant / critical literary critic]", role) + f"\n\n{base_prompt}"
    elif strategy_key == "Constraint-based":
        constraints = kwargs.get("constraints", [])
        constraint_list_str = "\n".join([f"- {c}" for c in constraints]) if constraints else "- [Add your constraints here]"
        transformed_prompt = instruction_template.replace("- [Constraint 1, e.g., Max 100 words]", constraint_list_str) + f"\n\n{base_prompt}"
    elif strategy_key == "Persona Embedding":
        persona_description = kwargs.get("persona_description", "neutral and helpful AI")
        transformed_prompt = instruction_template.replace("[PERSONA DESCRIPTION, e.g., witty, sarcastic, and highly intelligent AI who enjoys wordplay]", persona_description) + f"\n\n{base_prompt}"
    elif strategy_key == "System + User + Assistant Format":
        system_inst = kwargs.get("system_instruction", "You are a helpful AI.")
        transformed_prompt = instruction_template.replace("[Overall instructions for the AI for the entire conversation, e.g., You are a customer support agent helping users with technical issues.]", system_inst)
        transformed_prompt = transformed_prompt.replace("[The user's initial query or instruction]", base_prompt)
        transformed_prompt = transformed_prompt.replace("[Your first response should be based on this initial query and system instructions. Future responses will follow.]", "[Assistant response here...]") # Placeholder
    else: # For strategies like Zero-shot, Chain-of-thought that simply prepend.
        transformed_prompt = f"{instruction_template}\n\n{base_prompt}"

    logger.info(f"Applied strategy '{strategy_key}'. Transformed prompt length: {len(transformed_prompt)}")
    return transformed_prompt

# ====================================================================================================
# SECTION 3: STREAMLIT UI LAYOUT AND INTERACTION
# This section defines the user interface for the Prompt Types Toolkit module.
# ====================================================================================================

def run(api_key_valid: bool):
    """
    Main function to run the Prompt Types Toolkit module's Streamlit UI.
    This function is called by app.py when the 'Prompt Types Toolkit' module is selected.
    """
    st.header("🤖 Prompt Types Toolkit")
    st.markdown("Enhance your prompts with powerful engineering strategies.")
    st.markdown("---")

    # Display initial help message.
    shared_utils.display_module_help(PROMPT_TYPES_TOOLKIT_HELP_MESSAGE)

    # 3.1 Base Prompt Input
    st.subheader("📝 Enter Your Base Prompt")
    base_prompt = st.text_area(
        "Start with your core instruction for the AI:",
        value=st.session_state.get("ptt_base_prompt", ""),
        height=150,
        placeholder="E.g., 'Summarize this article.' or 'Write a short marketing ad for a new coffee machine.'",
        help="This is the fundamental prompt you want to enhance.",
        key="ptt_base_prompt_input"
    )
    st.session_state["ptt_base_prompt"] = base_prompt

    st.markdown("---")

    # 3.2 Strategy Selection
    st.subheader("💡 Select a Prompt Engineering Strategy")
    # Using radio buttons for single selection of a strategy.
    selected_strategy_key = st.radio(
        "Choose how you want to enhance your prompt:",
        options=list(PROMPT_STRATEGIES.keys()),
        index=list(PROMPT_STRATEGIES.keys()).index(st.session_state.get("ptt_selected_strategy", "Zero-shot")),
        key="ptt_strategy_radio",
        help="Each strategy applies a different technique to guide the AI."
    )
    st.session_state["ptt_selected_strategy"] = selected_strategy_key

    st.info(PROMPT_STRATEGIES[selected_strategy_key]["description"])


    # 3.3 Dynamic Inputs Based on Selected Strategy
    strategy_specific_inputs = {}
    if selected_strategy_key == "Few-shot":
        st.subheader("📚 Add Few-shot Examples")
        num_examples = st.number_input(
            "Number of Examples:",
            min_value=1, max_value=5, value=st.session_state.get("ptt_num_examples", 2), step=1,
            key="ptt_num_examples"
        )
        st.session_state["ptt_num_examples"] = num_examples
        examples = []
        for i in range(num_examples):
            st.markdown(f"**Example {i+1}:**")
            input_ex = st.text_area(f"Input {i+1}:", key=f"ptt_fewshot_input_{i}", value=st.session_state.get(f"ptt_fewshot_input_{i}", ""), height=50)
            output_ex = st.text_area(f"Output {i+1}:", key=f"ptt_fewshot_output_{i}", value=st.session_state.get(f"ptt_fewshot_output_{i}", ""), height=50)
            examples.append({"input": input_ex, "output": output_ex})
            st.session_state[f"ptt_fewshot_input_{i}"] = input_ex
            st.session_state[f"ptt_fewshot_output_{i}"] = output_ex
        strategy_specific_inputs["examples"] = examples

    elif selected_strategy_key == "Role-play":
        st.subheader("🎭 Define the Role")
        role_input = st.text_input(
            "AI's Role (e.g., 'seasoned marketing expert', 'friendly teaching assistant'):",
            value=st.session_state.get("ptt_role_input", ""),
            placeholder="e.g., 'a customer support agent'",
            key="ptt_role_input_text"
        )
        st.session_state["ptt_role_input"] = role_input
        strategy_specific_inputs["role"] = role_input

    elif selected_strategy_key == "Constraint-based":
        st.subheader("🚫 Add Constraints")
        # Allow multiple constraints via text area, separated by newlines
        constraints_text = st.text_area(
            "List each constraint on a new line:",
            value=st.session_state.get("ptt_constraints_text", "- Max 200 words\n- Use formal language\n- Avoid jargon"),
            height=100,
            key="ptt_constraints_text_area"
        )
        st.session_state["ptt_constraints_text"] = constraints_text
        strategy_specific_inputs["constraints"] = [c.strip() for c in constraints_text.split('\n') if c.strip()]

    elif selected_strategy_key == "Persona Embedding":
        st.subheader("👤 Define the Persona")
        persona_desc = st.text_area(
            "Describe the AI's persona (e.g., 'a witty and sarcastic AI who enjoys wordplay'):",
            value=st.session_state.get("ptt_persona_desc", ""),
            height=100,
            placeholder="e.g., 'a wise and patient mentor'",
            key="ptt_persona_desc_text"
        )
        st.session_state["ptt_persona_desc"] = persona_desc
        strategy_specific_inputs["persona_description"] = persona_desc

    elif selected_strategy_key == "System + User + Assistant Format":
        st.subheader("💬 Define Conversation Roles")
        system_instruction = st.text_area(
            "System Instruction (Overall guidance for the AI throughout the conversation):",
            value=st.session_state.get("ptt_system_instruction", "You are a helpful and knowledgeable AI assistant."),
            height=100,
            key="ptt_system_instruction_text"
        )
        st.session_state["ptt_system_instruction"] = system_instruction
        strategy_specific_inputs["system_instruction"] = system_instruction


    st.markdown("---")
    col_generate_btn, col_clear_btn = st.columns([0.8, 0.2])
    with col_generate_btn:
        generate_button_clicked = st.button(
            "✨ Generate Transformed Prompt",
            use_container_width=True,
            key="ptt_generate_button",
            help="Click to apply the selected strategy to your base prompt."
        )
    with col_clear_btn:
        clear_button_clicked = st.button(
            "🗑️ Clear",
            use_container_width=True,
            key="ptt_clear_button",
            help="Clear all inputs and generated prompt."
        )

    # Handle the clear button click
    if clear_button_clicked:
        st.session_state["ptt_base_prompt"] = ""
        st.session_state["ptt_generated_prompt"] = ""
        st.session_state["ptt_selected_strategy"] = "Zero-shot"
        # Clear specific inputs for strategies if they are in session_state
        for key_prefix in ["ptt_fewshot_input_", "ptt_fewshot_output_", "ptt_role_input", "ptt_constraints_text", "ptt_persona_desc", "ptt_system_instruction"]:
            for key in list(st.session_state.keys()):
                if key.startswith(key_prefix):
                    del st.session_state[key]
        if "ptt_num_examples" in st.session_state:
            del st.session_state["ptt_num_examples"]
        st.experimental_rerun()


    # 3.4 Transformed Prompt Display
    st.subheader("🚀 Transformed Prompt")
    if "ptt_generated_prompt" not in st.session_state:
        st.session_state["ptt_generated_prompt"] = "Your transformed prompt will appear here."

    transformed_prompt_display = st.text_area(
        "Copy the strategy-enhanced prompt below:",
        value=st.session_state["ptt_generated_prompt"],
        height=350,
        key="ptt_transformed_prompt_output",
        disabled=True
    )

    if st.session_state["ptt_generated_prompt"] and st.session_state["ptt_generated_prompt"] != "Your transformed prompt will appear here.":
        shared_utils.add_copy_to_clipboard_button(st.session_state["ptt_generated_prompt"], shared_utils.MSG_COPY_BUTTON)
        st.info("The prompt above has been modified based on your selected strategy.")
    else:
        st.info("Enter your base prompt and select a strategy to see the transformation.")

    shared_utils.display_ai_powered_notice()


    # 3.5 Logic for Generation
    if generate_button_clicked:
        if not base_prompt.strip():
            st.error("Please enter a base prompt to apply a strategy.")
            logger.warning("Prompt transformation aborted: Base prompt is empty.")
            st.session_state["ptt_generated_prompt"] = "Your transformed prompt will appear here."
            st.experimental_rerun()
            return

        logger.info(f"Applying strategy '{selected_strategy_key}' to base prompt.")
        transformed_text = apply_prompt_strategy(base_prompt, selected_strategy_key, **strategy_specific_inputs)

        st.session_state["ptt_generated_prompt"] = transformed_text
        st.success("Prompt successfully transformed!")
        st.experimental_rerun() # Rerun to update the display area.

    logger.info("Prompt Types Toolkit module UI rendered.")
