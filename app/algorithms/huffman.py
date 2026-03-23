import heapq
from collections import Counter


class HuffmanNode:

    def __init__(self, char, freq):

        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq


def build_huffman_tree(text):

    frequency = Counter(text)

    heap = [
        HuffmanNode(char, freq)
        for char, freq in frequency.items()
    ]

    heapq.heapify(heap)

    while len(heap) > 1:

        left = heapq.heappop(heap)
        right = heapq.heappop(heap)

        merged = HuffmanNode(None, left.freq + right.freq)

        merged.left = left
        merged.right = right

        heapq.heappush(heap, merged)

    return heap[0]


def generate_huffman_codes(root, code="", codes=None):

    if codes is None:
        codes = {}

    if root.char is not None:
        codes[root.char] = code if code else "0"
        return codes

    generate_huffman_codes(root.left, code + "0", codes)
    generate_huffman_codes(root.right, code + "1", codes)

    return codes