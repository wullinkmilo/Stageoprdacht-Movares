import time
import math
import gurobipy as gp
from gurobipy import Model, GRB, quicksum
import matplotlib.pyplot as plt
import pprint

from A10_structure_data import structure_data


def set_year(assets, y_0):
    i = 0
    for asset in assets.values():
        for measure in asset.measures:
            i += 1
            measure.set_y_0(y_0)
            measure.set_penalty_values(measure.costs*100, 10, theta=measure.age)
    print(f"Imported {i} measures on {len(assets)} assets.")
    print(f"Model will contain {(T)*(T+1)*i} binary decision variables (for each directed arc).")

def CDF_reliability(asset, measure, time_since_last_measure, t):
    cdf = 1 - math.exp(-((time_since_last_measure) / measure.theta) ** measure.beta)
    age_factor = 1.05 ** (measure.age + t)  # Example age factor, can be adjusted based on requirements
    return cdf * age_factor

def run_model(assets, T):
    start = time.time()
    print("Running model...")


    # ------- DIRECTED GRAPH -------
    print("Creating directed graph...")

    # Create all nodes and arcs that can be visited in the flow network for each asset-measure combination.

    nodes = {}
    arcs = {}

    for asset in assets.values():
        for measure in asset.measures:
            key = (asset, measure)
            # print(f"Creating variables for {key}")
            nodes[key] = {(measure.tslm, measure.age)}

            for t in range(T):
                current_nodes = [(tslm, age) for tslm, age in nodes[key] if age == measure.age + t]

                for tslm, age in current_nodes:
                    cdf_value = CDF_reliability(asset, measure, tslm, t)

                    # Option 1: Perform the measure at year y_0 + t
                    nodes[key].add((0, age + 1))
                    arcs[key, (tslm, age), "Measure"] = {"from": (tslm, age), "to": (0, age + 1), "costs": measure.costs, "penalty": cdf_value * measure.penalty}

                    # Option 2: Do not perform the measure at year y_0 + t
                    nodes[key].add((tslm + 1, age + 1))

                    if t == T - 1:
                        arcs[key, (tslm, age), "No_Measure"] = {"from": (tslm, age), "to": (tslm + 1, age + 1), "costs": 0, "penalty": cdf_value * measure.penalty}
                    else:
                        arcs[key, (tslm, age), "No_Measure"] = {"from": (tslm, age), "to": (tslm + 1, age + 1), "costs": 0, "penalty": 0}

    # Incoming and outgoing mapping of graph
    incoming = {}
    outgoing = {}

    for arc in arcs:
        key, from_node, measure_taken = arc
        from_node = arcs[arc]["from"]
        to_node = arcs[arc]["to"]

        if key not in incoming:
            incoming[key] = {}
        if to_node not in incoming[key]:
            incoming[key][to_node] = []
        incoming[key][to_node].append(arc)

        if key not in outgoing:
            outgoing[key] = {}
        if from_node not in outgoing[key]:
            outgoing[key][from_node] = []
        outgoing[key][from_node].append(arc)

    end = time.time()
    print(f"Directed graph created after {end - start:.2f} seconds")


    # ------- INITIALIZATION -------
    print("Initializing optimization model...")

    m = Model("Bridge Maintenance Optimization")


    # ------- VARIABLES -------
    print("Creating decision variables...")

    # Decision variables for each arc in the flow network. Binary variable: 1 if the arc is chosen, 0 otherwise.
    ARCS = {}

    for arc in arcs:
        key, from_node, measure_taken = arc
        ARCS[arc] = m.addVar(vtype=GRB.BINARY, name=f"arc_({key[0]},{key[1]})_({from_node[0]},{from_node[1]})_{measure_taken}")
        # print first loop to see if it works

    print(len(ARCS), "decision variables created.")

    m.update()

    end = time.time()
    print(f"Decision variables created after {end - start:.2f} seconds")


    # ------- CONSTRAINTS -------
    print("Creating constraints...")

    # Source nodes have exactly one outgoing arc (either perform the measure or not).
    for asset in assets.values():
        for measure in asset.measures:
            key = (asset, measure)
            source_node = (measure.tslm, measure.age)
            m.addConstr(
                quicksum(ARCS[arc] for arc in outgoing[key][source_node]) == 1,
                name=f"source_constraint_({key[0]},{key[1]})"
            )

    # Flow conservation constraints
    for asset in assets.values():
        for measure in asset.measures:
            key = (asset, measure)

            for node in nodes[key]:
                if node == (measure.tslm, measure.age):  # Skip source node
                    continue
                if node[1] == measure.age + T:  # Skip terminal nodes
                    continue
                m.addConstr(
                        quicksum(ARCS[arc] for arc in incoming[key][node]) ==
                        quicksum(ARCS[arc] for arc in outgoing[key][node]),
                        name=f"flow_conservation_({key[0]},{key[1]})_({node[0]},{node[1]})"
                    )

    # Terminal node constraints should not be needed

    m.update()

    end = time.time()
    print(f"Constraints created after {end - start:.2f} seconds")


    # ------- OBJECTIVE FUNCTION -------
    print("Creating objective function...")

    maintenance_costs = quicksum(
        ARCS[arc] * arcs[arc]["costs"] for arc in arcs
    )
    penalty_costs = quicksum(
        ARCS[arc] * arcs[arc]["penalty"] for arc in arcs
    )

    m.setObjective(maintenance_costs + penalty_costs, GRB.MINIMIZE)

    end = time.time()
    print(f"Objective function created after {end - start:.2f} seconds")


    # ------- OPTIMIZATION -------
    print("Optimizing model...")

    m.write("bridge_maintenance.lp")

    m.optimize()

    m.write("bridge_maintenance.sol")

    results = {}
    chosen_arcs = []

    if m.status == GRB.OPTIMAL:
        end = time.time()
        print(f"Optimal solution found after {end - start:.2f} seconds")
        for arc in arcs:
            if ARCS[arc].X > 0.5:  # If the arc is chosen in the optimal solution
                # print(f"Chosen arc: {arc}, Value: {ARCS[arc].X}")
                chosen_arcs.append(arc)
                key, from_node, action = arc
                measure = key[1]
                age_at_measure = from_node[1]
                if action == "Measure":
                    results[(key[0], key[1],  measure.construction_year + age_at_measure)] = 1
                else:
                    results[(key[0], key[1],  measure.construction_year + age_at_measure)] = 0

    elif m.status == GRB.INFEASIBLE:
        print("Model is infeasible.")

    return results, chosen_arcs, arcs, nodes

def plot_route(chosen_arcs, arcs, nodes, asset, measure):
    # Plot nodes and arcs for a specific asset-measure combination.
    key = (asset, measure)

    plt.figure(figsize=(12, 7))
    for node in nodes[key]:
        plt.scatter(node[1], node[0], color='blue')
        # plt.text(node[0], node[1], f"({node[0]}, {node[1]})", fontsize=9, ha='right')

    for arc in arcs:
        if arc[0] == key:
            from_node = arcs[arc]["from"]
            to_node = arcs[arc]["to"]
            if not arc in chosen_arcs:  # Only plot chosen arcs
                plt.annotate(
                    '',
                    xy=(to_node[1], to_node[0]),
                    xytext=(from_node[1], from_node[0]),
                    arrowprops=dict(arrowstyle='->', color='lightgray', linestyle='--'),
                )
            else:
                plt.annotate(
                    '',
                    xy=(to_node[1], to_node[0]),
                    xytext=(from_node[1], from_node[0]),
                    arrowprops=dict(arrowstyle='->', color='green', linewidth=2),
                )


    plt.show()


def plot_schedule(results):
    # Make a plot of results. x-axis: years, y-axis: measures per asset.
    performed = [(asset, measure, year)
        for (asset, measure, year), value in results.items()
        if value == 1
    ]

    # Unique asset-measure combinations
    asset_measures = sorted(set(
        (asset.ID, measure.ID)
        for asset, measure, year in performed
    ))

    # Assign each asset-measure combination a y-position
    y_positions = {
        asset_measure: i
        for i, asset_measure in enumerate(asset_measures)
    }

    # Plot each performed measure as a square
    fig, ax = plt.subplots(figsize=(12, 7))

    for asset, measure, year in performed:
        y = y_positions[(asset.ID, measure.ID)]

        ax.scatter(
            year,
            y,
            marker="s",
            s=300,
            color="black"
        )

    # Y-axis labels
    ax.set_yticks(range(len(asset_measures)))
    ax.set_yticklabels([
        f"{asset_ID} - {measure_ID}"
        for asset_ID, measure_ID in asset_measures
    ])

    ax.set_xlabel("Year")
    ax.set_ylabel("Asset - Measure")

    ax.grid(axis="x", alpha=0.3)
    
    plt.show()

if __name__ == "__main__":

    print("Start running...")
    assets_json_file_path = r"C:\\Users\\milowullink\\OneDrive - Movares\\Documenten\\Stageopdracht Movares\\assets.json"
    dependencies_json_file_path = r"C:\\Users\\milowullink\\OneDrive - Movares\\Documenten\\Stageopdracht Movares\\dependencies.json"

    assets = structure_data(assets_json_file_path, dependencies_json_file_path)


    y_0 = 2026
    T = 150
    set_year(assets, y_0)

    results, chosen_arcs, arcs, nodes = run_model(assets, T)
    
    plot_schedule(results)

    # plot_route(chosen_arcs, arcs, nodes, assets[0], assets[0].measures[0])