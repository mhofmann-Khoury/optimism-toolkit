# OPTIMISM (Optimization Programming Toolkit Integrating Metaheuristic Intuitive Search-Methods)
OPTIMISM (Optimization Programming Toolkit Integrating Metaheuristic Intuitive Search Methods) is a toolkit that helps non-technical domain experts and programmers collaboratively implement optimizers in diverse domains. OPTIMISM is designed based on the principle that building optimizers requires collaboration between programmers and domain experts who tailor the methods to the specific domain, which is critical but often under-supported.

The toolkit is designed to be domain agnostic and enables domain experts to participate in optimizer implementation through a simple and generalized framework that can implement a wide variety of optimization methods. OPTIMISM deconstructs many metaheuristic methods into a small set of pluggable operations called objectives and modifiers, which helps domain experts express their goals and modification strategies. At the same time, OPTIMISM enables programmers to flexibly experiment with a variety of optimization methods with minimal additional coding.

The toolkit empowers domain experts and programmers to collaboratively create unique solutions while considering a variety of domain-specific goals. Designers with domain expertise can access optimizers through an automatically generated graphical user interface (GUI), while programmers can rapidly prototype domain-specific optimizers that apply objectives and modifiers.

In summary, OPTIMISM provides a platform for collaboration between domain experts and programmers, allowing them to work together to build customized optimizers for a wide range of domains.

# Setup
Clone the [repository](https://github.com/mhofmann-Khoury/optimism-toolkit) and source code:

```
git clone https://github.com/mhofmann-Khoury/optimism-toolkit.git
```

From the source directory install the required packages to your python environment:

```
pip install -r requirements.txt
```

# Building Optimizable Designs
Optimism is a toolkit that enables you to generate optimized "_designs_" using modular metaheuristic search methods. To do this you first need to build an optimizable design. A design can be anything you can express in Python code (e.g., cookie recipes, cataract lens prescriptions, tiled-surfaces). The way you represent your designs will have substantial effects on what you can create and optimize. 

Generally, we recommend using Python classes to represent your design. Your class should include features of the design that you would like to optimize for (i.e., objectives) and modify (i.e., modifiers). For an example class structure, look at the `cookie_optimizer.py` program in our examples package. The class contains parameters for all the ingredient amounts in a chocolate chip cookie. Testing and tweaking these amounts will generate different types of cookies.

Once you have your design class structure finalized you add some boilerplate OPTIMISM code to hook the class into the OPTIMISM framework. Each optimizable design needs a heuristic library. You create this by calling `make_heuristic_library(...)` and naming the heuristic libray for your design. This returns two values: the _heuristic decorator function_ which you will use to register heuristics into the _heuristic library_. 

```Python
"""Import heuristic library and create one for a specific design."""
from heuristics.heuristic_registration import make_heuristic_library
...
design_heuristic, design_heuristic_library = make_heuristic_library("Design Heuristic Library")

class Design:
    def __init__(self):
        self.design_parameter = ...
```

## Adding Objectives
Once you have the features of your design defined you need to give OPTIMISM a way to assess the quality of any given instance of your design. You do this by writing objective functions and registering them in the heuristic library. Objectives can be any function that takes in an instance of your design as its and only (non-default) parameter and returns a float between 0.0 and 1.0. The return value indicates if the design is performing well under some objective.  The closer the return value is to 1.0, the better it is performing. In the objective you can program any kind of evaluation that is import for the design domain. Generally, we recommend making efficient and simple objectives. Generally, objectives are class methods where the `self` parameter ensures the design is passed to the function first. You register the objective to the heuristic library using the following decorator pattern:

```Python
from heuristics.heuristic_functions import Heuristic_Type
...
@design_heuristic(Heuristic_Type.Objective, "Optional Objective Name")
def objective_method(self) -> float:
    objective_value = ...
    return objective_value
```

Note that the decorator is the first value returned from the `make_heuristic_library` function. To register the class method or function as an objective pass the decorator `Heuristic_Type.Objective`. The second parameter is an optional string for naming the objective. If this is left empty, the name used to register the objective will be the function name. 

## Adding Modifiers
Objectives provide a way to evaluate the quality of designs. Modifiers provide a method for changing designs so that they can improve those objective values. Like objectives, a modifier is a function that takes an instance of a design as its first and only non-default parameter. It then returns a modified copy of the design. You can modify the copied design however you want. We generally recommend making small changes (e.g., incrementing a parameter). You register modifiers in a similar way to objectives:

```Python
@design_heuristic(Heuristic_Type.Modifier, "Optional Modifier Name")
def modifier_method(self):
    copy = self.copy()
    copy.design_parameter = ...
    return copy
```

Note that the modifier must return a deep copy of the design instance. Otherwise, the optimizer will overwrite prior instances with modifiers. If your design class is compatible with the deep copy package from the [copy package](https://www.geeksforgeeks.org/copy-python-deep-copy-shallow-copy/), you can pass the `design_heuristic` decorator a default parameter `deepcopy=True`. In this case, your design will be copied and the modifier function will be applied to the copied instance. This lets you write methods that directly modify the design. The following deep copy sample will produce the same result with more legible code:
```Python
@design_heuristic(Heuristic_Type.Modifier, "Optional Modifier Name", deepcopy=True)
def modifier_method(self):
    self.design_parameter = ...
```

## Non-Default Heuristic Parameters
It is likely that you will want to create multiple objectives and modifiers with a variety of non-default parameters. To pass parameters to decorated objectives and modifiers you simply added keyword arguments to the decorator. For example, we can set an `increment` parameter twice with two decorators to create a decrement modifier. 

```Python
@design_heuristic(Heuristic_Type.Modifier, "Decrement 1", deepcopy=True, increment_amoount=-1.0)
@design_heuristic(Heuristic_Type.Modifier, "Increment 1", deepcopy=True)
def increment(self, increment_amount=1.0):
    self.design_parameter += increment_amount
```

## Common Heuristic Patterns
We provide a small library of decorators for heuristic functions that help set common patterns. For example, you can inverse the result of an objective (e.g., `1-objective_value`) with the following pattern:
```Python
@design_heuristic(Heuristic_Type.Objective, "Inversed Objective")
@inverse
def objective_method(self) -> float:
    objective_value = ...
    return objective_value
```
Note the that the `design_heuristic` decorator is still required to register the inverted objective.

# Configuring  an Optimizer 
Now that you have a design and have registered objectives and modifiers to the heuristic library you can build an optimizer for your design. 
## Flow of an Optimizer
An OPTIMISM optimizer flows as follows:

![A flow diagram of an optimizer that starts by evaluating a design using objectives, selects a design, considers the stopping criteria, and modifies the design by 1) choosing a modifier and 2) applying that modifier](/optimizer_flow.png).

You give the optimizer a set of at least one seed design. Each design is evaluated by objectives. Then a _design selector_ chooses a design. That design is tested against some _stopping criteria_. If it passes the criteria the full set of designs is returned. Otherwise, the design will be modified by first having a _modifier selector_ choose a modifier from your heuristic library and then having the modifier modify and create a new design. That design is then evaluated starting the cycle over again. The flow diagram above highlights pieces of the optimizer you build in blue and the pieces provide by OPTIMISM in yellow. 

## Defining a Heuristic Map
The optimizer will be guided by heuristics that you build from the objectives and modifiers you registered to the heuristic library. A heuristic is a weight between an objective and modifier. A `Heuristic_Map` keeps tracks of these weights and uses them to calculate the value of modifiers as your designs are optimized. 

To build a `Heuristic_Map` you provide a dictionary with objectives keyed to dictionaries of modifiers keyed to their heuristic weight to the objective. For shorthand, you can use the `add_heuristic` method to add these weights one by one.

```Python
from heuristics.Heuristic_Map import Heuristic_Map
...
objective = design_heuristic_library.get_objective(Design.objective_method)
modifier = design_heuristic_library.get_modifier(Design.modifier_method)
design_heuristic_map = Heuristic_Map()
design_heuristic_map.add_heuristic(objective, modifier, 1.0)
```

Note that objectives and modifiers can be accessed from the heuristic library by their function identifier or by the name you registered them under. 

The heuristic map is one of the most powerful ways to guide your optimizer. Experiment with different weights and heuristics.

## Constructing an Objective Function
The objective function lets you combine multiple objectives from your heuristic library to evaluate a single design. You weight objectives by their importance. You define an objective function similarly to building a heuristic map:

```Python
from heuristics.Objective_Function import Objective_Function
...
objective = design_heuristic_library.get_objective(Design.objective_method)
objective_function = Objective_Function()
objective_function.add_objective_by_weight(objective, 1.0)
```


## Constructing an Optimizer
Now that you have all the design specific features of your optimizer all you need to do is build an optimizer around them. To configure your optimizer you need to select a design selector, modifier selector, stopping criteria from the Optimism Library. You can reconfigure the default parameters of these functions using lambda functions. 

A basic optimizer is made and called like this:

```Python
from optimizer.Optimizer import Optimizer
from selector_functions.design_selectors.design_selectors import Highest_Scoring_Design
from selector_functions.modifier_selectors.modifier_selectors import Best_For_Lowest_Objective_Modifier
from stopping_criteria.stopping_criteria import stop_if_any_criteria_met, stop_at_threshold_score, stop_at_N_iterations
...
design_selector = Highest_Scoring_Design()
modifier_selector = Best_For_Lowest_Objective_Modifier()
stopping_criteria = stop_at_threshold_score
optimizer = Optimizer(design_selector, modifier_selector, stopping_criteria)
```

You run the optimizer with a specific heuristic map and objective function. It will return the set of designs generated from the whole process and from this you can collect the top scoring designs:

```Python
seeds = [...]
resulting_population = optimizer.optimize(objective_function, heuristic_map, seeds)
top_10_results = resulting_population.top_N_iterations(10)
```


