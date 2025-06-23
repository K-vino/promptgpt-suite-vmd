# modules/prompt_builder.py
# This module is a placeholder for the "Prompt Builder (No-Code UI)" feature.
# It envisions a drag-and-drop interface for visually constructing prompts.

import streamlit as st
import logging
from modules import shared_utils # Import shared utility functions

logger = logging.getLogger(__name__)

# ====================================================================================================
# SECTION 1: MODULE-SPECIFIC CONSTANTS AND CONFIGURATIONS
# Defines conceptual builder elements and help messages.
# ====================================================================================================

BUILDER_HELP_MESSAGE = """
### Build Prompts Visually! (Coming Soon!)
This module will offer a no-code, drag-and-drop interface to build complex prompts.
**Envisioned Features:**
* **Drag-and-drop blocks:** Combine pre-defined prompt components.
* **Input → Output visual flow:** Map out the AI's processing steps.
* **Auto-preview mode:** See the generated prompt in real-time.
* **Variable placeholders:** Easily insert dynamic content (`{{variable}}`).
* **Save as reusable templates:** Store your visual designs.
* **Generate prompt + UI schema:** For programmatic integration.
* **Visual JSON prompt designer:** Build structured prompts.
* **Share builder via link:** Collaborate on prompt design.
* **Build complex Gemini chat templates:** Design multi-turn conversations.

Get ready for intuitive prompt creation!
"""

# Conceptual building blocks for a drag-and-drop interface.
# In a full implementation, these would represent UI components that assemble into a prompt string.
CONCEPTUAL_BUILDING_BLOCKS = [
    "Task Definition", "Tone Selector", "Format Selector", "Constraint Block",
    "Example Input (Few-shot)", "Example Output (Few-shot)", "Role Definition",
    "Persona Description", "Chain-of-Thought Trigger", "Output Length",
    "Context Information", "Audience Definition"
]

# ====================================================================================================
# SECTION 2: CONCEPTUAL BUILDER LOGIC
# These functions represent the backend logic for assembling and rendering prompts
# from a visual builder.
# ====================================================================================================

def conceptual_assemble_prompt_from_blocks(selected_blocks: list, block_data: dict) -> str:
    """
    (Conceptual) Assembles a prompt string from a list of selected building blocks and their data.
    This function simulates the logic of a no-code prompt builder.

    Args:
        selected_blocks (list): A list of block names (e.g., ["Task Definition", "Tone Selector"]).
        block_data (dict): A dictionary containing data associated with each block.

    Returns:
        str: The assembled prompt string.
    """
    assembled_prompt_parts = []
    logger.info(f"Conceptually assembling prompt from {len(selected_blocks)} blocks.")

    # Simulate logic for each block
    for block_name in selected_blocks:
        if block_name == "Task Definition" and "task" in block_data:
            assembled_prompt_parts.append(f"Task: {block_data['task']}")
        elif block_name == "Tone Selector" and "tone" in block_data:
            assembled_prompt_parts.append(f"Tone: {block_data['tone']}")
        elif block_name == "Format Selector" and "format" in block_data:
            assembled_prompt_parts.append(f"Format: {block_data['format']}")
        elif block_name == "Constraint Block" and "constraints" in block_data:
            constraints_str = ", ".join(block_data["constraints"])
            assembled_prompt_parts.append(f"Constraints: {constraints_str}")
        elif block_name == "Role Definition" and "role" in block_data:
            assembled_prompt_parts.append(f"Assume the role of: {block_data['role']}")
        elif block_name == "Chain-of-Thought Trigger":
            assembled_prompt_parts.append("Think step-by-step to arrive at the answer.")
        # Add more block logic here for other conceptual blocks

    if not assembled_prompt_parts:
        return "No blocks selected or insufficient data to assemble a prompt."

    return "\n\n".join(assembled_prompt_parts)

# ====================================================================================================
# SECTION 3: STREAMLIT UI LAYOUT AND INTERACTION
# This section defines the user interface for the Prompt Builder module.
# ====================================================================================================

def run(api_key_valid: bool):
    """
    Main function to run the Prompt Builder module's Streamlit UI.
    This function is called by app.py when the 'Prompt Builder (No-Code)' module is selected.
    """
    st.header("🏗️ Prompt Builder (No-Code)")
    st.markdown("Visually design and construct complex prompts using a drag-and-drop interface.")
    st.markdown("---")

    shared_utils.display_module_help(BUILDER_HELP_MESSAGE)

    st.warning("This module is under heavy development. The features described are conceptual and will be implemented in future updates. Below is a simplified simulation of the builder.")
    st.markdown("---")

    st.subheader("💡 Conceptual Building Blocks")
    st.markdown("Select blocks and enter details to 'build' your prompt.")

    # Use multiselect to simulate "dragging" blocks onto a canvas
    selected_conceptual_blocks = st.multiselect(
        "Choose your prompt building blocks:",
        options=CONCEPTUAL_BUILDING_BLOCKS,
        default=st.session_state.get("pb_selected_blocks", []),
        key="pb_block_selector",
        help="Select components you want to include in your prompt."
    )
    st.session_state["pb_selected_blocks"] = selected_conceptual_blocks

    block_data = {}
    st.subheader("➡️ Configure Block Details")

    # Dynamic input fields for selected blocks
    if "Task Definition" in selected_conceptual_blocks:
        block_data["task"] = st.text_input("Task Description:", value=st.session_state.get("pb_task_input", ""), key="pb_task_def_input")
        st.session_state["pb_task_input"] = block_data["task"]
    if "Tone Selector" in selected_conceptual_blocks:
        block_data["tone"] = st.selectbox("Tone:", options=["Formal", "Informal", "Creative"], key="pb_tone_select", index=st.session_state.get("pb_tone_idx", 0))
        st.session_state["pb_tone_idx"] = ["Formal", "Informal", "Creative"].index(block_data["tone"])
    if "Format Selector" in selected_conceptual_blocks:
        block_data["format"] = st.selectbox("Format:", options=["Paragraph", "Bullet Points", "JSON"], key="pb_format_select", index=st.session_state.get("pb_format_idx", 0))
        st.session_state["pb_format_idx"] = ["Paragraph", "Bullet Points", "JSON"].index(block_data["format"])
    if "Constraint Block" in selected_conceptual_blocks:
        constraints_str = st.text_area("Constraints (one per line):", value=st.session_state.get("pb_constraints_input", ""), key="pb_constraints_input_area")
        block_data["constraints"] = [c.strip() for c in constraints_str.split('\n') if c.strip()]
        st.session_state["pb_constraints_input"] = constraints_str
    if "Role Definition" in selected_conceptual_blocks:
        block_data["role"] = st.text_input("Role for AI:", value=st.session_state.get("pb_role_input", ""), key="pb_role_input_text")
        st.session_state["pb_role_input"] = block_data["role"]

    st.markdown("---")
    col_build, col_clear = st.columns([0.8, 0.2])

    with col_build:
        build_button_clicked = st.button("🏗️ Build Prompt", use_container_width=True, key="pb_build_button")
    with col_clear:
        clear_button_clicked = st.button(
            "🗑️ Clear",
            use_container_width=True,
            key="pb_clear_button",
            help="Clear all selections and generated prompt."
        )

    # Handle clear button click
    if clear_button_clicked:
        st.session_state["pb_selected_blocks"] = []
        st.session_state["pb_task_input"] = ""
        st.session_state["pb_tone_idx"] = 0
        st.session_state["pb_format_idx"] = 0
        st.session_state["pb_constraints_input"] = ""
        st.session_state["pb_role_input"] = ""
        st.session_state["pb_assembled_prompt"] = ""
        st.experimental_rerun()

    # Output display area
    st.subheader("📝 Assembled Prompt Preview")
    if "pb_assembled_prompt" not in st.session_state:
        st.session_state["pb_assembled_prompt"] = "Select blocks and fill in details to see your prompt assembled here."

    assembled_prompt_display = st.text_area(
        "Preview of Assembled Prompt:",
        value=st.session_state["pb_assembled_prompt"],
        height=300,
        key="pb_assembled_prompt_output",
        disabled=True
    )

    if st.session_state["pb_assembled_prompt"] and st.session_state["pb_assembled_prompt"] != "Select blocks and fill in details to see your prompt assembled here.":
        shared_utils.add_copy_to_clipboard_button(st.session_state["pb_assembled_prompt"], shared_utils.MSG_COPY_BUTTON)
        st.info("The prompt above is assembled from your selected blocks. Copy it for use.")
    else:
        st.info("Start by selecting blocks from the 'Conceptual Building Blocks' section.")

    # Logic for building the prompt
    if build_button_clicked:
        if not selected_conceptual_blocks:
            st.error("Please select at least one building block to construct the prompt.")
            return

        logger.info("Building prompt from selected blocks.")
        assembled_text = conceptual_assemble_prompt_from_blocks(selected_conceptual_blocks, block_data)
        st.session_state["pb_assembled_prompt"] = assembled_text
        st.success("Prompt successfully assembled!")
        st.experimental_rerun()

    shared_utils.display_ai_powered_notice()
    logger.info("Prompt Builder module UI rendered (conceptual).")
