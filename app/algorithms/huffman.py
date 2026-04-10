import heapq
from collections import Counter

class HuffmanNode:
    _id_counter = 0

    def __init__(self, char, freq):
        self.id = HuffmanNode._id_counter
        HuffmanNode._id_counter += 1
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq

    def to_dict(self):
        return {
            "id": self.id,
            "char": self.char,
            "freq": self.freq,
            "value": self.freq,
            "left": self.left.to_dict() if self.left else None,
            "right": self.right.to_dict() if self.right else None
        }

def build_huffman(text):
    if not text:
        return {
            "codes": {},
            "tree": {},
            "steps": []
        }

    # Reset counter for each run
    HuffmanNode._id_counter = 0

    # 1. Build frequency map
    frequency = Counter(text)

    # 2. Use min-heap to construct Huffman tree
    heap = []
    for char, freq in frequency.items():
        heapq.heappush(heap, HuffmanNode(char, freq))
        
    steps = []

    def get_queue_snapshot():
        return [{"id": n.id, "char": n.char, "freq": n.freq} for n in sorted(heap)]

    # 5. Generate steps for visualization
    while len(heap) > 1:
        # Pop two lowest frequency nodes
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        
        selected_nodes = [
            {"id": left.id, "char": left.char, "freq": left.freq},
            {"id": right.id, "char": right.char, "freq": right.freq}
        ]
        
        # Action: select
        steps.append({
            "action": "select",
            "queue": get_queue_snapshot(),
            "selected": selected_nodes,
            "result": {}
        })
        
        # Merge nodes
        merged = HuffmanNode(None, left.freq + right.freq)
        merged.left = left
        merged.right = right
        
        result_node = {"id": merged.id, "char": merged.char, "freq": merged.freq}
        
        # Action: merge
        steps.append({
            "action": "merge",
            "queue": get_queue_snapshot(),
            "selected": selected_nodes,
            "result": result_node
        })
        
        # Push merged node back to heap
        heapq.heappush(heap, merged)
        
        # Action: insert
        steps.append({
            "action": "insert",
            "queue": get_queue_snapshot(),
            "selected": [],
            "result": result_node
        })

    root = heap[0] if heap else None

    # 3. Generate binary codes
    codes = {}
    def generate_codes(node, current_code=""):
        if node is None:
            return
        if node.char is not None:
            codes[node.char] = current_code if current_code else "0"
            return
        generate_codes(node.left, current_code + "0")
        generate_codes(node.right, current_code + "1")

    if root:
        generate_codes(root)

    # 4. Encode text (built-in requirement but not returned based on constraints)
    encoded_text = "".join(codes[char] for char in text) if text and codes else ""

    return {
        "codes": codes,
        "tree": root.to_dict() if root else {},
        "steps": steps
    }