from flask import Blueprint, render_template, request
import networkx as nx

# 🔥 REQUIRED for server-side rendering
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import io
import base64

from app.algorithms.mst import prims_mst, kruskal_mst
from app.utils.validators import validate_weight_matrix

mst_bp = Blueprint("mst", __name__)


@mst_bp.route("/mst")
def mst_index():
    return render_template("mst/index.html")


@mst_bp.route("/mst/matrix", methods=["POST"])
def mst_matrix():

    num_vertices = int(request.form["num_vertices"])
    algorithm = request.form.get("algorithm", "prim")

    return render_template(
        "mst/matrix.html",
        num_vertices=num_vertices,
        algorithm=algorithm
    )


# 🔥 Build full graph
def build_full_graph(matrix):
    G = nx.Graph()
    num_vertices = len(matrix)

    G.add_nodes_from(range(num_vertices))

    for i in range(num_vertices):
        for j in range(i + 1, num_vertices):
            if matrix[i][j] != 0:
                G.add_edge(i, j, weight=matrix[i][j])

    return G


# 🔥 UPDATED: supports animation steps
def generate_graph_image(G, step):

    if len(G.edges()) == 0:
        return None

    mst_edges = step["edges"]
    current_node = step["current"]

    # Layout
    if len(G.nodes()) <= 6:
     pos = nx.circular_layout(G)
    else:
     pos = nx.spring_layout(G, seed=42)

    # 🔥 CENTER GRAPH PROPERLY
    x_vals = [v[0] for v in pos.values()]
    y_vals = [v[1] for v in pos.values()]

    x_center = (max(x_vals) + min(x_vals)) / 2
    y_center = (max(y_vals) + min(y_vals)) / 2

    pos = {
        k: (v[0] - x_center, v[1] - y_center)
        for k, v in pos.items()
    }


    plt.figure(figsize=(6, 6))
    plt.margins(0.2)
    plt.axis('off')

    # Convert MST edges
    mst_set = set((min(u, v), max(u, v)) for u, v, _ in mst_edges)

    mst_edge_list = []
    non_mst_edges = []

    for u, v in G.edges():
        if (min(u, v), max(u, v)) in mst_set:
            mst_edge_list.append((u, v))
        else:
            non_mst_edges.append((u, v))

    # 🔥 Node coloring (highlight current)
    node_colors = []
    for node in G.nodes():
        if node == current_node:
            node_colors.append("red")
        else:
            node_colors.append("#93c5fd")

    nx.draw_networkx_nodes(
        G, pos,
        node_color=node_colors,
        node_size=900,
        edgecolors="black"
    )

    # Non-MST edges
    nx.draw_networkx_edges(
        G, pos,
        edgelist=non_mst_edges,
        edge_color="lightgray",
        width=1,
        alpha=0.4,
        connectionstyle="arc3,rad=0.2"
    )

    # MST edges
    nx.draw_networkx_edges(
        G, pos,
        edgelist=mst_edge_list,
        edge_color="#16a34a",
        width=4
    )

    # Labels
    nx.draw_networkx_labels(G, pos)

    # Edge labels
    mst_labels = {}
    non_mst_labels = {}

    for u, v, w in mst_edges:
        mst_labels[(u, v)] = w

    for u, v in non_mst_edges:
        if G.has_edge(u, v):
            non_mst_labels[(u, v)] = G[u][v]['weight']

    nx.draw_networkx_edge_labels(
        G, pos,
        edge_labels=non_mst_labels,
        font_size=8,
        font_color="gray",
        bbox=dict(facecolor='white', edgecolor='none', alpha=0.6)
    )

    nx.draw_networkx_edge_labels(
        G, pos,
        edge_labels=mst_labels,
        font_size=10,
        font_color="black",
        bbox=dict(facecolor='white', edgecolor='none', alpha=0.9)
    )

    # Save image
    img = io.BytesIO()
    plt.savefig(img, format="png", bbox_inches='tight')
    plt.close()

    img.seek(0)
    return base64.b64encode(img.read()).decode('utf-8')


@mst_bp.route("/mst/calculate", methods=["POST"])
def mst_calculate():

    num_vertices = int(request.form.get("num_vertices", 0))
    algorithm = request.form.get("algorithm", "prim")

    matrix = []

    for i in range(num_vertices):
        row = []
        for j in range(num_vertices):
            value = request.form.get(f"cell_{i}_{j}")
            row.append(int(value) if value else 0)

        matrix.append(row)

    validate_weight_matrix(matrix)

    # 🔥 UPDATED: get steps also
    if algorithm == "kruskal":
        mst_edges, total_weight, steps = kruskal_mst(num_vertices, matrix)
    else:
        mst_edges, total_weight, steps = prims_mst(num_vertices, matrix)

    G = build_full_graph(matrix)

    # 🔥 Final static graph (no highlight)
    graph_image = generate_graph_image(G, {
        "edges": mst_edges,
        "current": -1
    })

    # 🔥 Generate animation frames
    step_images = []
    for step in steps:
        img = generate_graph_image(G, step)
        step_images.append(img)

    return render_template(
        "mst/result.html",
        mst_edges=mst_edges,
        total_weight=total_weight,
        algorithm=algorithm,
        graph_image=graph_image,
        step_images=step_images   # 🔥 NEW
    )