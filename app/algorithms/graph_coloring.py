import networkx as nx


def welsh_powell_vertex_coloring(G):

    coloring = {}

    nodes_sorted = sorted(
        G.nodes(),
        key=lambda node: G.degree(node),
        reverse=True
    )

    for node in nodes_sorted:

        used_colors = {
            coloring[neigh]
            for neigh in G.neighbors(node)
            if neigh in coloring
        }

        color = 0

        while color in used_colors:
            color += 1

        coloring[node] = color

    return coloring


def greedy_edge_coloring(G):

    L = nx.line_graph(G)

    coloring = nx.coloring.greedy_color(
        L,
        strategy="largest_first"
    )

    return coloring


def greedy_coloring_with_order(G, order):

    coloring = {}

    for node in order:

        used = {
            coloring[n]
            for n in G.neighbors(node)
            if n in coloring
        }

        color = 0

        while color in used:
            color += 1

        coloring[node] = color

    return coloring


def count_min_colorings(G, k, limit=100000):

    nodes = list(G.nodes())
    colors = list(range(k))

    assignment = {}
    count = 0

    def is_valid(node, color):

        return all(
            assignment.get(neigh) != color
            for neigh in G.neighbors(node)
        )

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