import sys
import numpy as np


class Matrix:
    def __init__(self, n):
        self.matrix = np.empty([n, n + 1])

    def add_row(self, row_id, value_array):
        for x in range(len(value_array)):
            self.matrix[row_id][x] = value_array[x]

    def add_multiple(self, multiple, original_row, altered_row):
        for x in range(len(self.matrix[original_row])):
            constant = self.matrix[original_row][x] * multiple
            self.matrix[altered_row][x] = self.matrix[altered_row][x] + constant

    def scale(self, constant, row_id):
        for x in range(len(self.matrix[row_id])):
            self.matrix[row_id][x] = self.matrix[row_id][x] * constant

    def swap(self, row1, row2):
        if row1 == row2:
            return
        for x in range(len(self.matrix[row1])):
            temp = self.matrix[row1][x]
            self.matrix[row1][x] = self.matrix[row2][x]
            self.matrix[row2][x] = temp


def row_reduce(matrix1, rows):
    # Make a counter to indicate where the pivot rows end.
    pivot_counter = -1
    while True:
        # Check each row for the leftmost non-zero coefficient.
        for index_number in range(rows):
            for row_number in range(rows):

                # Check if row is a pivot row.
                if row_number > pivot_counter:

                    # If there is a nonzero coefficient in the leftmost column
                    coefficient = matrix1.matrix[row_number][index_number]
                    if coefficient is not 0:

                        # Swap row to top of non-pivot rows.
                        matrix1.swap(row_number, pivot_counter + 1)
                        new_row = pivot_counter + 1

                        # Row becomes a pivot row, which increases pivot counter by one.
                        pivot_counter += 1

                        # Rescale to make pivot coefficient 1.
                        matrix1.scale((1 / coefficient), new_row)

                        # Subtract row from others to make other coefficients for the same variable zero.
                        for zero_row in range(rows):
                            if zero_row != new_row:
                                coefficient_to_zero = matrix1.matrix[zero_row][index_number]
                                if coefficient_to_zero is not 0:
                                    matrix1.add_multiple((-1 * coefficient_to_zero), new_row, zero_row)

                        # We are now done with this variable. Break inner loop to continue looping at next index_number.
                        break
        return


# Get the number of dishes and ingredients (this will be the same number).
with open(sys.argv[1]) as input_file:
    N = int(input_file.readline())

    # Create an instance of the Matrix class.
    global m
    m = Matrix(N)

    # Add rows to the matrix.
    for i in range(N):
        next_line = input_file.readline()

        space = -1
        row = []
        for j in range(N + 1):
            if j < N:
                previous = space
                space = next_line.find(" ", previous + 1)
                value = int(next_line[previous + 1:space])
                row.append(value)
            elif j == N:
                backslash = next_line.find(" \n", space + 1)
                value = int(next_line[space + 1:backslash])
                row.append(value)

                m.add_row(i, row)

    # Solve for each variable.
    row_reduce(m, N)

    # Print the results. Any non-pivot variables are set to 0 for simplicity.
    for i in range(N):
        if m.matrix[i][i] == 1:
            decimals = "{:.3f}".format(m.matrix[i][N])
            print(decimals, end=" ")






