from json import JSONEncoder


class AutoJSONEncoder(JSONEncoder):
    def default(self, o):
        if hasattr(o, "__json__"):
            return o.__json__()
        else:
            return JSONEncoder.default(self, o)
