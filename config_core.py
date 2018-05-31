import os

CONCEPTUAL_SEARCH_ENABLED = os.getenv(
    "CONCEPTUAL_SEARCH_ENABLED",
    "True").lower() == "true"
