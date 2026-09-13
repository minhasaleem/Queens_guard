"""
solver.py
Backtracking algorithm for the N-Queens problem.

This file is intentionally kept separate from app.py so that:
- Hint and Auto Solve (Step 7) can both reuse this exact logic.
- The Algorithm Activity panel (Step 8) can hook into the same steps
  via optional step logging, without duplicating the algorithm.
- The core DAA algorithm stays easy to read/grade on its own, isolated
  from Streamlit/UI code.

BACKTRACKING LOGIC (plain-language):
1. Work one row at a time, starting at row 0.
2. In the current row, try each column from left to right.
3. Before placing a queen, check if that (row, column) is "safe":
   no other placed queen shares its column or either diagonal.
4. If safe: place the queen, then recursively try to solve the next row.
5. If that recursive call succeeds, we're done — bubble the success
   back up through every earlier call.
6. If it fails (no column worked in some later row), remove
   ("backtrack") the queen we just placed and try the next column
   in this row.
7. If no column in this row works at all, report failure to the row
   above (which will then backtrack itself, and so on).
8. Success is reached when we've placed a safe queen in every row.
"""


def is_safe(columns, row, col, blocked=None):
    """
    Check whether placing a queen at (row, col) is safe, given the
    queens already placed in rows 0..row-1.

    `columns` is a list where columns[r] is the column of the queen
    placed in row r (for rows that already have a queen).
    `blocked` is an optional set of (row, col) cells that can never
    hold a queen (used later for blocked-cell levels in Step 10).
    """
    blocked = blocked or set()

    if (row, col) in blocked:
        return False

    for r in range(row):
        c = columns[r]
        if c is None:
            continue
        if c == col:
            return False  # same column
        if abs(c - col) == abs(r - row):
            return False  # same diagonal
    return True


def why_unsafe(columns, row, col, blocked=None):
    """
    Explain why placing a queen at (row, col) is NOT safe.
    Used only for building readable Algorithm Activity log messages.
    """
    blocked = blocked or set()

    if (row, col) in blocked:
        return "cell is blocked"

    for r in range(row):
        c = columns[r]
        if c is None:
            continue
        if c == col:
            return f"same column as queen at row {r + 1}"
        if abs(c - col) == abs(r - row):
            return f"diagonal conflict with queen at row {r + 1}"

    return "unknown conflict"


def solve_n_queens(n, blocked=None, start_columns=None, start_row=0,
                    log=None, max_log_entries=400):
    """
    Solve the N-Queens problem using backtracking.

    Parameters:
        n              : board size (n x n)
        blocked        : optional set of (row, col) blocked cells
        start_columns  : optional partial solution to build on top of
                          (used by Hint/Auto Solve for a board that
                          already has some queens placed)
        start_row      : row to start solving from (default 0)
        log            : optional list — if provided, every algorithm
                          step (try/safe/conflict/place/backtrack/
                          solution) is appended to it as a
                          (text, status) tuple, for the Algorithm
                          Activity panel (Step 8). If None, no logging
                          happens (zero extra overhead).
        max_log_entries: caps how many entries get logged, so large
                          boards don't produce an unreadable wall of
                          text. Recursive call / backtrack counts in
                          `stats` are always accurate regardless of
                          this cap.

    Returns a tuple: (solution, stats)
        solution : list of length n, where solution[row] = column of
                   the queen in that row, or None if no solution exists
        stats    : dict with 'recursive_calls' and 'backtracks' counts
    """
    blocked = blocked or set()
    columns = list(start_columns) if start_columns else [None] * n

    stats = {"recursive_calls": 0, "backtracks": 0}

    def add_log(text, status="info"):
        if log is not None and len(log) < max_log_entries:
            log.append((text, status))

    def backtrack(row):
        stats["recursive_calls"] += 1

        # Base case: every row has a safely placed queen
        if row == n:
            add_log("All N queens placed safely — SOLUTION FOUND", "solution")
            return True

        # If this row already has a fixed queen (from start_columns),
        # just confirm it's safe and move on to the next row.
        if columns[row] is not None:
            if is_safe(columns, row, columns[row], blocked):
                return backtrack(row + 1)
            return False

        for col in range(n):
            add_log(f"Try queen at Row {row + 1}, Column {col + 1}")

            if is_safe(columns, row, col, blocked):
                add_log("Check row, column and diagonals — SAFE", "safe")
                columns[row] = col          # place the queen
                add_log(f"Place queen at Row {row + 1}, Column {col + 1}", "safe")

                if backtrack(row + 1):
                    return True

                add_log(
                    f"BACKTRACK — remove queen from Row {row + 1}, Column {col + 1}",
                    "backtrack",
                )
                columns[row] = None         # backtrack: undo and retry
                stats["backtracks"] += 1
            else:
                reason = why_unsafe(columns, row, col, blocked)
                add_log(f"Position rejected — CONFLICT ({reason})", "conflict")

        return False  # no column worked in this row

    success = backtrack(start_row)

    if success:
        return columns, stats
    return None, stats


def columns_to_board(columns, n, blocked=None):
    """
    Convert a `columns` solution (columns[row] = col) into the same
    board representation used by the Streamlit app: an n x n list of
    lists using '.', 'Q', 'X'.
    """
    blocked = blocked or set()
    board = [["." for _ in range(n)] for _ in range(n)]

    for r, c in blocked:
        board[r][c] = "X"

    if columns:
        for row, col in enumerate(columns):
            if col is not None:
                board[row][col] = "Q"

    return board