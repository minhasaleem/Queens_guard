"""
test_solver.py

A simple, standalone script to test solver.py without running the
Streamlit app. Run it with:

    python test_solver.py

This does NOT touch app.py or the UI in any way — Step 6 is only
about building and verifying the algorithm itself.
"""

from solver import solve_n_queens, columns_to_board


def print_board(board):
    for row in board:
        print(" ".join(row))
    print()


def main():
    for n in [4, 5, 6, 8]:
        print(f"Solving {n} x {n} N-Queens...")
        solution, stats = solve_n_queens(n)

        if solution is None:
            print("No solution found.")
        else:
            board = columns_to_board(solution, n)
            print_board(board)
            print(f"Solution (column per row): {solution}")

        print(f"Recursive calls: {stats['recursive_calls']}")
        print(f"Backtracks: {stats['backtracks']}")
        print("-" * 40)


if __name__ == "__main__":
    main()