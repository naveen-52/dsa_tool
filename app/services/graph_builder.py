import networkx as nx
import matplotlib.pyplot as plt
import io
import base64


# 🔹 Build full graph from adjacency matrix (your original logic)
def build_graph_from_matrix(matrix):
    num_vertices = len(matrix)

    G = nx.Graph()
    G.add_nodes_from(range(num_vertices))

    for i in range(num_vertices):
        for j in range(i + 1, num_vertices):
            if matrix[i][j] != 0:
                G.add_edge(i, j, weight=matrix[i][j])

    return G


# 🔹 Build graph only from MST edges (NEW)
def build_mst_graph(mst_edges, num_vertices):
    G = nx.Graph()
    G.add_nodes_from(range(num_vertices))

    for u, v, w in mst_edges:
        G.add_edge(u, v, weight=w)

    return G


# 🔹 Generate graph image (base64 for HTML rendering)
def generate_graph_image(G):
    # ✅ FIX: stable layout (same output every time)
    pos = nx.spring_layout(G, seed=42)

    plt.figure(figsize=(6, 6))

    nx.draw(
        G,
        pos,
        with_labels=True,
        node_color="lightblue",
        node_size=800
    )

    edge_labels = nx.get_edge_attributes(G, "weight")
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

    # Convert to image (memory)
    img = io.BytesIO()
    plt.savefig(img, format="png")
    plt.close()

    img.seek(0)

    # Encode to base64
    return base64.b64encode(img.getvalue()).decode()

# 🔹 Generate Huffman Tree Image (NEW)
def generate_huffman_tree_image(tree):
    G = nx.DiGraph()
    pos = {}
    labels = {}

    def traverse(node_data, node_id=0, x=0, y=0, dx=1.0):
        if not node_data:
            return None
            
        G.add_node(node_id)
        pos[node_id] = (x, y)
        
        val = node_data.get("value", "")
        char = node_data.get("char")
        
        if char is not None:
            labels[node_id] = f"'{char}':{val}"
        else:
            labels[node_id] = str(val)
            
        next_id = node_id + 1
        
        left_data = node_data.get("left")
        if left_data:
            left_id = traverse(left_data, next_id, x - dx, y - 1, dx / 2)
            if left_id is not None:
                G.add_edge(node_id, left_id)
                next_id = max(G.nodes) + 1
            
        right_data = node_data.get("right")
        if right_data:
            right_id = traverse(right_data, next_id, x + dx, y - 1, dx / 2)
            if right_id is not None:
                G.add_edge(node_id, right_id)
            
        return node_id

    traverse(tree)

    plt.figure(figsize=(10, 6))
    
    nx.draw(
        G,
        pos,
        with_labels=False,
        node_color="#60a5fa",
        node_size=1500,
        edge_color="gray",
        arrows=False
    )
    
    nx.draw_networkx_labels(G, pos, labels, font_size=10, font_family="sans-serif")

    img = io.BytesIO()
    plt.savefig(img, format="png", bbox_inches='tight')
    plt.close()

    img.seek(0)
    return base64.b64encode(img.getvalue()).decode()