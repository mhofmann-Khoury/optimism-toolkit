"""Decorators that transform the result of objective functions"""
from functools import wraps
from typing import Callable, Tuple


def inverse_objective(objective: Callable) -> Callable:
    """
    :param objective: the objective function to invert
    :return: inversion objective function
    """

    @wraps(objective)
    def inverse(design) -> float:
        """
        :param design: design to evaluate
        :return: Inverse of given objective score
        """
        inverse.base_function = objective
        return 1.0 - objective(design)

    return inverse


def target_value_objective(target: float, bounds: Tuple[float, float] = (0.0, 1.0)) -> Callable:
    """
    Evaluate the objective's proximity to a target value with a linear drop-off to the bounds.
    :param target: target value of objective
    :param bounds: bounds on objective values
    :return: target objective function
    """

    def decorator(objective: Callable) -> Callable:
        """
        :param objective: objective to modify
    :return: target objective function
        """

        @wraps(objective)
        def target_value(design) -> float:
            """

            :param design: design to evaluate
            :return: linear drop off value from target to bounds
            """
            target_value.base_function = objective
            value = objective(design)
            if value == target:
                return 1.0
            dist_to_target = abs(target - value)
            dist_to_lower = abs(target - bounds[0])
            dist_to_upper = abs(target - bounds[1])
            if value < target:  # portion of distance to lower bound
                return 1.0 - (dist_to_target / dist_to_lower)
            else:
                return 1.0 - (dist_to_target / dist_to_upper)

        return target_value

    return decorator
