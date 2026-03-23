import heapq

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

    return mst_edges, total_weight



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