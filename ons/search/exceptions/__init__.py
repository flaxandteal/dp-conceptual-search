class MalformedSearchTerm(Exception):
    def __init__(self, search_term: str):
        super(MalformedSearchTerm, self).__init__("Malformed search term: '{0}'".format(search_term))


class UnknownTypeFilter(Exception):
    def __init__(self, unknown_type_filter: str):
        super(UnknownTypeFilter, self).__init__("Unknown type filter: '{0}'".format(unknown_type_filter))

        self.unknown_type_filter = unknown_type_filter

