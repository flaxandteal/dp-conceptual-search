import os

CONCEPTUAL_SEARCH = os.getenv("CONCEPTUAL_SEARCH_ENABLED", "False").lower() == "true"
