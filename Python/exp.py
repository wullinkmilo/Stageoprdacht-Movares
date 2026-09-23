# Simplified version of model
import time
import math
from turtle import st
import gurobipy as gp
from gurobipy import Model, GRB, quicksum
import matplotlib.pyplot as plt

class Asset:
    def __init__(self, name, actions, construction_year):
        self.name = name
        self.actions = actions
        self.construction_year = construction_year

class Action:
    def __init__(self, name, costs, penalty, y_of_last_action_input, beta, theta):
        self.name = name
        self.costs = costs
        self.penalty = penalty
        self.y_of_last_action_input = y_of_last_action_input
        self.beta = beta
        self.theta = theta

def import_data():
    bridges = [
        {
            "name": "Bridge 1",
            "construction_year": 2000,
            "actions": [
                {"name": "Action 1", "costs": 1000, "penalty": 10_000,
                "y_of_last_action_input": 2020, "beta": 10, "theta": 10},
                {"name": "Action 2", "costs": 2000, "penalty": 20_000,
                "y_of_last_action_input": 2018, "beta": 5, "theta": 15},
                {"name": "Action 3", "costs": 3000, "penalty": 300000_000,
                "y_of_last_action_input": 2015, "beta": 2, "theta": 20},
            ],
        },
        {
            "name": "Bridge 2",
            "construction_year": 2010,      
            "actions": [
                {"name": "Action 1", "costs": 1200, "penalty": 12_000,
                "y_of_last_action_input": 2022, "beta": 8, "theta": 12},
                {"name": "Action 2", "costs": 2000, "penalty": 20_000,
                "y_of_last_action_input": 2019, "beta": 4, "theta": 18},
            ],
        },
    ]
    return bridges


def generate_actions(actions):
    """Create a separate Action object for every bridge-specific definition."""
    return [Action(**action) for action in actions]

def structure_data(bridges):
    # Transform database to Asset and Action objects
    structured_bridges = [
        Asset(
            bridge["name"],
            actions=generate_actions(bridge["actions"]),
            construction_year=bridge["construction_year"],
        )
        for bridge in bridges
    ]
    return structured_bridges

# Calculate optimal time for next action based on reliability function

def PDF_reliability(bridge, action, years_between_actions):
    # Calculate PDF reliability based on the Weibull distribution
    return (action.beta / action.theta) * ((years_between_actions / action.theta) ** (action.beta - 1)) * math.exp(-((years_between_actions / action.theta) ** action.beta))

def CDF_reliability(bridge, action, years_between_actions):
    # Calculate CDF reliability based on the Weibull distribution
    return 1 - math.exp(-((years_between_actions / action.theta) ** action.beta))

def precalculate_PDF_values(bridges, y_0, T):
    # Pre-calculate PDF values for all bridges, actions, and years to avoid repeated calculations in the optimization model.
    start = time.time()
    possible_last_action_years = sorted(
        {action.y_of_last_action_input for bridge in bridges for action in bridge.actions}
        | set(range(y_0, y_0 + T))
    )
    pdf_values = {}
    for bridge in bridges:
        for action in bridge.actions:
            for year in range(y_0, y_0 + T):
                for last_year in possible_last_action_years:
                        if last_year <= year:
                            pdf_values[bridge.name, action.name, year, last_year] = PDF_reliability(bridge, action, year - last_year)
    end = time.time()
    print(f"Pre-calculation of PDF values took {end - start:.2f} seconds")
    return pdf_values

# Build an optimization model to determine the optimal actions at what times.

def run_model(bridges, y_0, T, pdf_values):
    start = time.time()

    m = gp.Model("Asset Management Optimization")

    # Variables: binary decision variables for each action on each bridge in each year
    bridge_action_year = {}
    for bridge in bridges:
        for action in bridge.actions:
            for year in range(y_0, y_0 + T):
                bridge_action_year[bridge.name, action.name, year] = m.addVar(
                    vtype=GRB.BINARY,
                    name=f"{bridge.name}_{action.name}_{year}",
                )


    # Variables: y_action for each action on each bridge (last year the action was performed)
    y_of_last_action = {}
    for bridge in bridges:
        for action in bridge.actions:
            for year in range(y_0, y_0 + T):
                y_of_last_action[bridge.name, action.name, year] = m.addVar(
                    vtype=GRB.INTEGER,
                    lb=0,
                    ub=y_0 + T,
                    name=f"{bridge.name}_{action.name}_y_of_last_action_{year}",
                )

    # Binary selectors linearize the lookup of the Weibull CDF.  The last
    # action year can only be the input year or one of the planning years.
    last_action_selectors = {}
    possible_last_action_years = sorted(
        {action.y_of_last_action_input for bridge in bridges for action in bridge.actions}
        | set(range(y_0, y_0 + T))
    )
    for bridge in bridges:
        for action in bridge.actions:
            for year in range(y_0, y_0 + T):
                for last_year in possible_last_action_years:
                    last_action_selectors[bridge.name, action.name, year, last_year] = m.addVar(
                        vtype=GRB.BINARY,
                        name=f"{bridge.name}_{action.name}_{year}_last_{last_year}",
                    )

    m.update()

    # Constraints: If an action is performed, the y_of_last_action should be updated to y_0 + t.
    # for bridge in bridges:
    #     for action in bridge.actions:
    #         for i, year in enumerate(range(y_0, y_0 + T)):
    #             if i == 0:
    #                 m.addConstr(y_of_last_action[bridge.name, action.name, year] == action.y_of_last_action_input)
    #             else:
    #                 x = bridge_action_year[bridge.name, action.name, year]

    #                 set_var = y_of_last_action[bridge.name, action.name, year]
    #                 previous_last = y_of_last_action[bridge.name, action.name, year - 1]

    #                 # Maintenance happens now
    #                 m.addConstr(
    #                     (x == 1) >> (set_var == year)
    #                 )

    #                 # No maintenance -> carry previous value forward
    #                 m.addConstr(
    #                     (x == 0) >> (set_var == previous_last)
    #                 )

    # Select exactly one possible last-action year.  This makes the penalty
    # lookup linear rather than using exp() in the objective.
    for bridge in bridges:
        for action in bridge.actions:
            for year in range(y_0, y_0 + T):
                selectors = [
                    last_action_selectors[bridge.name, action.name, year, last_year]
                    for last_year in possible_last_action_years
                    if last_year < year  # Only years prior to the current year can be selected as the last action year
                ]
                m.addConstr(quicksum(selectors) == bridge_action_year[bridge.name, action.name, year])

    # Ensure that the last action year is consistent with the y_of_last_action variable
    # Last action selector 2030, 2025 means binary should be 1 for 2025 and 2030 and zero for all binaries in between.
    for bridge in bridges:
        for action in bridge.actions:
            m.addConstr(bridge_action_year[bridge.name, action.name, y_0 + T - 1] == 1)  # Action must be performed by the end of the planning horizon
            for year in range(y_0, y_0 + T):
                m.addConstr(bridge_action_year[bridge.name, action.name, year] >= quicksum(last_action_selectors[bridge.name, action.name, year, last_year] for last_year in possible_last_action_years if last_year < year))
                m.addConstr(bridge_action_year[bridge.name, action.name, last_year] >= quicksum(last_action_selectors[bridge.name, action.name, year, last_year] for year in range(y_0, y_0 + T) if year > last_year))

    m.update()

    # Objective: Minimize total costs
    
    # Action costs
    action_costs = quicksum(
        action.costs * bridge_action_year[bridge.name, action.name, year]
        for bridge in bridges
        for action in bridge.actions
        for year in range(y_0, y_0 + T)
    )

    # Penalty costs. The CDF values are constants selected by binary
    # variables, so the objective is linear.
    penalty_costs = quicksum(
        action.penalty
        * pdf_values[
            bridge.name,
            action.name,
            year,
            last_year
        ]
        * last_action_selectors[
            bridge.name,
            action.name,
            year,
            last_year
        ]
        for bridge in bridges
        for action in bridge.actions
        for year in range(y_0, y_0 + T)
        for last_year in possible_last_action_years
        if last_year <= year
    )

    m.setObjective(action_costs + penalty_costs, GRB.MINIMIZE)

    m.update()

    m.write("simple.lp")  # Write the model to a file for inspection

    m.optimize()

    end = time.time()
    print(f"Optimization time: {end - start:.2f} seconds")

    results = {}

    if m.status == GRB.OPTIMAL:
        print("Optimal solution found:")
        for bridge in bridges:
            for action in bridge.actions:
                for year in range(y_0, y_0 + T):
                    if bridge_action_year[bridge.name, action.name, year].x > 0.5:
                        print(f"Perform {action.name} on {bridge.name} in year {year}")
                        results[(bridge.name, action.name, year)] = 1
                    else:
                        results[(bridge.name, action.name, year)] = 0

                    if y_of_last_action[bridge.name, action.name, year].x > 0.5:
                        print(f"Year of last action for {action.name} on {bridge.name} in year {year}: {y_of_last_action[bridge.name, action.name, year].x}")

                    for last_year in possible_last_action_years:
                        if last_action_selectors[bridge.name, action.name, year, last_year].x > 0.5:
                            print(f"Last action year for {action.name} on {bridge.name} in year {year}: {last_year}")

    return results


def visualize_results(results):
    # Make a plot of results. x-axis: years, y-axis: actions per bridge.
    performed = [(bridge, action, year)
        for (bridge, action, year), value in results.items()
        if value == 1
    ]

    # Unique bridge-action combinations
    bridge_actions = sorted(set(
        (bridge, action)
        for bridge, action, year in performed
    ))

    # Assign each bridge-action combination a y-position
    y_positions = {
        bridge_action: i
        for i, bridge_action in enumerate(bridge_actions)
    }

    # Plot each performed action as a square
    fig, ax = plt.subplots(figsize=(12, 7))

    for bridge, action, year in performed:
        y = y_positions[(bridge, action)]

        ax.scatter(
            year,
            y,
            marker="s",
            s=300,
            color="black"
        )

    # Y-axis labels
    ax.set_yticks(range(len(bridge_actions)))
    ax.set_yticklabels([
        f"{bridge} - {action}"
        for bridge, action in bridge_actions
    ])

    ax.set_xlabel("Year")
    ax.set_ylabel("Bridge - Action")

    ax.grid(axis="x", alpha=0.3)
    
    plt.show()


if __name__ == "__main__":
    bridges = structure_data(import_data())
    y_0 = 2026
    T = 150
    pdf_values = precalculate_PDF_values(bridges, y_0, T)
    results = run_model(bridges, y_0, T, pdf_values)
    visualize_results(results)
