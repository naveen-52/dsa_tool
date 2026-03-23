from flask import Blueprint, render_template, request, session
import networkx as nx

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import io
import base64
import random
import itertools

from app.services.graph_builder import build_graph_from_matrix

from app.algorithms.graph_coloring import (
    welsh_powell_vertex_coloring,
    greedy_edge_coloring,
    greedy_coloring_with_order,
    count_min_colorings
)

graph_bp = Blueprint("graph", __name__)

MAX_COLORINGS = 20
MAX_MANUAL_GRAPHS = 50


# ✅ HELPER (ADDED)
def get_graph_from_session():
    matrix = session.get("matrix")
    num_vertices = session.get("num_vertices")

    if not matrix:
        return None, None, None

    G = build_graph_from_matrix(matrix)
    return G, matrix, num_vertices


# ---------------- GRAPH COLORING HOME ----------------

@graph_bp.route("/graph-coloring")
def graph_coloring_index():
    return render_template("graph_coloring/index.html")


# ---------------- MATRIX INPUT ----------------

@graph_bp.route("/graph-coloring/matrix", methods=["POST"])
def graph_coloring_matrix():

    num_vertices = int(request.form["num_vertices"])

    return render_template(
        "graph_coloring/matrix.html",
        num_vertices=num_vertices
    )


# ---------------- GRAPH VISUALIZATION ----------------
@graph_bp.route("/graph-coloring/visualize", methods=["POST"])
def graph_coloring_visualize():

    num_vertices = int(request.form["num_vertices"])

    matrix = [
        [int(request.form[f"cell_{i}_{j}"]) for j in range(num_vertices)]
        for i in range(num_vertices)
    ]

    G = build_graph_from_matrix(matrix)

    # ✅ FIX: no fake edges
    if G.number_of_edges() == 0:
        return "Graph must have at least one edge", 400

    # ✅ SMART LABEL LOGIC
    if num_vertices <= 26:
        labels = {i: chr(65 + i) for i in range(num_vertices)}  # A-Z
    elif num_vertices <= 80:
        labels = {i: str(i+1) for i in range(num_vertices)}     # numbers
    else:
        labels = None

    # ✅ BETTER LAYOUT
    if num_vertices <= 50:
     pos = nx.spring_layout(G, seed=42, iterations=50)
    elif num_vertices <= 150:
     pos = nx.circular_layout(G)
    else:
     pos = nx.random_layout(G)
    # ✅ BIGGER CANVAS
    plt.figure(figsize=(10,10))

    # -------- DRAW NODES --------
    nx.draw_networkx_nodes(
        G,
        pos,
        node_color="skyblue",
        node_size=120 if num_vertices > 50 else 400
    )

    # -------- DRAW EDGES (FADED) --------
    nx.draw_networkx_edges(
    G,
    pos,
    edge_color="#000000",
    width=1.5,
    alpha=0.9
)

    # -------- DRAW LABELS (ONLY IF SMALL) --------
    if labels is not None and num_vertices <= 40:
        nx.draw_networkx_labels(G, pos, labels, font_size=8)

    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    plt.close()

    buf.seek(0)

    graph_url = base64.b64encode(buf.getvalue()).decode()

    # ✅ STORE ONCE
    session["matrix"] = matrix
    session["num_vertices"] = num_vertices

    return render_template(
        "graph_coloring/graph.html",
        graph_url=graph_url,
        num_vertices=num_vertices,
        matrix=matrix
    )
# ---------------- CHROMATIC NUMBER ----------------
@graph_bp.route("/graph-coloring/chromatic", methods=["POST"])
def graph_coloring_chromatic():

    # ✅ FIX: use session instead of form
    G, matrix, num_vertices = get_graph_from_session()

    if not G:
        return "No graph data found", 400

    max_colorings = 5 if num_vertices > 50 else MAX_COLORINGS

    if num_vertices <= 26:
        labels = {i: chr(65 + i) for i in range(num_vertices)}
    elif num_vertices <= 100:
        labels = {i: str(i+1) for i in range(num_vertices)}
    else:
        labels = None

    if num_vertices <= 50:
     pos = nx.spring_layout(G, seed=42, iterations=20)
    elif num_vertices <= 150:
     pos = nx.circular_layout(G)
    else:
     pos = nx.random_layout(G)

    base_coloring = welsh_powell_vertex_coloring(G)
    chromatic_number = max(base_coloring.values()) + 1

    if num_vertices > 15:
        total_colorings = 0
        truncated_flag = True
    else:
        total_colorings, truncated_flag = count_min_colorings(
            G,
            chromatic_number,
            limit=100000
        )

    vertex_palette = [
        "red","green","blue","yellow",
        "cyan","magenta","orange",
        "purple","pink","brown"
    ]

    # =========================================
    # VERTEX COLORING DRAW (UNCHANGED)
    # =========================================
    def draw_vertex_graph(coloring):

        if num_vertices > 60:
            fig_size = 14
            node_size = 500
            font_size = 7
            edge_alpha = 0.1
        elif num_vertices > 30:
            fig_size = 12
            node_size = 700
            font_size = 9
            edge_alpha = 0.15
        else:
            fig_size = 8
            node_size = 1000
            font_size = 12
            edge_alpha = 0.3

        plt.figure(figsize=(fig_size, fig_size))

        node_colors = [
            vertex_palette[coloring[n] % len(vertex_palette)]
            for n in G.nodes()
        ]

        nx.draw_networkx_nodes(
            G,
            pos,
            node_color=node_colors,
            node_size=node_size,
            edgecolors="black",
            linewidths=1.5
        )

        nx.draw_networkx_edges(
    G,
    pos,
    edge_color="#000000",   # 🔥 black
    width=1.2,              # thicker
    alpha=0.9               # visible
)

        if labels is not None and num_vertices <= 80:
            nx.draw_networkx_labels(
                G,
                pos,
                labels,
                font_size=font_size,
                font_weight="bold",
                font_color="black"
            )

        buf = io.BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight")
        plt.close()

        buf.seek(0)
        return base64.b64encode(buf.getvalue()).decode()

    # =========================================

    graphs = []
    seen = set()

    base_nodes = list(G.nodes())
    max_attempts = 5 if num_vertices > 50 else 100

    for _ in range(max_attempts):

        nodes = base_nodes[:]
        random.shuffle(nodes)

        coloring = greedy_coloring_with_order(G, nodes)

        if max(coloring.values()) + 1 != chromatic_number:
            continue

        signature = tuple(coloring[n] for n in sorted(coloring))

        if signature in seen:
            continue

        seen.add(signature)
        graphs.append(draw_vertex_graph(coloring))

        if len(graphs) >= max_colorings:
            break

    edge_coloring = greedy_edge_coloring(G)
    chromatic_index = max(edge_coloring.values()) + 1 if edge_coloring else 0

    edge_palette = [
        "red","green","blue","orange",
        "purple","cyan","magenta",
        "brown","pink","olive"
    ]

    edge_colors = [
        edge_palette[edge_coloring.get(e,0) % len(edge_palette)]
        for e in G.edges()
    ]

    # =========================================
    # 🔥 ONLY THIS PART MODIFIED (EDGE FIX)
    # =========================================

    if num_vertices > 60:
        fig_size = 14
        node_size = 500
    elif num_vertices > 30:
        fig_size = 12
        node_size = 700
    else:
        fig_size = 8
        node_size = 1000

    plt.figure(figsize=(fig_size, fig_size))

    nx.draw_networkx_nodes(
        G,
        pos,
        node_color="skyblue",
        node_size=node_size,
        edgecolors="black",
        linewidths=2   # 🔥 improved border
    )

    if labels is not None and num_vertices <= 80:
        nx.draw_networkx_labels(
            G,
            pos,
            labels,
            font_size=10,
            font_weight="bold"
        )

    # 🔥 EDGE IMPROVEMENT
    edge_width = 1.2 if num_vertices > 50 else 2.5

    nx.draw_networkx_edges(
    G,
    pos,
    edge_color=edge_colors,
    width=2.5,              # stronger
    alpha=1.0,              # no fade
    connectionstyle="arc3,rad=0.05"
)

    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    plt.close()

    buf.seek(0)
    edge_graph_url = base64.b64encode(buf.getvalue()).decode()

    # =========================================

    return render_template(
        "graph_coloring/chromatic_index.html",
        chromatic_index=chromatic_number,
        total_valid_colorings=total_colorings,
        coloring_count_truncated=truncated_flag,
        graphs=graphs,
        truncated=len(graphs) >= max_colorings,
        edge_chromatic_index=chromatic_index,
        edge_graph_url=edge_graph_url,
        matrix=matrix,
        num_vertices=num_vertices
    )
# ---------------- MANUAL COLORING ----------------

@graph_bp.route("/graph-coloring/manual", methods=["GET"])
def graph_coloring_manual():

    # ✅ FIX: use session
    G, matrix, num_vertices = get_graph_from_session()

    if not G:
        return "No graph data found", 400

    return render_template(
        "graph_coloring/manual_color.html",
        num_vertices=num_vertices,
        matrix=matrix
    )


@graph_bp.route("/graph-coloring/manual-process", methods=["POST"])
def graph_coloring_manual_process():

    # ✅ FIX: use session
    G, matrix, num_vertices = get_graph_from_session()

    if not G:
        return "No graph data found", 400

    num_colors = int(request.form["num_colors"])

    coloring = {}

    for i in range(num_vertices):
        color_value = request.form.get(f"color_{i}")
        if color_value is None:
            color_value = 0
        coloring[i] = int(color_value)

    valid = True

    for u, v in G.edges():
        if coloring[u] == coloring[v]:
            valid = False
            break

    palette = [
        "red","green","blue","yellow",
        "cyan","magenta","orange",
        "purple","pink","brown"
    ]

    pos = nx.spring_layout(G, seed=42)

    node_colors = [
        palette[(coloring[n]-1) % len(palette)] if coloring[n] > 0 else "gray"
        for n in G.nodes()
    ]

    # ===============================
    # 🔥 IMPROVED DRAWING (FINAL FIX)
    # ===============================

    if num_vertices > 60:
        fig_size = 14
        node_size = 500
        font_size = 7
        edge_alpha = 0.1
    elif num_vertices > 30:
        fig_size = 12
        node_size = 700
        font_size = 9
        edge_alpha = 0.15
    else:
        fig_size = 8
        node_size = 1000
        font_size = 12
        edge_alpha = 0.3

    plt.figure(figsize=(fig_size, fig_size))

    # -------- NODES --------
    nx.draw_networkx_nodes(
        G,
        pos,
        node_color=node_colors,
        node_size=node_size,
        edgecolors="black",
        linewidths=1.5
    )

    # -------- EDGES (FADED HARD) --------
    nx.draw_networkx_edges(
    G,
    pos,
    edge_color="#000000",
    width=1.3,
    alpha=0.85
)

    # -------- LABELS --------
    if num_vertices <= 80:
        nx.draw_networkx_labels(
            G,
            pos,
            font_size=font_size,
            font_weight="bold",
            font_color="black"
        )

    # ===============================

    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    plt.close()

    buf.seek(0)

    graph_img = base64.b64encode(buf.getvalue()).decode()

    return render_template(
        "graph_coloring/manual_color_result.html",
        graph=graph_img,
        valid=valid,
        num_colors=num_colors,
        num_vertices=num_vertices,
        matrix=matrix
    )
@graph_bp.route("/graph-coloring/graph")
def graph_from_session():

    G, matrix, num_vertices = get_graph_from_session()

    if not G:
        return "No graph data found", 400

    pos = nx.spring_layout(G, seed=42)

    plt.figure(figsize=(6,6))

    nx.draw(
        G,
        pos,
        node_color="skyblue",
        with_labels=True
    )

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close()

    buf.seek(0)

    graph_url = base64.b64encode(buf.getvalue()).decode()

    return render_template(
        "graph_coloring/graph.html",
        graph_url=graph_url,
        num_vertices=num_vertices,
        matrix=matrix
    )