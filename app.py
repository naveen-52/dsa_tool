"""
from flask import Flask, render_template, request
import matplotlib.pyplot as plt
import matplotlib
import networkx as nx
import itertools
import io
import base64
import heapq
import random
from collections import Counter

matplotlib.use('Agg')

app = Flask(__name__)

@app.context_processor
def utility_processor():
    return dict(chr=chr)


# ---------------- HOME ----------------

@app.route('/')
def index():
    stats = {
        "total_graphs": 24,
        "algorithms_used": 3,
        "sessions": 58
    }

    recent_activity = [
        "Ran Graph Coloring on 12 nodes",
        "Generated MST using Prim's algorithm",
        "Created Huffman tree for compression"
    ]

    return render_template(
        'home.html',
        stats=stats,
        recent_activity=recent_activity
    )


# ---------------- GRAPH COLORING ----------------

@app.route('/graph-coloring')
def graph_coloring_index():
    return render_template('graph_coloring/index.html')


@app.route('/graph-coloring/matrix', methods=['POST'])
def graph_coloring_matrix():
    num_vertices = int(request.form['num_vertices'])
    return render_template('graph_coloring/matrix.html', num_vertices=num_vertices)


@app.route('/graph-coloring/visualize', methods=['POST'])
def graph_coloring_visualize():

    num_vertices = int(request.form['num_vertices'])

    matrix = [
        [int(request.form[f'cell_{i}_{j}']) for j in range(num_vertices)]
        for i in range(num_vertices)
    ]

    G = nx.Graph()
    G.add_nodes_from(range(num_vertices))

    # FIXED EDGE CREATION
    for i in range(num_vertices):
        for j in range(i + 1, num_vertices):
            if matrix[i][j] == 1:
                G.add_edge(i, j)

    labels = {i: chr(65 + i) for i in range(num_vertices)}

    plt.figure(figsize=(6,6))
    pos = nx.circular_layout(G)

    nx.draw(
        G,
        pos,
        labels=labels,
        with_labels=True,
        node_color='skyblue',
        node_size=700,
        edge_color='gray'
    )

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()

    buf.seek(0)

    graph_url = base64.b64encode(buf.getvalue()).decode()

    return render_template(
        'graph_coloring/graph.html',
        graph_url=graph_url,
        num_vertices=num_vertices,
        matrix=matrix
    )


# ---------------- COLORING ALGORITHMS ----------------

def welsh_powell_vertex_coloring(G):

    coloring = {}

    nodes_sorted = sorted(
        G.nodes(),
        key=lambda node: G.degree(node),
        reverse=True
    )

    for node in nodes_sorted:

        used_colors = set(coloring.get(neigh) for neigh in G.neighbors(node))

        color = 0
        while color in used_colors:
            color += 1

        coloring[node] = color

    return coloring


def count_min_colorings(G, k, limit=100000):

    nodes = list(G.nodes())
    colors = list(range(k))
    assignment = {}
    count = 0

    def is_valid(node, color):
        return all(assignment.get(neigh) != color for neigh in G.neighbors(node))

    def backtrack(i):

        nonlocal count

        if count >= limit:
            return

        if i == len(nodes):

            if len(set(assignment.values())) == k:
                count += 1

            return

        node = nodes[i]

        for c in colors:

            if is_valid(node, c):

                assignment[node] = c
                backtrack(i + 1)
                del assignment[node]

    backtrack(0)

    return count, count >= limit


def greedy_edge_coloring(G):

    L = nx.line_graph(G)

    coloring = nx.coloring.greedy_color(
        L,
        strategy="largest_first"
    )

    return coloring


MAX_COLORINGS = 20


def greedy_coloring_with_order(G, order):

    coloring = {}

    for node in order:

        used = {coloring.get(n) for n in G.neighbors(node)}

        color = 0

        while color in used:
            color += 1

        coloring[node] = color

    return coloring


@app.route('/graph-coloring/chromatic', methods=['POST'])
def graph_coloring_chromatic():

    try:

        num_vertices = int(request.form['num_vertices'])

        matrix = [
            [int(request.form[f'cell_{i}_{j}']) for j in range(num_vertices)]
            for i in range(num_vertices)
        ]

        G = nx.Graph()
        G.add_nodes_from(range(num_vertices))

        for i in range(num_vertices):
            for j in range(i + 1, num_vertices):
                if matrix[i][j] == 1:
                    G.add_edge(i, j)

        pos = nx.circular_layout(G)
        labels = {i: chr(65 + i) for i in range(num_vertices)}

        base_coloring = welsh_powell_vertex_coloring(G)
        chromatic_number = max(base_coloring.values()) + 1

        if num_vertices > 11:
            total_colorings = 0
            truncated_flag = True
        else:
            total_colorings, truncated_flag = count_min_colorings(
                G,
                chromatic_number,
                limit=100000
            )

        vertex_palette = [
            'red','green','blue','yellow',
            'cyan','magenta','orange',
            'purple','pink','brown'
        ]

        def draw_vertex_graph(coloring):

            plt.figure(figsize=(6,6))

            node_colors = [
                vertex_palette[coloring[n] % len(vertex_palette)]
                for n in G.nodes()
            ]

            nx.draw(
                G,
                pos,
                labels=labels,
                with_labels=True,
                node_color=node_colors,
                node_size=700,
                edge_color='gray'
            )

            buf = io.BytesIO()

            plt.savefig(buf, format='png', bbox_inches='tight')
            plt.close()

            buf.seek(0)

            return base64.b64encode(buf.getvalue()).decode()

        graphs = []
        seen = set()

        base_nodes = list(G.nodes())

        for _ in range(100):

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

            if len(graphs) >= MAX_COLORINGS:
                break

        edge_coloring = greedy_edge_coloring(G)
        chromatic_index = max(edge_coloring.values()) + 1 if edge_coloring else 0

        edge_palette = [
            "red","green","blue","orange",
            "purple","cyan","magenta",
            "brown","pink","olive"
        ]

        edge_colors = [
            edge_palette[edge_coloring[e] % len(edge_palette)]
            for e in G.edges()
        ]

        plt.figure(figsize=(7,7))

        nx.draw_networkx_nodes(G, pos, node_color="skyblue", node_size=700)
        nx.draw_networkx_labels(G, pos, labels)

        nx.draw_networkx_edges(
            G,
            pos,
            edge_color=edge_colors,
            width=3
        )

        buf = io.BytesIO()

        plt.savefig(buf, format="png", bbox_inches="tight")
        plt.close()

        buf.seek(0)

        edge_graph_url = base64.b64encode(buf.getvalue()).decode()

        return render_template(
            "graph_coloring/chromatic_index.html",
            chromatic_index=chromatic_number,
            total_valid_colorings=total_colorings,
            coloring_count_truncated=truncated_flag,
            graphs=graphs,
            truncated=len(graphs) >= MAX_COLORINGS,
            edge_chromatic_index=chromatic_index,
            edge_graph_url=edge_graph_url
        )

    except Exception as e:
        print(f"Error: {e}")
        return str(e)


# ---------------- MANUAL COLORING ----------------

MAX_MANUAL_GRAPHS = 50


@app.route('/graph-coloring/manual', methods=['GET'])
def graph_coloring_manual():

    num_vertices = int(request.args['num_vertices'])

    matrix = [
        [int(request.args[f'cell_{i}_{j}']) for j in range(num_vertices)]
        for i in range(num_vertices)
    ]

    return render_template(
        'graph_coloring/manual_color.html',
        num_vertices=num_vertices,
        matrix=matrix
    )


@app.route('/graph-coloring/manual-process', methods=['POST'])
def graph_coloring_manual_process():

    try:

        num_vertices = int(request.form['num_vertices'])
        num_colors = int(request.form['num_colors'])

        matrix = [
            [int(request.form[f'cell_{i}_{j}']) for j in range(num_vertices)]
            for i in range(num_vertices)
        ]

        G = nx.Graph()
        G.add_nodes_from(range(num_vertices))

        for i in range(num_vertices):
            for j in range(i + 1, num_vertices):
                if matrix[i][j] == 1:
                    G.add_edge(i, j)

        vertex_coloring = welsh_powell_vertex_coloring(G)

        colors = [
            'red','green','blue','yellow',
            'cyan','magenta','orange',
            'purple','pink','brown'
        ]

        pos = nx.circular_layout(G)

        def draw_graph(color_mapping):

            labels = {i: chr(65 + i) for i in range(num_vertices)}

            plt.figure(figsize=(6,6))

            node_colors = [
                color_mapping[vertex_coloring[node]]
                for node in G.nodes()
            ]

            nx.draw(
                G,
                pos,
                labels=labels,
                with_labels=True,
                node_color=node_colors,
                node_size=700,
                edge_color='gray'
            )

            buf = io.BytesIO()

            plt.savefig(buf, format='png')
            plt.close()

            buf.seek(0)

            return base64.b64encode(buf.getvalue()).decode()

        color_combinations = []

        for i in range(0, num_colors - num_vertices + 1):

            start = i
            end = start + num_vertices

            color_combinations.extend(
                itertools.permutations(colors[start:end])
            )

        graphs = []

        for mapping in color_combinations:

            if len(graphs) >= MAX_MANUAL_GRAPHS:
                break

            color_map = {i: color for i, color in enumerate(mapping)}

            graphs.append(draw_graph(color_map))

        return render_template(
            'graph_coloring/manual_color_result.html',
            graphs=graphs
        )

    except Exception as e:
        print(f"Error: {e}")
        return str(e)


# ---------------- MST ----------------

# ---------------- MST ----------------

@app.route('/mst')
def mst_index():
    return render_template('mst/index.html')


@app.route('/mst/matrix', methods=['POST'])
def mst_matrix():

    num_vertices = int(request.form['num_vertices'])

    algorithm = request.form.get("algorithm", "prim")

    return render_template(
        'mst/matrix.html',
        num_vertices=num_vertices,
        algorithm=algorithm
    )


def validate_weight_matrix(matrix):

    n = len(matrix)

    for row in matrix:
        if len(row) != n:
            raise ValueError("Matrix must be square.")

    for i in range(n):
        for j in range(n):
            if matrix[i][j] != matrix[j][i]:
                raise ValueError("Matrix must be symmetric.")

    for i in range(n):
        for j in range(n):
            if matrix[i][j] < 0:
                raise ValueError("Negative weights are not allowed.")


# -------- PRIM'S ALGORITHM --------

def prims_mst(num_vertices, matrix):

    visited = set()
    mst_edges = []
    total_weight = 0

    adjacency = {i: [] for i in range(num_vertices)}

    for i in range(num_vertices):
        for j in range(num_vertices):
            if matrix[i][j] > 0:
                adjacency[i].append((j, matrix[i][j]))

    min_heap = [(0, 0, -1)]

    while min_heap and len(visited) < num_vertices:

        weight, current, parent = heapq.heappop(min_heap)

        if current in visited:
            continue

        visited.add(current)

        if parent != -1:
            mst_edges.append((parent, current, weight))
            total_weight += weight

        for neighbor, edge_weight in adjacency[current]:
            if neighbor not in visited:
                heapq.heappush(min_heap, (edge_weight, neighbor, current))

    if len(visited) != num_vertices:
        raise ValueError("Graph must be connected to compute MST.")

    return mst_edges, total_weight


# -------- KRUSKAL ALGORITHM --------

def kruskal_mst(num_vertices, matrix):

    parent = list(range(num_vertices))
    rank = [0] * num_vertices

    def find(node):
        if parent[node] != node:
            parent[node] = find(parent[node])
        return parent[node]

    def union(u, v):

        root_u = find(u)
        root_v = find(v)

        if root_u == root_v:
            return False

        if rank[root_u] < rank[root_v]:
            parent[root_u] = root_v

        elif rank[root_u] > rank[root_v]:
            parent[root_v] = root_u

        else:
            parent[root_v] = root_u
            rank[root_u] += 1

        return True

    edges = []

    for i in range(num_vertices):
        for j in range(i + 1, num_vertices):
            if matrix[i][j] > 0:
                edges.append((matrix[i][j], i, j))

    edges.sort()

    mst_edges = []
    total_weight = 0

    for weight, u, v in edges:

        if union(u, v):

            mst_edges.append((u, v, weight))
            total_weight += weight

        if len(mst_edges) == num_vertices - 1:
            break

    return mst_edges, total_weight


# -------- MST CALCULATION ROUTE --------

@app.route('/mst/calculate', methods=['POST'])
def mst_calculate():

    try:

        num_vertices = int(request.form.get('num_vertices', 0))
        algorithm = request.form.get("algorithm", "prim")

        matrix = []

        for i in range(num_vertices):

            row = []

            for j in range(num_vertices):

                value = request.form.get(f'cell_{i}_{j}')

                if value is None:
                    return f"Missing value for cell_{i}_{j}"

                row.append(int(value))

            matrix.append(row)

        validate_weight_matrix(matrix)

        G = nx.Graph()
        G.add_nodes_from(range(num_vertices))

        for i in range(num_vertices):
            for j in range(i + 1, num_vertices):

                if matrix[i][j] > 0:
                    G.add_edge(i, j, weight=matrix[i][j])

        if not nx.is_connected(G):
            return "Graph must be connected."

        # SELECT ALGORITHM

        if algorithm == "kruskal":
            mst_edges, total_weight = kruskal_mst(num_vertices, matrix)
        else:
            mst_edges, total_weight = prims_mst(num_vertices, matrix)

        pos = nx.circular_layout(G)

        labels = {i: chr(65 + i) for i in range(num_vertices)}

        plt.figure(figsize=(8, 8))

        mst_edge_list = [(u, v) for u, v, _ in mst_edges]

        nx.draw_networkx_nodes(G, pos, node_color='skyblue', node_size=700)
        nx.draw_networkx_labels(G, pos, labels)

        nx.draw_networkx_edges(G, pos, edge_color='gray', width=4, style='dashed')

        nx.draw_networkx_edges(
            G,
            pos,
            edgelist=mst_edge_list,
            edge_color='green',
            width=4
        )

        edge_labels = {(u, v): d["weight"] for u, v, d in G.edges(data=True)}

        nx.draw_networkx_edge_labels(
            G,
            pos,
            edge_labels=edge_labels,
            font_size=18,
            font_color="red",
            bbox=dict(facecolor="white", edgecolor="none")
        )

        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        plt.close()

        buf.seek(0)

        graph_url = base64.b64encode(buf.getvalue()).decode('utf8')

        return render_template(
            'mst/result.html',
            graph_url=graph_url,
            mst_edges=mst_edges,
            total_weight=total_weight,
            algorithm=algorithm
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        return str(e)

# ---------------- HUFFMAN ----------------

@app.route('/huffman')
def huffman_index():
    return render_template('huffman/index.html')


class HuffmanNode:

    def __init__(self,char,freq):

        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self,other):
        return self.freq < other.freq


def build_huffman_tree(text):

    frequency = Counter(text)

    heap = [
        HuffmanNode(char,freq)
        for char,freq in frequency.items()
    ]

    heapq.heapify(heap)

    while len(heap) > 1:

        left = heapq.heappop(heap)
        right = heapq.heappop(heap)

        merged = HuffmanNode(None,left.freq + right.freq)

        merged.left = left
        merged.right = right

        heapq.heappush(heap,merged)

    return heap[0]


def generate_huffman_codes(root,code="",codes=None):

    if codes is None:
        codes = {}

    if root.char is not None:

        codes[root.char] = code if code else "0"

        return codes

    generate_huffman_codes(root.left,code+"0",codes)
    generate_huffman_codes(root.right,code+"1",codes)

    return codes


@app.route('/huffman/encode', methods=['POST'])
def huffman_encode():

    text_input = request.form['text_input']

    frequency = Counter(text_input)

    root = build_huffman_tree(text_input)

    codes = generate_huffman_codes(root)

    return render_template(
        'huffman/result.html',
        original_text=text_input,
        huffman_codes=codes,
        frequencies=frequency.items()
    )


if __name__ == "__main__":
    app.run(debug=True) 
    """