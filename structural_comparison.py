import csv
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "results"

CLEAN_FILE = RESULTS_DIR / "i2cSlave_clean_structural_features.csv"
TROJAN_FILE = RESULTS_DIR / "i2cSlave_trojan_structural_features.csv"


def read_features(filename):
    with open(filename, "r", newline="") as f:
        return next(csv.DictReader(f))


def main():

    clean = read_features(CLEAN_FILE)
    trojan = read_features(TROJAN_FILE)

    clean_nodes = int(clean["Nodes"])
    trojan_nodes = int(trojan["Nodes"])

    clean_edges = int(clean["Edges"])
    trojan_edges = int(trojan["Edges"])

    clean_degree = float(clean["AverageDegree"])
    trojan_degree = float(trojan["AverageDegree"])

    delta_nodes = trojan_nodes - clean_nodes
    delta_edges = trojan_edges - clean_edges
    delta_degree = trojan_degree - clean_degree

    node_change = (
        delta_nodes / clean_nodes
        if clean_nodes else 0
    )

    edge_change = (
        delta_edges / clean_edges
        if clean_edges else 0
    )

    structural_delta_score = (
        0.5 * min(abs(node_change), 1.0)
        + 0.5 * min(abs(edge_change), 1.0)
    )

    print("\nStructural Comparison")
    print("---------------------")

    print("Clean Nodes       :", clean_nodes)
    print("Trojan Nodes      :", trojan_nodes)
    print("Delta Nodes       :", delta_nodes)

    print("Clean Edges       :", clean_edges)
    print("Trojan Edges      :", trojan_edges)
    print("Delta Edges       :", delta_edges)

    print("Clean Avg Degree  :", clean_degree)
    print("Trojan Avg Degree :", trojan_degree)
    print("Delta Avg Degree  :", round(delta_degree, 4))

    print(
        "Node Change       :",
        round(node_change, 4)
    )

    print(
        "Edge Change       :",
        round(edge_change, 4)
    )

    print(
        "Structural Delta  :",
        round(structural_delta_score, 4)
    )


if __name__ == "__main__":
    main()\
        
        