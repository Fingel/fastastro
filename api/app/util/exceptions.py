class UniquValueException(Exception):
    def __init__(self, *args, field, value, **kwargs):
        self.field = field
        self.value = value
        return super().__init__(*args, **kwargs)
