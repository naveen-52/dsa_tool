def validate_weight_matrix(matrix):

    n = len(matrix)

    for row in matrix:
        if len(row) != n:
            raise ValueError("Matrix must be square.")

    for i in range(n):
        for j in range(n):
            if matrix[i][j] != matrix[j][i]:
                raise ValueError("Matrix must be symmetric.")

    for i in range(n):
        for j in range(n):
            if matrix[i][j] < 0:
                raise ValueError("Negative weights are not allowed.")