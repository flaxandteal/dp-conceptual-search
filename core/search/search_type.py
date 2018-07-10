from enum import Enum


class SearchType(Enum):
    QUERY_THEN_FETCH = "query_then_fetch"
    DFS_QUERY_THEN_FETCH = "dfs_query_then_fetch"

    def __str__(self):
        return self.value
