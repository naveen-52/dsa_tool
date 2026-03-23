import networkx as nx

def build_graph_from_matrix(matrix):

    num_vertices = len(matrix)

    G = nx.Graph()
    G.add_nodes_from(range(num_vertices))

    for i in range(num_vertices):
        for j in range(i + 1, num_vertices):
            if matrix[i][j] != 0:
                G.add_edge(i, j, weight=matrix[i][j])

    return G