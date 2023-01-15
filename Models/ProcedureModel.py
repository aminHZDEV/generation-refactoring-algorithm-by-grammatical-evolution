from Models.RuleModel import Rule


class ProcedureModel(Rule):
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
        super().__init__(source=source, target=target, type=type)

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
