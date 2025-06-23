# modules/prompt_library.py
# This module implements the "Prompt Library" feature of the PromptGPT Suite.
# It provides a collection of categorized and searchable prompt templates
# that users can browse, use, and potentially contribute to.

import streamlit as st
import pandas as pd
import logging
from modules import shared_utils # Import shared utility functions

logger = logging.getLogger(__name__)

# ====================================================================================================
# SECTION 1: MODULE-SPECIFIC CONSTANTS AND DATA
# Defines the structure and content for the prompt library.
# In a real enterprise app, this data would come from a database.
# ====================================================================================================

# 1.1 Initial Help Message
PROMPT_LIBRARY_HELP_MESSAGE = """
### Explore the Prompt Library!
Discover a vast collection of pre-designed prompts for various AI tasks.
* **Browse Categories:** Filter prompts by their type (e.g., Creative, Technical).
* **Search:** Find specific prompts using keywords.
* **Copy & Adapt:** Use prompts directly or modify them in the Prompt Generator.
"""

# 1.2 Hardcoded Sample Prompts (Simulating a Database/API)
# In a full-scale application, this data would be loaded from a database (e.g., Firestore),
# an external API, or a structured file. For this demo, we use a Python list of dictionaries.
SAMPLE_PROMPTS = [
    {
        "id": 1,
        "name": "Creative Story Starter",
        "category": "Creative Writing",
        "tags": ["story", "creative", "fiction", "fantasy"],
        "prompt_text": "Write the first paragraph of a fantasy novel where a disillusioned wizard discovers a hidden, sentient forest.",
        "tone": "Descriptive",
        "format": "Paragraph",
        "complexity": "Intermediate"
    },
    {
        "id": 2,
        "name": "Email for Client Update",
        "category": "Business Communication",
        "tags": ["email", "business", "update", "client"],
        "prompt_text": "Draft a concise professional email to a client providing a weekly project update. Highlight progress on 'Feature X' and mention upcoming steps for 'Module Y'. Maintain a formal yet friendly tone.",
        "tone": "Formal, Friendly",
        "format": "Email",
        "complexity": "Beginner"
    },
    {
        "id": 3,
        "name": "Python Function for Data Analysis",
        "category": "Coding & Development",
        "tags": ["python", "code", "data analysis", "function"],
        "prompt_text": "Write a Python function named `analyze_sales_data` that takes a Pandas DataFrame with columns 'Product', 'Region', 'Sales', and 'Date' as input. The function should calculate total sales per region and return the top 3 regions by sales. Include docstrings and type hints.",
        "tone": "Technical",
        "format": "Code Snippet",
        "complexity": "Advanced"
    },
    {
        "id": 4,
        "name": "Social Media Post (Product Launch)",
        "category": "Marketing",
        "tags": ["social media", "marketing", "product launch", "tweet"],
        "prompt_text": "Create a catchy social media post (for Twitter/X) announcing the launch of a new eco-friendly water bottle. Emphasize sustainability and durability. Include relevant emojis and hashtags.",
        "tone": "Enthusiastic",
        "format": "Social Media Post",
        "complexity": "Beginner"
    },
    {
        "id": 5,
        "name": "Debate Argument: AI in Education",
        "category": "Academic",
        "tags": ["debate", "education", "AI", "argument"],
        "prompt_text": "Prepare a structured argument supporting the integration of AI tools in K-12 education. Focus on personalized learning, efficiency for teachers, and access to information. Provide three main points with supporting evidence.",
        "tone": "Academic, Persuasive",
        "format": "Numbered List",
        "complexity": "Intermediate"
    },
    {
        "id": 6,
        "name": "Recipe for Vegan Chili",
        "category": "Lifestyle",
        "tags": ["recipe", "cooking", "vegan", "food"],
        "prompt_text": "Provide a simple, easy-to-follow recipe for a classic vegan chili. Include ingredients list, step-by-step instructions, and approximate cooking time. Assume basic cooking knowledge.",
        "tone": "Instructive",
        "format": "Recipe",
        "complexity": "Beginner"
    },
    {
        "id": 7,
        "name": "Job Interview Questions (Software Engineer)",
        "category": "HR & Recruitment",
        "tags": ["interview", "job", "software engineer", "questions"],
        "prompt_text": "Generate 5 behavioral and 5 technical interview questions for a junior software engineer position. Behavioral questions should focus on teamwork and problem-solving, technical on Python and basic algorithms.",
        "tone": "Professional, Direct",
        "format": "Numbered List",
        "complexity": "Intermediate"
    },
    {
        "id": 8,
        "name": "Dialogue: Customer Support Issue",
        "category": "Customer Service",
        "tags": ["dialogue", "customer service", "script", "support"],
        "prompt_text": "Write a short dialogue between a customer (frustrated about a delayed delivery) and a customer service representative (calm and helpful) aiming to resolve the issue. Include empathy and a clear solution.",
        "tone": "Empathetic",
        "format": "Dialogue",
        "complexity": "Intermediate"
    },
    {
        "id": 9,
        "name": "Historical Event Summary: Moon Landing",
        "category": "Education",
        "tags": ["history", "summary", "space", "moon landing"],
        "prompt_text": "Provide a concise summary of the Apollo 11 Moon Landing (1969), focusing on its key figures, significance, and immediate impact. Limit to 200 words.",
        "tone": "Informative",
        "format": "Summary",
        "complexity": "Beginner"
    },
    {
        "id": 10,
        "name": "JSON Schema for User Profile",
        "category": "Coding & Development",
        "tags": ["json", "schema", "API", "user profile"],
        "prompt_text": "Generate a JSON schema for a user profile object, including fields for 'id' (string), 'username' (string), 'email' (string, email format), 'age' (integer, min 18), 'is_active' (boolean), and 'roles' (array of strings).",
        "tone": "Technical",
        "format": "JSON",
        "complexity": "Advanced"
    }
]

# Convert to DataFrame for easier searching and filtering
PROMPT_DF = pd.DataFrame(SAMPLE_PROMPTS)

# Extract unique categories and tags for filtering
ALL_CATEGORIES = ["All"] + sorted(PROMPT_DF["category"].unique().tolist())
ALL_TAGS = sorted(list(set([tag for tags_list in PROMPT_DF["tags"] for tag in tags_list])))


# ====================================================================================================
# SECTION 2: STREAMLIT UI LAYOUT AND INTERACTION
# This section defines the user interface for the Prompt Library module.
# ====================================================================================================

def run(api_key_valid: bool):
    """
    Main function to run the Prompt Library module's Streamlit UI.
    This function is called by app.py when the 'Prompt Library' module is selected.
    """
    st.header("📚 Prompt Library")
    st.markdown("Browse and utilize a collection of expert-crafted prompt templates.")
    st.markdown("---")

    # Display initial help message.
    shared_utils.display_module_help(PROMPT_LIBRARY_HELP_MESSAGE)

    # 2.1 Search and Filter Controls
    st.subheader("🔍 Search & Filter Prompts")
    col_search, col_category, col_tags = st.columns([0.5, 0.25, 0.25])

    with col_search:
        search_query = st.text_input(
            "Search by Keyword:",
            value=st.session_state.get("pl_search_query", ""),
            placeholder="e.g., 'story', 'email', 'python'",
            key="pl_search_query_input",
            help="Type keywords to find relevant prompts by name or content."
        )
        st.session_state["pl_search_query"] = search_query

    with col_category:
        selected_category_index = ALL_CATEGORIES.index(st.session_state.get("pl_selected_category", "All")) \
            if st.session_state.get("pl_selected_category", "All") in ALL_CATEGORIES else 0
        selected_category = st.selectbox(
            "Filter by Category:",
            options=ALL_CATEGORIES,
            index=selected_category_index,
            key="pl_category_select",
            help="Narrow down prompts by their primary category."
        )
        st.session_state["pl_selected_category"] = selected_category

    with col_tags:
        # Use multiselect for tags to allow multiple tag filters
        selected_tags = st.multiselect(
            "Filter by Tags:",
            options=ALL_TAGS,
            default=st.session_state.get("pl_selected_tags", []),
            key="pl_tags_multiselect",
            help="Select one or more tags to filter prompts."
        )
        st.session_state["pl_selected_tags"] = selected_tags

    st.markdown("---")

    # 2.2 Filter Prompts Logic
    filtered_df = PROMPT_DF.copy()

    # Apply search query filter
    if search_query:
        # Search across 'name', 'prompt_text', and 'category'
        filtered_df = filtered_df[
            filtered_df.apply(
                lambda row: search_query.lower() in str(row['name']).lower() or
                            search_query.lower() in str(row['prompt_text']).lower() or
                            search_query.lower() in str(row['category']).lower(),
                axis=1
            )
        ]
        logger.debug(f"Filtered by search query: {search_query}. Rows: {len(filtered_df)}")


    # Apply category filter
    if selected_category != "All":
        filtered_df = filtered_df[filtered_df["category"] == selected_category]
        logger.debug(f"Filtered by category: {selected_category}. Rows: {len(filtered_df)}")

    # Apply tags filter
    if selected_tags:
        # Filter rows where ANY of the selected_tags are present in the 'tags' list
        filtered_df = filtered_df[
            filtered_df["tags"].apply(lambda tags_list: any(tag in tags_list for tag in selected_tags))
        ]
        logger.debug(f"Filtered by tags: {selected_tags}. Rows: {len(filtered_df)}")

    st.subheader(f"✨ Available Prompts ({len(filtered_df)} found)")

    if filtered_df.empty:
        st.info("No prompts match your current filters. Try adjusting your search or categories.")
        logger.info("No prompts found for current filters.")
    else:
        # 2.3 Display Filtered Prompts
        # Iterate through the filtered DataFrame and display each prompt.
        for index, row in filtered_df.iterrows():
            with st.expander(f"**{row['name']}** ({row['category']})", expanded=False):
                st.markdown(f"**Description:** {row['prompt_text']}")
                st.markdown(f"**Tone:** `{row['tone']}` | **Format:** `{row['format']}` | **Complexity:** `{row['complexity']}`")
                st.markdown(f"**Tags:** `{'`, `'.join(row['tags'])}`")

                # "Use This Prompt" button copies the prompt text and can potentially
                # navigate to the Prompt Generator with this prompt pre-filled.
                col_use, col_copy = st.columns([0.2, 0.8])
                with col_use:
                    if st.button(f"🚀 Use This Prompt", key=f"use_prompt_{row['id']}", help="Pre-fill this prompt in the Prompt Generator module."):
                        st.session_state["current_module"] = "Prompt Generator"
                        st.session_state["pg_user_task"] = row['prompt_text']
                        # Try to pre-select tone and format if they exist in the Generator's lists.
                        if row['tone'] in shared_utils.PROMPT_GENERATOR_TONES:
                            st.session_state["pg_selected_tone"] = row['tone']
                        if row['format'] in shared_utils.PROMPT_GENERATOR_FORMATS:
                            st.session_state["pg_selected_format"] = row['format']
                        st.success(f"Prompt '{row['name']}' copied to Prompt Generator.")
                        st.experimental_rerun() # Rerun to switch module and update generator.
                        logger.info(f"User chose to use prompt ID {row['id']} in Generator.")

                with col_copy:
                    # Provide a direct copy button for the prompt text
                    shared_utils.add_copy_to_clipboard_button(row['prompt_text'], f"📋 Copy Prompt #{row['id']}")
                    st.info("Click 'Use This Prompt' to pre-fill it in the Prompt Generator, or 'Copy Prompt' for direct use.")

    shared_utils.display_ai_powered_notice() # Indicate AI generation capabilities (if relevant for future features).
    logger.info("Prompt Library module UI rendered.")
