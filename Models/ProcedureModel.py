from typing import Any


class ProcedureModel:
    def __init__(
        self,
        refactoring_type: str = "",
        source: str = "",
        target: str = "",
        name: str = "",
        type: str = "",
    ):
        self._name = name
        self._refactoring = refactoring_type
        self._source = source
        self._target = target
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

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, a):
        self._name = a

    @property
    def refactoring(self):
        return self._refactoring

    @refactoring.setter
    def refactoring(self, a):
        self._refactoring = a
