import inspect
from typing import Dict, Callable, Optional

from heuristics.heuristic_functions import Objective, Modifier, Heuristic_Type


class Heuristic_Library:
    """Library that Keeps track of all Registered Heuristics"""

    def __init__(self, library_name: str):
        self._library_name = library_name
        self._objectives: Dict[str: Objective] = {}
        self._modifiers: Dict[str: Modifier] = {}

    def get_objective(self, name: str) -> Objective:
        """
        :param name:
        :return: objective by name
        """
        return self._objectives[name]

    def get_modifier(self, name: str) -> Modifier:
        """
        :param name:
        :return: modifier by name
        """
        return self._modifiers[name]

    def add_function(self, heuristic_type: Heuristic_Type, function: Callable, name: Optional[str], deep_copy: bool = False, **function_kwargs):
        """
        Add function by type to library
        :param heuristic_type: Modifier or Objective
        :param function: function to register
        :param name: name of function or None if derived from function
        :param deep_copy: True if modifier deep copies designs first
        :param function_kwargs: keyword arguments to add to objective
        """
        if heuristic_type is Heuristic_Type.Modifier:
            self.add_modifier(function, name, deep_copy, **function_kwargs)
        else:
            self.add_objective(function, name, **function_kwargs)

    def add_objective(self, objective_callable: Callable, objective_name: Optional[str], **objective_kwargs):
        """
        :param objective_callable: callable to create objective from
        :param objective_name: name for objective or callable name if None
        :param objective_kwargs: keyword arguments to add to the objective
        """
        if objective_name is None:
            if inspect.ismethod(objective_callable):
                objective_name = objective_callable.__qualname__
            elif inspect.isfunction(objective_callable) or inspect.isclass(objective_callable):
                objective_name = objective_callable.__name__
            else:
                assert False, f"{objective_callable} has not default name. Expected method, function, or callable class"
        if objective_name in self._objectives:
            print(f"OPTIMISM Warning: overloading objective {objective_name}")
        if len(objective_kwargs) == 0:
            objective = Objective(objective_callable, objective_name)
        else:
            objective = Objective(lambda design: objective_callable(design, **objective_kwargs), objective_name)
        self._objectives[objective_name] = objective

    def add_modifier(self, modifier_callable: Callable, modifier_name: Optional[str], deep_copy: bool = False, **modifier_kwargs):
        """
        :param modifier_callable: callable to create modifier from
        :param modifier_name: name for modifier or callable name if None.
        :param deep_copy: if true, modifier will copy design before modification
        :param modifier_kwargs: keyword arguments to add to the modifier
        """
        if modifier_name is None:
            if inspect.ismethod(modifier_callable):
                modifier_name = modifier_callable.__qualname__
            elif inspect.isfunction(modifier_callable) or inspect.isclass(modifier_callable):
                modifier_name = modifier_callable.__name__
            else:
                assert False, f"{modifier_callable} has not default name. Expected method, function, or callable class"
        if len(modifier_kwargs) == 0:
            if deep_copy:
                def copy_and_modify_no_kwargs(design):
                    """
                    :param design: design to be copied and modify
                    :return: copy design then modify the copy
                    """
                    copied_design = design.deep_copy()
                    return modifier_callable(copied_design)

                modifier = Modifier(copy_and_modify_no_kwargs, modifier_name)
            else:
                modifier = Modifier(modifier_callable, modifier_name)
        else:
            if deep_copy:
                def copy_and_modify(design):
                    """
                    :param design: design to be copied and modify
                    :return: copy design then modify the copy with modifier key word arguments
                    """
                    copied_design = design.deep_copy()
                    return modifier_callable(copied_design, **modifier_kwargs)

                modifier = Modifier(copy_and_modify, modifier_name)
            else:
                modifier = Modifier(lambda design: modifier_callable(design, **modifier_kwargs), modifier_name)
        self._modifiers[modifier_name] = modifier
