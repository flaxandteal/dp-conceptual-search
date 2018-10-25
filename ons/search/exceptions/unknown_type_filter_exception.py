class UnknownTypeFilter(Exception):
    def __init__(self, unknown_type_filter: str):
        super(UnknownTypeFilter, self).__init__("Unknown type filter: '{0}'".format(unknown_type_filter))

        self.unknown_type_filter = unknown_type_filter
