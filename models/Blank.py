class Blank:
    def __init__(self):
        pass

    def __eq__(self, other):
        return isinstance(other, Blank)
