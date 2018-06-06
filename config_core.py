import os

CONCEPTUAL_SEARCH_ENABLED = os.environ.get('CONCEPTUAL_SEARCH_ENABLED', 'False').lower() == 'true'
