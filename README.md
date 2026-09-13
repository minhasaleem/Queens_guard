# ♛ Queen's Guard

**An Interactive N-Queens Backtracking Puzzle**

Queen's Guard is an interactive web application that turns the classic **N-Queens problem** into an engaging puzzle game. Built with **Streamlit** and **Python**, it lets players place queens on an N×N chessboard so that no two queens threaten each other — while visualising every step of the backtracking algorithm under the hood.

> **Course:** Design and Analysis of Algorithms (DAA) — PBL Project  
> **Semester:** MCA Semester 3

---

## 🎮 Features

| Feature | Description |
|---|---|
| **Interactive Chessboard** | Click cells to place or remove queens on a beautifully styled board |
| **Conflict Detection** | Instant feedback when a queen placement violates row, column, or diagonal constraints |
| **Hint System** | Uses the backtracking solver to suggest the next safe placement |
| **Auto Solve** | Completes the board automatically from the current state (or from scratch) |
| **Show Solution** | Reveals a valid solution computed by the backtracking algorithm |
| **Undo** | Step back through your placement history one move at a time |
| **Live HUD** | Real-time display of board size, difficulty, lives, score, and elapsed time |
| **Algorithm Activity Log** | Step-by-step trace of the backtracking solver (try → safe/conflict → place → backtrack) |
| **Algorithm Statistics** | Tracks recursive calls, backtracks, and execution time after every solver invocation |
| **Multiple Board Sizes** | Supports 4×4, 5×5, 6×6, and 8×8 boards |
| **Difficulty Levels** | Four tiers with varying blocked cells, hints, and lives |
| **Scoring & Stars** | Performance-based scoring with a 3-star rating system |

---

## 🧠 Algorithm — Backtracking

The core solver implements a **recursive backtracking** approach:

```
1. Work one row at a time, starting at row 0.
2. In the current row, try each column from left to right.
3. Before placing a queen, check if (row, column) is "safe":
   → no other placed queen shares its column or either diagonal.
4. If safe — place the queen, then recursively solve the next row.
5. If the recursive call succeeds — bubble the success back up.
6. If it fails — remove ("backtrack") the queen and try the next column.
7. If no column in this row works — report failure to the row above.
8. Success is reached when every row has a safely placed queen.
```

The implementation lives in [`solver.py`](solver.py) and is intentionally separated from the UI so the algorithm can be read, tested, and graded independently.

### Time & Space Complexity

| Aspect | Complexity |
|---|---|
| **Time (worst case)** | O(N!) — each row reduces the branching factor |
| **Space** | O(N) — one column value stored per row + recursion stack depth N |

---

## 📁 Project Structure

```
queens_guard/
├── app.py              # Streamlit UI — game logic, board rendering, HUD, controls
├── solver.py           # Backtracking algorithm (is_safe, solve_n_queens, columns_to_board)
├── test_solver.py      # Standalone script to verify the solver without the UI
├── requirements.txt    # Python dependencies (streamlit >= 1.38.0)
├── .gitignore          # Standard ignores for venv, cache, OS files
└── README.md           # This file
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.9+**

### Installation

```bash
# 1. Clone the repository
git clone <repo-url>
cd queens_guard

# 2. Create and activate a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

### Running the App

```bash
streamlit run app.py
```

The app will open in your default browser at **http://localhost:8501**.

### Running the Solver Tests

```bash
python test_solver.py
```

This prints solutions and statistics for 4×4 through 8×8 boards without launching the Streamlit UI.

---

## 🎯 Difficulty Levels

| Level | Blocked Cells | Hints | Lives |
|---|:---:|:---:|:---:|
| **Beginner** | 0 | 3 | 2 |
| **Intermediate** | 1 | 3 | 2 |
| **Advanced** | 2 | 2 | 2 |
| **Challenge** | 4 | 1 | 2 |

Blocked cells are randomly placed but guaranteed **not** to overlap with a valid solution, so every game is always solvable.

---

## 🏆 Scoring

| Component | Points |
|---|---|
| Each queen placed | **+100** |
| Each conflict | **−25** |
| Each hint used | **−15** |

### Star Ratings

| Stars | Score Threshold |
|---|---|
| ⭐⭐⭐ | ≥ 800 |
| ⭐⭐ | ≥ 500 |
| ⭐ | < 500 |

---

## 🎨 Design

The UI follows a **"Royal Study"** design system:

- **Warm chessboard palette** — classic light (`#F0D9B5`) and dark (`#B58863`) squares
- **Navy & gold accents** — elegant navy (`#1F2A44`) and gold (`#C6A15B`) throughout
- **Card-based layout** — clean panels with subtle shadows and rounded borders
- **Visual feedback** — hint cells highlighted in gold, conflict cells in red
- **Live timer** — auto-updating HUD refreshes every second via Streamlit fragments

---

## 🛠 Tech Stack

| Technology | Purpose |
|---|---|
| **Python 3** | Core language |
| **Streamlit** (≥ 1.38.0) | Web UI framework — interactive widgets, session state, fragments |

No external solver libraries are used — the backtracking algorithm is implemented from scratch.

---

## 📄 License

This project was developed as an academic PBL (Project-Based Learning) submission.
