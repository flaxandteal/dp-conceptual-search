class Hit(dict):
    def __init__(self, *args, **kwargs):
        super(Hit, self).__init__(*args, **kwargs)

    def set_value(self, field_name, value):
        if field_name in self:
            self[field_name] = value
        elif "." in field_name:
            parts = field_name.split(".")
            if parts[0] == "description" and len(parts) <= 2:
                self["description"][parts[1]] = value
        else:
            raise Exception("Unable to set field %s" % field_name)
