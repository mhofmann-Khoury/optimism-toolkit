"""base classes for objectives and modifiers"""
from enum import Enum
from typing import Callable, Optional, Any, Dict


class Heuristic_Type(Enum):
    """
    Enumeration of heuristic function types
    """
    Objective = "objective"
    Modifier = "modifier"


class Heuristic_Function:
    """
        Structure for managing heuristic functions
    """

    def __init__(self, function: Callable, heuristic_type: Heuristic_Type, name: Optional[str] = None):
        self._heuristic_type: Heuristic_Type = heuristic_type
        self._function: Callable = function
        if name is None:
            self._name: str = function.__name__  # todo check python callable name
        else:
            self._name: str = name

    @property
    def name(self) -> str:
        """
        :return: name of the heuristic function
        """
        return self._name

    @property
    def is_objective(self) -> bool:
        """
        :return: True if is an objective
        """
        return self._heuristic_type is Heuristic_Type.Objective

    @property
    def is_modifier(self) -> bool:
        """
        :return: True if is a modifier
        """
        return self._heuristic_type is Heuristic_Type.Modifier

    def __str__(self):
        return f"{self._heuristic_type.value}:{self.name}"

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return hash(self) == hash(other)


class Objective(Heuristic_Function):
    """
        Manages and checks objective functions
    """

    def __init__(self, function: Callable, name: Optional[str] = None):
        super().__init__(function, Heuristic_Type.Objective, name)

    def __call__(self, design: Any, *args, **kwargs) -> float:
        result = self._function(design, *args, **kwargs)
        result_as_float = float(result)
        assert 0.0 <= result_as_float <= 1.0, f"Expected objective score of {self} to be between 0 and 1 but got {result}"
        return result_as_float


class Modifier(Heuristic_Function):
    """
        Manages and checks output of a modifier
    """

    def __init__(self, function: Callable, name: Optional[str] = None, deep_copy: bool = False):
        super().__init__(function, Heuristic_Type.Modifier, name)
        self._deep_copy = deep_copy
        self.applications: int = 0
        self.unique_applications: int = 0
        self.score_changes: float = 0.0
        self.score_increases: int = 0
        self.score_decreases: int = 0
        self.objective_changes: Dict[Objective, float] = {}
        self.objective_increases: Dict[Objective, int] = {}
        self.objective_decreases: Dict[Objective, int] = {}
        self.heuristic_map = None

    def add_new_objective(self, objective: Objective):
        """
        Records a new objective modified by this modifier
        :param objective: objective to record
        """
        self.objective_changes[objective] = 0.0
        self.objective_increases[objective] = 0
        self.objective_decreases[objective] = 0

    def record_application(self, design_change, is_unique: bool = True):
        """
        Records the results of applying this modifier
        :param is_unique: True if this the first application of this modifier to between these iterations
        :param design_change: the comparison between prior and resulting iteration
        """
        self.heuristic_map.remove_from_sorted_modifiers(self)
        self.unique_applications += int(is_unique)
        self.applications += 1
        self.score_changes += design_change.score_change
        self.score_increases += int(design_change.score_increased)
        self.score_decreases += int(design_change.score_decreased)
        for o in design_change:
            if o not in self.objective_changes:
                self.objective_changes[o] = 0.0
                self.objective_increases[o] = 0
                self.objective_decreases[o] = 0
            self.objective_changes[o] += design_change.objective_changes[o]
            self.objective_increases[o] += int(design_change.objective_increased[o])
            self.objective_decreases[o] += int(design_change.objective_decreased[o])

        assert self.heuristic_map is not None
        self.heuristic_map.update_modifier_sort(self)

    def __call__(self, design: Any, *args, **kwargs) -> Any:
        if self._deep_copy:
            design = design.copy()  # todo, more consistent way to do copies?
        modified_design = self._function(design, *args, **kwargs)
        return modified_design
