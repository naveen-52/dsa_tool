from flask import Blueprint, render_template, request, jsonify, session
from app.algorithms.huffman import build_huffman

huffman_bp = Blueprint("huffman", __name__)

@huffman_bp.route("/huffman", methods=["GET"])
def huffman_index():
    return render_template("huffman/index.html")

@huffman_bp.route("/huffman/visualize", methods=["GET"])
def huffman_visualize():
    return render_template("huffman/visualize.html")

# Preserving other UI routes to prevent HTML/Navigation breaks
@huffman_bp.route("/huffman/result", methods=["GET"])
def huffman_result():
    return render_template("huffman/result_page.html")

@huffman_bp.route("/huffman/animate", methods=["GET"])
def huffman_animate():
    return render_template("huffman/animate.html")


@huffman_bp.route("/huffman/encode", methods=["POST"])
def huffman_encode():
    try:
        data = request.get_json()
        if not data or "text" not in data:
            return jsonify({"error": "No text provided"}), 400

        text = data.get("text", "")
        if not text:
            return jsonify({"error": "Text cannot be empty"}), 400

        # Delegate purely to algorithm logic
        result = build_huffman(text)
        
        codes = result.get("codes", {})
        tree = result.get("tree", {})
        steps = result.get("steps", [])

        # Session storage
        session["text"] = text
        session["codes"] = codes
        session["tree"] = tree
        session["steps"] = steps

        # Generate the encoded string manually via the codes dict
        encoded_text = "".join(codes[char] for char in text)

        return jsonify({
            "encoded": encoded_text,
            "codes": codes,
            "tree": tree,
            "steps": steps
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500


@huffman_bp.route("/huffman/decode", methods=["POST"])
def huffman_decode():
    try:
        data = request.get_json()
        if not data or "encoded" not in data:
            return jsonify({"error": "No encoded text provided"}), 400

        encoded_text = data.get("encoded", "")

        # Retrieve mapped data from session
        codes = session.get("codes")

        if not codes:
            return jsonify({"error": "No codes found in session. Please encode first."}), 400

        # Invert the mapping: binary -> character
        reverse_codes = {v: k for k, v in codes.items()}

        decoded_text = ""
        current_bits = ""

        # Reconstruct exactly the original string
        for bit in encoded_text:
            current_bits += bit
            if current_bits in reverse_codes:
                decoded_text += reverse_codes[current_bits]
                current_bits = ""

        return jsonify({
            "decoded": decoded_text
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500