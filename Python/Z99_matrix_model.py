import time
import math
import gurobipy as gp
from gurobipy import Model, GRB, quicksum
import matplotlib.pyplot as plt
import pprint

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
                {"name": "Action 3", "costs": 3000, "penalty": 30_000,
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

def structure_data(bridges):
    # Transform database to Asset and Action objects
    structured_bridges = [
        Asset(
            bridge["name"],
            actions=[Action(**action) for action in bridge["actions"]],
            construction_year=bridge["construction_year"],
        )
        for bridge in bridges
    ]
    return structured_bridges

def CDF_reliability(bridge, action, time_since_last_action):
    return 1 - math.exp(-((time_since_last_action) / action.theta) ** action.beta)

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
                            pdf_values[bridge.name, action.name, year, last_year] = CDF_reliability(bridge, action, year - last_year)
    end = time.time()
    print(f"Pre-calculation of PDF values took {end - start:.2f} seconds")
    return pdf_values

def run_model(bridges, y_0, T):
    start = time.time()
    m = Model("Bridge Maintenance Optimization")

    # ------- VARIABLES -------
    years_of_actions_before_y_0 = {action.y_of_last_action_input for bridge in bridges for action in bridge.actions}
    possible_last_action_years = sorted(
        years_of_actions_before_y_0
        | set(range(y_0, y_0 + T))
    )
    print(f"Possible last action years: {possible_last_action_years}")

    # Create binary decision variables for each bridge, action, and year
    BIN_bridge_action_year = {}
    for bridge in bridges:
        for action in bridge.actions:
            for year in possible_last_action_years:
                BIN_bridge_action_year[bridge.name, action.name, year] = m.addVar(
                    vtype=GRB.BINARY,
                    name=f"BIN_{bridge.name}_{action.name}_{year}",
                )

    # Create binary decision variables for each bridge, action, year and the last action year
    BIN_bridge_action_year_last_year = {}
    for bridge in bridges:
        for action in bridge.actions:
            for year in range(y_0, y_0 + T):
                for last_year in possible_last_action_years:
                    if last_year < year:
                        BIN_bridge_action_year_last_year[bridge.name, action.name, year, last_year] = m.addVar(
                            vtype=GRB.BINARY,
                            name=f"BIN_{bridge.name}_{action.name}_{year}_last_{last_year}",
                        )

    # ------ CONSTRAINTS -------

    # Set the binary values for when the last maintenance was preformed based on the input data and make sure maintenance is performed on the last maintenance year.
    for bridge in bridges:
        for action in bridge.actions:
            for year in years_of_actions_before_y_0:
                if year == action.y_of_last_action_input:
                    m.addConstr(
                        BIN_bridge_action_year[bridge.name, action.name, action.y_of_last_action_input] == 1,
                        name=f"LastActionInput_{bridge.name}_{action.name}"
                    )
                else:
                    m.addConstr(
                        BIN_bridge_action_year[bridge.name, action.name, year] == 0,
                        name=f"LastActionInput_{bridge.name}_{action.name}_{year}"
                    )
            m.addConstr(
                BIN_bridge_action_year[bridge.name, action.name, y_0 + T - 1] == 1,
                name=f"LastActionInput_{bridge.name}_{action.name}_{y_0 + T - 1}"
            )

    # Add constraints to connect these binary variables.
    for bridge in bridges:
        for action in bridge.actions:
            for year in range(y_0, y_0 + T):
                # The sum of the last action year selectors must equal the action decision variable for that year.
                m.addConstr(quicksum(
                    BIN_bridge_action_year_last_year[bridge.name, action.name, year, last_year]
                    for last_year in possible_last_action_years
                    if last_year < year
                ) == BIN_bridge_action_year[bridge.name, action.name, year])
                for last_year in possible_last_action_years:
                    if last_year < year:
                        # Ensure that if a last action year is selected, the corresponding action must have been performed in that year.
                        m.addConstr(BIN_bridge_action_year[bridge.name, action.name, last_year] >= BIN_bridge_action_year_last_year[bridge.name, action.name, year, last_year])
                        m.addConstr(BIN_bridge_action_year[bridge.name, action.name, year] >= BIN_bridge_action_year_last_year[bridge.name, action.name, year, last_year])

    # ------ OBJECTIVE FUNCTION -------
    # The objective is to minimize the total costs, which include the action costs and the penalty costs based on the Weibull CDF.
    action_costs = quicksum(
        action.costs * BIN_bridge_action_year[bridge.name, action.name, year]
        for bridge in bridges
        for action in bridge.actions
        for year in range(y_0, y_0 + T)
    )

    penalty_costs = quicksum(
        action.penalty * pdf_values[bridge.name, action.name, year, last_year] * BIN_bridge_action_year_last_year[bridge.name, action.name, year, last_year]
        for bridge in bridges
        for action in bridge.actions
        for year in range(y_0, y_0 + T)
        for last_year in possible_last_action_years
        if last_year < year
    )

    m.setObjective(action_costs + penalty_costs, GRB.MINIMIZE)

    m.write("bridge_maintenance.lp")

    m.optimize()
    
    end = time.time()
    print(f"Optimization time: {end - start:.2f} seconds")

    results = {}

    if m.status == GRB.OPTIMAL:
        print("Optimal solution found:")
        for bridge in bridges:
            for action in bridge.actions:
                for year in possible_last_action_years:
                    if BIN_bridge_action_year[bridge.name, action.name, year].x > 0.5:
                        print(f"Perform {action.name} on {bridge.name} in year {year}")
                        results[(bridge.name, action.name, year)] = 1
                    else:
                        results[(bridge.name, action.name, year)] = 0
                    for last_year in possible_last_action_years:
                        if last_year < year and year >= y_0:
                            if BIN_bridge_action_year_last_year[bridge.name, action.name, year, last_year].x > 0.5:
                                print(f"Last action for {action.name} on {bridge.name} before year {year} was in year {last_year}")

    print("Total action costs:", action_costs.getValue())
    print("Total penalty costs:", penalty_costs.getValue())

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
    print(gp.gurobi.version())
    bridges = structure_data(import_data())
    y_0 = 2026
    T = 10
    pdf_values = precalculate_PDF_values(bridges, y_0, T)
    results = run_model(bridges, y_0, T)
    visualize_results(results)