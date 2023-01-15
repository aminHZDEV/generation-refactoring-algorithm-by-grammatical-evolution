from Models.ProcedureModel import ProcedureModel
from Refactorings import (
    ExtractClass,
    MoveMethod,
    PullUpMethod,
    PushDownMethod,
    PullUpConstructor,
)
import understand as und
import random
from collections import Counter
from antlr4 import *


class GrammarClass:
    """
    < procedure >: := < rtype > < procedure > | < rtype >
    < rtype >: := < extractClass > | < moveMethod > | < pullUpMethod > | < pushDownMethod > | < Pull Up Constructor >
    < extractClass >: := < searchClass >
    < moveMethod >: := < searchMethod > < searchClass >
    < pullUpMethod >: := < searchMethod > < searchClass >
    < pushDownMethod >: := < searchMethod > < searchClass >
    < Pull Up Constructor >: := < searchClass >
    """

    def __init__(
        self, chromosome: list = None, udb_path: str = "", project_path: str = ""
    ):
        self.chromosome = chromosome[0]
        self.udb_path = udb_path
        self.pvot = 0
        self.project_path = project_path
        self.rf_list = []

    def _procedure(self):
        print("TEST 00 : ", self.chromosome)
        print("TEST 01 : ", self.chromosome[self.pvot] % 2)

        if len(self.chromosome) > 0:
            num = self.chromosome[self.pvot] % 2
            self.pvot += 1
            if num == 0:
                print("TEST 02 : ")
                return self._rtype(), self._procedure()
            elif num == 1:
                print("TEST 03 : ")
                return self._rtype()
        return self.rf_list

    def _rtype(self):

        if len(self.chromosome) > 1:
            print("TEST 04 : ")
            num = self.chromosome[self.pvot] % 5
            print("TEST 05 : ", num)
            self.pvot += 1
            if num == 0:
                return self._extractClass()
            elif num == 1:
                return self._moveMethod()
            elif num == 2:
                return self._pullUpMethod()
            elif num == 3:
                return self._pushDownMethod()
            elif num == 4:
                return self._pullUpConstructor()

        return None

    def _extractClass(self):
        random_class, moved_filed, move_methods = self._searchClass()
        source_class = random_class.simplename()
        if ExtractClass.main(
            udb_path=self.udb_path,
            file_path=random_class.parent().longname(),
            source_class=source_class,
            moved_fields=moved_filed,
            moved_methods=move_methods,
        ):
            self.rf_list.append(
                ProcedureModel(
                    refactoring_type="ExtractClass",
                    source=source_class,
                    target="",
                    name=str(moved_filed),
                    type="class",
                )
            )

    def _moveMethod(self):
        random_class, moved_filed, move_methods = self._searchClass()
        parent = random_class.parent()
        long_name = parent.longname().split(".")
        source_package = None
        source_class = None
        if len(long_name) == 1:
            source_class = long_name[-1]
        elif len(long_name) > 1:
            source_class = long_name[-1]
            source_package = ".".join(long_name[:-1])

        target_package = None
        target_class = None

        """
        target_class: str, target_package: str,
        """

        if len(random_class) == 1:
            target_class = random_class[0]
        elif len(random_class) > 1:
            target_package = ".".join(random_class[:-1])
            target_class = random_class[-1]
        method_name = random.choice(move_methods)

        if MoveMethod.main(
            source_class=source_class,
            source_package=source_package,
            target_class=target_class,
            target_package=target_package,
            method_name=method_name,
            udb_path=self.udb_path,
        ):

            self.rf_list.append(
                ProcedureModel(
                    refactoring_type="MoveMethod",
                    source=source_class,
                    target=target_class,
                    name=method_name,
                    type="Method",
                )
            )

    def _pullUpMethod(self):
        _db = und.open(self.udb_path)
        candidates = []
        class_entities = _db.ents(
            "Class ~Unknown ~Anonymous ~TypeVariable ~Private ~Static"
        )
        common_methods = []

        for ent in class_entities:
            children = []
            class_method_dict = {}
            father_methods = []

            for met_ref in ent.refs("Define", "Method ~Override"):
                method = met_ref.ent()
                father_methods.append(method.simplename())

            for ref in ent.refs("Extendby"):
                child = ref.ent()
                if not child.kind().check("public class"):
                    continue
                child_name = child.simplename()
                children.append(child_name)
                if child_name not in class_method_dict:
                    class_method_dict[child_name] = []

                for met_ref in child.refs("Define", "Method"):
                    method = met_ref.ent()
                    method_name = method.simplename()

                    if method.ents("Override"):
                        continue

                    if method_name not in father_methods:
                        common_methods.append(method_name)
                        class_method_dict[child_name].append(method_name)

            counts = Counter(common_methods)
            common_methods = [value for value, count in counts.items() if count > 1]
            if len(common_methods) > 0:
                random_method = random.choice(common_methods)
                children = [
                    k for k, v in class_method_dict.items() if random_method in v
                ]
                if len(children) > 1:
                    candidates.append(
                        {
                            "method_name": random.choice(common_methods),
                            "children_classes": children,
                        }
                    )
        candid = random.choice(candidates)
        _db.close()
        if PullUpMethod.main(
            udb_path=self.udb_path,
            children_classes=candid["children_classes"],
            method_name=candid["method_name"],
        ):
            self.rf_list.append(
                ProcedureModel(
                    refactoring_type="PullUpMethod",
                    source=candid["children_classes"],
                    target="",
                    name=candid["method_name"],
                    type="Method",
                )
            )

    def _pushDownMethod(self):
        _db = und.open(self.udb_path)
        candidates = []
        class_entities = _db.ents(
            "Class ~Unknown ~Anonymous ~TypeVariable ~Private ~Static"
        )
        for ent in class_entities:
            params = {
                "source_class": "",
                "source_package": "",
                "method_name": "",
                "target_classes": [],
            }
            method_names = []

            for ref in ent.refs("Extendby ~Implicit", "Public Class"):
                params["source_class"] = ent.simplename()
                ln = ent.longname().split(".")
                params["source_package"] = ln[0] if len(ln) > 1 else ""
                params["target_classes"].append(ref.ent().simplename())

            for ref in ent.refs("Define", "Method"):
                method_names.append(ref.ent().simplename())

            if method_names:
                params["method_name"] = random.choice(method_names)
            else:
                continue

            if params["target_classes"]:
                params["target_classes"] = [random.choice(params["target_classes"])]
            else:
                continue

            if params["source_class"] != "":
                candidates.append(params)
        candid = random.choice(candidates)
        _db.close()
        if PushDownMethod.main(
            udb_path=self.udb_path,
            source_class=candid["source_class"],
            source_package=candid["source_package"],
            method_name=candid["method_name"],
            target_classes=candid["target_classes"],
        ):
            self.rf_list.append(
                ProcedureModel(
                    refactoring_type="PushDownMethod",
                    source=candid["source_class"],
                    target=candid["target_classes"],
                    name=candid["method_name"],
                    type="Method",
                )
            )

    def _pullUpConstructor(self):
        _db = und.open(self.udb_path)
        candidates = []
        class_entities = _db.ents(
            "Class ~Unknown ~Anonymous ~TypeVariable ~Private ~Static"
        )
        for ent in class_entities:
            children = []
            params = {}
            for ref in ent.refs("Extendby"):
                child = ref.ent()
                if not child.kind().check("public class"):
                    continue
                child_name = child.simplename()
                children.append(child_name)

            ln = ent.longname().split(".")
            params["source_package"] = ".".join(ln[:-1]) if len(ln) > 1 else ""
            params["target_class"] = ent.simplename()
            if len(children) >= 2:
                params["class_names"] = random.sample(
                    children, random.randint(2, len(children))
                )
                candidates.append(params)
        try:
            if PullUpConstructor.main(
                udb_path=self.udb_path,
                class_names=params["class_names"],
                target_class=params["target_class"],
                source_package=params["source_package"],
            ):
                self.rf_list.append(
                    ProcedureModel(
                        refactoring_type="PullUpConstructor",
                        source=params["class_names"],
                        target=params["target_class"],
                        name="",
                        type="Class",
                    )
                )
        except Exception as e:
            print("PullUpConstructor ERROR : ", e)
        _db.close()

    def _searchClass(self):
        _db = und.open(self.udb_path)
        classes = _db.ents("Type Class ~Unknown ~Anonymous")
        random_class = random.choice(classes)
        class_fields = []
        class_methods = []
        for ref in random_class.refs("define", "variable"):
            class_fields.append(ref.ent())

        for ref in random_class.refs("define", "method"):
            class_methods.append(ref.ent())
        moved_filed = [
            ent.simplename()
            for ent in random.sample(
                class_methods, random.randint(0, len(class_methods))
            )
        ]
        move_methods = [
            ent.simplename()
            for ent in random.sample(class_fields, random.randint(0, len(class_fields)))
        ]
        _db.close()
        return random_class, moved_filed, move_methods

    def searchMethod(self):
        pass


class GrammarClassWithCluster:
    def __init__(self, chromosome: list = None):
        self.chromosome = chromosome

    """
    <procedure> ::= <rtype> <procedure> | <rtype>
    <rtype> ::= <extractClass> | <moveMethod> | <pullUpMethod> | <pushDownMethod> | <inlineClass>
    <extractClass> ::= <searchClass>
    <moveMethod> ::= <searchMethod> <searchClass>
    <pullUpMethod> ::= <searchMethod> <searchClass>
    <pushDownMethod> ::= <searchMethod> <searchClass>
    <inlineClass> ::= <searchClass> <searchClass>
    <searchClass> ::= <ru1> <ru2> <ru3> <ru4> <ru5> <ru6> <ru7> <ru8>
    <searchMethod> ::= <ru9> <ru10>
    <ru1> ::= IntervalA | IntervalB | IntervalC | ... | IntervalN
    <ru2> ::= IntervalA | IntervalB | IntervalC | ... | IntervalN
    <ru3> ::= IntervalA | IntervalB | IntervalC | ... | IntervalN
    <ru4> ::= IntervalA | IntervalB | IntervalC | ... | IntervalN
    <ru5> ::= IntervalA | IntervalB | IntervalC | ... | IntervalN
    <ru6> ::= IntervalA | IntervalB | IntervalC | ... | IntervalN
    <ru7> ::= IntervalA | IntervalB | IntervalC | ... | IntervalN
    <ru8> ::= IntervalA | IntervalB | IntervalC | ... | IntervalN
    <ru9> ::= IntervalA | IntervalB | IntervalC | ... | IntervalN
    <ru10> ::= IntervalA | IntervalB | IntervalC | ... | IntervalN
    """

    def _procedure(self):
        if len(self.chromosome) > 0:
            num = self.chromosome[0] % 2
            if num == 0:
                return self._rtype(), self._procedure()
            elif num == 1:
                return self._rtype()
        return None

    def _rtype(self):
        if len(self.chromosome) > 1:
            num = self.chromosome[1] % 5
            if num == 0:
                return self._extractClass()
            elif num == 1:
                return self._moveMethod()
            elif num == 2:
                return self._pullUpMethod()
            elif num == 3:
                return self._pushDownMethod()
            elif num == 4:
                return self._inlineClass()
        return None

    def _extractClass(self):
        pass

    def _moveMethod(self):
        pass

    def _pullUpMethod(self):
        pass

    def _pushDownMethod(self):
        pass

    def _inlineClass(self):
        pass

    def _searchClass(self):
        pass

    def searchMethod(self):
        pass

    def _ru1(self):
        pass

    def _ru2(self):
        pass

    def _ru3(self):
        pass

    def _ru4(self):
        pass

    def _ru5(self):
        pass

    def _ru6(self):
        pass

    def _ru7(self):
        pass

    def _ru8(self):
        pass

    def _ru9(self):
        pass

    def _ru10(self):
        pass
