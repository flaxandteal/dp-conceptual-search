class UnknownTypeFilter(Exception):
    def __init__(self, type_filter: str):
        super(UnknownTypeFilter, self).__init__("Unknown type filter: '{0}'".format(type_filter))
