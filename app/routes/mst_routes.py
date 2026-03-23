from flask import Blueprint, render_template, request
import networkx as nx
import matplotlib.pyplot as plt
import io
import base64

from app.algorithms.mst import prims_mst, kruskal_mst
from app.utils.validators import validate_weight_matrix

mst_bp = Blueprint("mst", __name__)


@mst_bp.route("/mst")
def mst_index():
    return render_template("mst/index.html")


@mst_bp.route("/mst/matrix", methods=["POST"])
def mst_matrix():

    num_vertices = int(request.form["num_vertices"])

    algorithm = request.form.get("algorithm", "prim")

    return render_template(
        "mst/matrix.html",
        num_vertices=num_vertices,
        algorithm=algorithm
    )

@mst_bp.route("/mst/calculate", methods=["POST"])
def mst_calculate():

    num_vertices = int(request.form.get("num_vertices", 0))
    algorithm = request.form.get("algorithm", "prim")

    matrix = []

    for i in range(num_vertices):
        row = []

        for j in range(num_vertices):

            value = request.form.get(f"cell_{i}_{j}")

            row.append(int(value))

        matrix.append(row)

    validate_weight_matrix(matrix)

    if algorithm == "kruskal":
        mst_edges, total_weight = kruskal_mst(num_vertices, matrix)
    else:
        mst_edges, total_weight = prims_mst(num_vertices, matrix)

    return render_template(
        "mst/result.html",
        mst_edges=mst_edges,
        total_weight=total_weight,
        algorithm=algorithm
    )