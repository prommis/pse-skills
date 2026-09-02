"""
Template for creating a new IDAES/PrOMMiS/WaterTAP flowsheet.
"""

# Pyomo/IDAES imports
from pyomo.environ import (
    # Constraint,
    # Var,
    ConcreteModel,
    # Expression,
    # Objective,
    SolverFactory,
    TerminationCondition,
    TransformationFactory,
    value,
)
from pyomo.network import Arc, SequentialDecomposition
from idaes.core import FlowsheetBlock

# from idaes.core.scaling import AutoScaler, set_scaling_factor
from idaes.core.util.model_statistics import degrees_of_freedom
from idaes_fi.structfs.fsrunner import FlowsheetRunner, Context

# Optional phase functions below are reusable placeholders. The build skill
# decorates only the phases required by the requested flowsheet and derives
# their runner order from the selected models' verified dependencies.
FS = FlowsheetRunner(steps=("build",))


@FS.step("build")
def build_model(context: Context):
    """Create a model object which represents the problem to be solved.

    Args:
        context: Structured flowsheet context object with ".model" attribute
            to store the model.
    """
    m = ConcreteModel()
    m.fs = FlowsheetBlock(dynamic=False)
    add_property_packages(m)
    add_units(m)
    connect_units(m)
    context.model = m


def add_property_packages(m):
    """Add the property packages we intend to use to the flowsheet."""
    # e.g., m.fs.properties_1 = MyPropertyPackage.PhysicalParameterBlock()


def add_units(m):
    """Add unit models to represent each unit operation in the process."""
    # e.g., m.fs.unit01 = UnitModel(
    #     property_package=m.fs.properties_1
    # )


def connect_units(m):
    """Declare arcs connecting unit-operation ports."""
    # e.g., m.fs.arc_1 = Arc(
    #     source=m.fs.unit01.outlet,
    #     destination=m.fs.unit02.inlet,
    # )
    TransformationFactory("network.expand_arcs").apply_to(m)



def set_solver(context):
    """Set the optimization solver."""
    context.solver = SolverFactory("ipopt")



def set_operating_conditions(context):
    """Set variables corresponding to operating conditions."""
    m = context.model


def set_scaling(context):
    """Set manual scaling factors."""
    m = context.model



def solve_initial(context):
    """Perform the initial solve of the square model."""
    m = context.model
    results = context.solver.solve(m, tee=context["tee"])



def set_autoscaling(context):
    """Set automatic scaling factors."""
    m = context.model



def add_costing(context):
    """Add costing variables, if present."""
    m = context.model



def initialize_costing(context):
    """Initialize costing."""
    m = context.model



def setup_optimization(context):
    """Increase degrees of freedom and set the optimization objective."""
    m = context.model



def solve_optimization(context):
    """Solve the optimization problem."""
    m = context.model
    context.results = context.solver.solve(m, tee=context.tee)


if __name__ == "__main__":
    # Run all flowsheet steps in order.
    FS.run_steps()

    # Alternatively, run through a selected step:
    # FS.run_steps(last="solve_initial")