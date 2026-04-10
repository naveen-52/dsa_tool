import heapq


# 🔥 PRIM'S MST WITH STEP TRACKING
def prims_mst(num_vertices, matrix):

    visited = set()
    mst_edges = []
    steps = []   # ✅ UPDATED: store detailed steps
    total_weight = 0

    # Build adjacency list
    adjacency = {i: [] for i in range(num_vertices)}

    for i in range(num_vertices):
        for j in range(num_vertices):
            if matrix[i][j] > 0:
                adjacency[i].append((j, matrix[i][j]))

    # Min heap: (weight, current_node, parent)
    min_heap = [(0, 0, -1)]

    while min_heap and len(visited) < num_vertices:

        weight, current, parent = heapq.heappop(min_heap)

        if current in visited:
            continue

        visited.add(current)
        
        # 🔥 ADD INITIAL STEP (ONLY START NODE)
        if parent == -1:
         steps.append({
         "edges": [],
         "current": current
    })

        if parent != -1:
            mst_edges.append((parent, current, weight))
            total_weight += weight

            # 🔥 UPDATED STEP STRUCTURE
            steps.append({
                "edges": list(mst_edges),
                "current": current
            })

        for neighbor, edge_weight in adjacency[current]:
            if neighbor not in visited:
                heapq.heappush(min_heap, (edge_weight, neighbor, current))

    return mst_edges, total_weight, steps   # ✅ UPDATED


# 🔥 KRUSKAL MST WITH STEP TRACKING
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

    # Build edge list
    for i in range(num_vertices):
        for j in range(i + 1, num_vertices):
            if matrix[i][j] > 0:
                edges.append((matrix[i][j], i, j))

    edges.sort()

    mst_edges = []
    steps = []   # ✅ UPDATED
    total_weight = 0
   
# 🔥 ADD INITIAL STEP (START NODE)
    steps.append({
    "edges": [],
    "current": mst_edges[0][0] if mst_edges else 0  # you can choose first node
    })
     
    for weight, u, v in edges:

        if union(u, v):
            mst_edges.append((u, v, weight))
            total_weight += weight

            # 🔥 UPDATED STEP STRUCTURE
            steps.append({
                "edges": list(mst_edges),
                "current": v
            })

        if len(mst_edges) == num_vertices - 1:
            break

    return mst_edges, total_weight, steps   # ✅ UPDATED