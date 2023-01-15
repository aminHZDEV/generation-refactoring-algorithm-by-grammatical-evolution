class Rule:
    def __init__(self, source: str = "", target: str = "", type: str = ""):
        self._source_class = source
        self._target_class = target
        self._type = type

    @property
    def source(self):
        return self._source_class

    @property
    def target(self):
        return self._target_class

    @property
    def type(self):
        return self._source_class

    @source.setter
    def source(self, a):
        self._source_class = a

    @target.setter
    def target(self, a):
        self._target_class = a

    @type.setter
    def type(self, a):
        self._type = a
