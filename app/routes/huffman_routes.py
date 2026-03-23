from flask import Blueprint, render_template, request
from collections import Counter

from app.algorithms.huffman import build_huffman_tree, generate_huffman_codes

huffman_bp = Blueprint("huffman", __name__)


@huffman_bp.route("/huffman")
def huffman_index():
    return render_template("huffman/index.html")


@huffman_bp.route("/huffman/encode", methods=["POST"])
def huffman_encode():

    text_input = request.form["text_input"]

    frequency = Counter(text_input)

    root = build_huffman_tree(text_input)

    codes = generate_huffman_codes(root)

    return render_template(
        "huffman/result.html",
        original_text=text_input,
        huffman_codes=codes,
        frequencies=frequency.items()
    )