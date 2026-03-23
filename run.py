from flask import Flask, render_template

from app.routes.graph_routes import graph_bp
from app.routes.mst_routes import mst_bp
from app.routes.huffman_routes import huffman_bp

app = Flask(__name__)

# ADD THIS LINE
app.secret_key = "super_secret_key_123"

@app.context_processor
def utility_processor():
    return dict(chr=chr)

app.register_blueprint(graph_bp)
app.register_blueprint(mst_bp)
app.register_blueprint(huffman_bp)


@app.route("/")
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
        "home.html",
        stats=stats,
        recent_activity=recent_activity
    )


if __name__ == "__main__":
    app.run(debug=True)