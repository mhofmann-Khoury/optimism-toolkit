import random

from heuristics.Heuristic_Map import Heuristic_Map
from heuristics.Objective_Function import Objective_Function
from heuristics.heuristic_functions import Objective, Modifier
from optimizer.Optimizer import Optimizer
from selector_functions.design_selectors.design_selectors import Highest_Scoring_Design
from selector_functions.modifier_selectors.modifier_selectors import Best_For_Lowest_Objective_Modifier
from stopping_criteria.stopping_criteria import stop_if_any_criteria_met, stop_at_threshold_score, stop_at_N_iterations


def less_than_number(number: int, target: int) -> float:
    """
    :param number: number that is guessed
    :param target: target number to guess
    :return: 1 if n>t or distances from n to t
    """
    if number >= target:
        return 1.0
    else:
        return 1.0 - ((target - number) / 100)


def greater_than_number(number: int, target: int) -> float:
    """
    :param number: number that is guessed
    :param target: target number to guess
    :return: 1 if n<t or distances from n to t
    """
    if number <= target:
        return 1.0
    else:
        return 1.0 - ((number - target) / 100)


def increment(number: int) -> int:
    """
    :param number: number to increment.
    :return: incremented number by 1
    """
    i = min(number + 1, 100)
    print(f"{number} ^ {i}")
    return i


def decrement(number: int) -> int:
    """
    :param number: number to decrement.
    :return: decremented number by 1
    """
    i = max(number - 1, 0)
    print(f"{number} v {i}")
    return i


def guess_the_number():
    """
    Generate a
    :return: Discovered Design population
    """
    target = random.randint(0, 100)
    print(f"Target == {target}")
    le_objective = Objective(lambda number: less_than_number(number, target), name='le')
    ge_objective = Objective(lambda number: greater_than_number(number, target), name='ge')
    objective_function = Objective_Function({le_objective: 1.0,
                                             ge_objective: 1.0})
    heuristic_map = Heuristic_Map({Modifier(increment): {le_objective: 1.0},
                                   Modifier(decrement): {ge_objective: 1.0}})

    design_selector = Highest_Scoring_Design()
    modifier_selector = Best_For_Lowest_Objective_Modifier()
    stopping_criteria = lambda design_iteration, design_population: stop_if_any_criteria_met(design_iteration=design_iteration,
                                                                                             design_population=design_population,
                                                                                             criteria=[stop_at_threshold_score, stop_at_N_iterations])

    guesses = [random.randint(0, 100) for _ in range(0, 10)]
    optimizer = Optimizer(design_selector, modifier_selector, stopping_criteria)
    population = optimizer.optimize(objective_function, heuristic_map, guesses)
    return population.top_N_iterations(1)


print(f"Guessed: {guess_the_number()[0].design}")
