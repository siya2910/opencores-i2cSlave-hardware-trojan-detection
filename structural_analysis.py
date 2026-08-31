import json
import csv
from pathlib import Path
from collections import defaultdict


BASE_DIR = Path(__file__).resolve().parent
JSON_FILE = BASE_DIR / "results" / "i2cSlave_clean.json"
OUTPUT_FILE = BASE_DIR / "results" / "i2cSlave_structural_features.csv"


def load_design():
    with open(JSON_FILE, "r") as f:
        return json.load(f)


def get_top_module(data):
    modules = data.get("modules", {})

    if "i2cSlaveTop" in modules:
        return "i2cSlaveTop"

    # Fallback: identify the module with the fewest incoming references
    instantiated = set()

    for module in modules.values():
        for cell in module.get("cells", {}).values():
            cell_type = cell.get("type", "")
            if cell_type in modules:
                instantiated.add(cell_type)

    candidates = [
        name for name in modules
        if name not in instantiated
    ]

    if not candidates:
        raise ValueError("Could not identify top module.")

    return candidates[0]


def build_module_graph(data, module_name, prefix=""):
    """
    Build a structural graph from a Yosys module.

    Nodes represent instantiated cells.
    Edges represent signal connections between cells.
    Hierarchical modules are recursively expanded.
    """

    modules = data["modules"]
    module = modules[module_name]

    graph_nodes = set()
    graph_edges = set()

    cells = module.get("cells", {})

    # Map each net bit to its driving cell
    drivers = defaultdict(list)

    for cell_name, cell in cells.items():

        full_name = (
            f"{prefix}/{cell_name}"
            if prefix
            else cell_name
        )

        graph_nodes.add(full_name)

        cell_type = cell.get("type", "")

        # If this cell is another RTL module, recursively process it
        if cell_type in modules:
            sub_nodes, sub_edges = build_module_graph(
                data,
                cell_type,
                full_name
            )

            graph_nodes.update(sub_nodes)
            graph_edges.update(sub_edges)

        connections = cell.get("connections", {})

        # Determine output ports.
        # For standard Yosys cells, these are usually Y/Q/O/CO.
        output_ports = {
            "Y", "Q", "O", "CO", "COUT"
        }

        for port, bits in connections.items():

            if port in output_ports:

                for bit in bits:
                    drivers[bit].append(full_name)

    # Connect cells through common nets
    for cell_name, cell in cells.items():

        full_name = (
            f"{prefix}/{cell_name}"
            if prefix
            else cell_name
        )

        connections = cell.get("connections", {})

        for port, bits in connections.items():

            if port in {"Y", "Q", "O", "CO", "COUT"}:
                continue

            for bit in bits:

                for driver in drivers.get(bit, []):

                    if driver != full_name:
                        graph_edges.add(
                            (driver, full_name)
                        )

    return graph_nodes, graph_edges


def calculate_features(nodes, edges):

    node_count = len(nodes)
    edge_count = len(edges)

    # Degree dictionaries
    fan_in = {node: 0 for node in nodes}
    fan_out = {node: 0 for node in nodes}

    for source, target in edges:

        if source in fan_out:
            fan_out[source] += 1

        if target in fan_in:
            fan_in[target] += 1

    # Degree
    degree = {}

    for node in nodes:
        degree[node] = (
            fan_in[node] +
            fan_out[node]
        )

    # Average degree
    if node_count:
        average_degree = (
            sum(degree.values()) /
            node_count
        )
    else:
        average_degree = 0.0

    # Rare nodes:
    # nodes having very low connectivity
    rare_nodes = [
        node for node in nodes
        if degree[node] <= 1
    ]

    rare_node_count = len(rare_nodes)

    # Maximum fan-in/fan-out
    max_fan_in = max(
        fan_in.values(),
        default=0
    )

    max_fan_out = max(
        fan_out.values(),
        default=0
    )

    # Degree centrality approximation
    if node_count > 1:

        degree_centrality = {
            node:
            degree[node] / (node_count - 1)
            for node in nodes
        }

    else:

        degree_centrality = {
            node: 0.0
            for node in nodes
        }

    max_degree_centrality = max(
        degree_centrality.values(),
        default=0.0
    )

    # Normalized structural quantities
    # These bounds are used only to obtain a bounded
    # comparative score for this experiment.
    degree_norm = min(
        average_degree / 10.0,
        1.0
    )

    nodes_norm = min(
        node_count / 10000.0,
        1.0
    )

    edges_norm = min(
        edge_count / 20000.0,
        1.0
    )

    structural_score = (
        0.50 * degree_norm
        + 0.25 * nodes_norm
        + 0.25 * edges_norm
    )

    return {
        "Nodes": node_count,
        "Edges": edge_count,
        "AverageDegree": round(
            average_degree,
            4
        ),
        "RareNodeCount": rare_node_count,
        "FanInMax": max_fan_in,
        "FanOutMax": max_fan_out,
        "DegreeCentralityMax": round(
            max_degree_centrality,
            4
        ),
        "StructuralScore": round(
            structural_score,
            4
        )
    }


def save_features(features):

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        newline=""
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=features.keys()
        )

        writer.writeheader()
        writer.writerow(features)


def main():

    print("Loading:")
    print(JSON_FILE)

    data = load_design()

    top = get_top_module(data)

    print("\nTop module:")
    print(top)

    print("\nBuilding hierarchical circuit graph...")

    nodes, edges = build_module_graph(
        data,
        top
    )

    print("\nGraph Summary")
    print("-------------")
    print("Nodes:", len(nodes))
    print("Edges:", len(edges))

    features = calculate_features(
        nodes,
        edges
    )

    print("\nStructural Features")
    print("-------------------")

    for key, value in features.items():
        print(f"{key}: {value}")

    save_features(features)

    print("\nSaved:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()