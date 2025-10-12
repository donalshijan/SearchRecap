#!/usr/bin/env python3
"""
Configuration examples for InferenceManager.
Copy the relevant configuration to your config.py file.
"""

# =============================================================================
# EXAMPLE 1: GOOGLE SEARCH QUERIES (Current Default)
# =============================================================================
GOOGLE_QUERIES_CONFIG = {
    "DATA_LABEL": "queries",
    "DATA_DESCRIPTION": "Google search queries",
    "TASK_DESCRIPTION": "filter for educational and meaning-related content",
    "TASK_INSTRUCTIONS": (
        "Extract only the items where the intent is to understand the "
        "meaning, definition, usage, or origin of a word, phrase, idiom, "
        "or expression."
    )
}

# =============================================================================
# EXAMPLE 2: COMPANY NAMES
# =============================================================================
COMPANY_NAMES_CONFIG = {
    "DATA_LABEL": "companies",
    "DATA_DESCRIPTION": "company names from a business directory",
    "TASK_DESCRIPTION": "filter for technology companies",
    "TASK_INSTRUCTIONS": (
        "Extract only company names that are clearly technology or "
        "software companies, startups, or tech-related businesses."
    )
}

# =============================================================================
# EXAMPLE 3: PRODUCT NAMES
# =============================================================================
PRODUCT_NAMES_CONFIG = {
    "DATA_LABEL": "products",
    "DATA_DESCRIPTION": "product names from an e-commerce catalog",
    "TASK_DESCRIPTION": "categorize by product type",
    "TASK_INSTRUCTIONS": (
        "Classify each product as electronics, clothing, books, "
        "home & garden, or other. Return only electronics products."
    )
}

# =============================================================================
# EXAMPLE 4: PERSON NAMES
# =============================================================================
PERSON_NAMES_CONFIG = {
    "DATA_LABEL": "names",
    "DATA_DESCRIPTION": "list of people's names",
    "TASK_DESCRIPTION": "identify gender-neutral names",
    "TASK_INSTRUCTIONS": (
        "Extract names that could be used for either gender, "
        "avoiding names that are clearly masculine or feminine."
    )
}

# =============================================================================
# EXAMPLE 5: SENTIMENT ANALYSIS
# =============================================================================
SENTIMENT_ANALYSIS_CONFIG = {
    "DATA_LABEL": "reviews",
    "DATA_DESCRIPTION": "customer product reviews",
    "TASK_DESCRIPTION": "classify sentiment",
    "TASK_INSTRUCTIONS": (
        "Classify each review as positive, negative, or neutral "
        "based on the sentiment expressed."
    )
}

# =============================================================================
# EXAMPLE 6: CONTENT CATEGORIZATION
# =============================================================================
CONTENT_CATEGORIZATION_CONFIG = {
    "DATA_LABEL": "articles",
    "DATA_DESCRIPTION": "article titles and descriptions",
    "TASK_DESCRIPTION": "categorize by topic",
    "TASK_INSTRUCTIONS": (
        "Categorize each article as technology, health, finance, "
        "entertainment, or other based on the title and description."
    )
}

# =============================================================================
# EXAMPLE 7: LANGUAGE DETECTION
# =============================================================================
LANGUAGE_DETECTION_CONFIG = {
    "DATA_LABEL": "texts",
    "DATA_DESCRIPTION": "short text samples",
    "TASK_DESCRIPTION": "detect language",
    "TASK_INSTRUCTIONS": (
        "Identify the language of each text sample. "
        "Return only English language texts."
    )
}

# =============================================================================
# EXAMPLE 8: QUALITY FILTERING
# =============================================================================
QUALITY_FILTERING_CONFIG = {
    "DATA_LABEL": "comments",
    "DATA_DESCRIPTION": "user comments from a forum",
    "TASK_DESCRIPTION": "filter for high-quality content",
    "TASK_INSTRUCTIONS": (
        "Extract only comments that are constructive, informative, "
        "and contribute meaningfully to the discussion. "
        "Exclude spam, insults, or low-effort posts."
    )
}

# =============================================================================
# HOW TO USE:
# =============================================================================
"""
1. Choose the configuration that matches your use case
2. Copy the values to your config.py file:

# Example: For company names
DATA_LABEL = "companies"
DATA_DESCRIPTION = "company names from a business directory"
TASK_DESCRIPTION = "filter for technology companies"
TASK_INSTRUCTIONS = (
    "Extract only company names that are clearly technology or "
    "software companies, startups, or tech-related businesses."
)

3. Update your input file to match the expected JSON structure
4. Run the inference: python main.py

Note: You can also create custom configurations by following the same pattern!
"""
