import time
import random
import streamlit as st
from solver import solve_n_queens, columns_to_board

st.set_page_config(page_title="Queen's Guard", page_icon="♛", layout="wide")

# ------------------------------------------------------------------
# BOARD SIZE + DIFFICULTY — fully independent
# ------------------------------------------------------------------
BOARD_SIZES = [4, 5, 6, 8]

DIFFICULTY_CONFIG = {
    "Beginner":     {"blocked": 0, "hints": 3, "lives": 2},
    "Intermediate": {"blocked": 1, "hints": 3, "lives": 2},
    "Advanced":     {"blocked": 2, "hints": 2, "lives": 2},
    "Challenge":    {"blocked": 4, "hints": 1, "lives": 2},
}

def make_empty_board(n):
    return [["." for _ in range(n)] for _ in range(n)]

def count_queens(board):
    return sum(row.count("Q") for row in board)

def generate_blocked_cells(n, count):
    """Randomly choose blocked cells guaranteed not to overlap a real solution."""
    if count <= 0:
        return set()
    solution, _ = solve_n_queens(n)
    safe_cells = set(enumerate(solution)) if solution else set()
    all_cells = [(r, c) for r in range(n) for c in range(n)]
    candidates = [cell for cell in all_cells if cell not in safe_cells]
    random.shuffle(candidates)
    return set(candidates[:min(count, len(candidates))])

def build_level_board(n, blocked_count):
    blocked_cells = generate_blocked_cells(n, blocked_count)
    board = make_empty_board(n)
    for r, c in blocked_cells:
        board[r][c] = "X"
    return board, blocked_cells

def check_conflict(board, row, col):
    n = len(board)
    for r in range(n):
        for c in range(n):
            if board[r][c] == "Q":
                if r == row:
                    return f"same row as queen at Row {r + 1}"
                if c == col:
                    return f"same column as queen at Column {c + 1}"
                if abs(r - row) == abs(c - col):
                    return f"diagonal conflict with queen at Row {r + 1}, Column {c + 1}"
    return None

def calculate_score(queens_placed, conflicts, hints_used):
    score = (queens_placed * 100) - (conflicts * 25) - (hints_used * 15)
    return max(0, score)

def get_stars(score):
    if score >= 800:
        return 3
    if score >= 500:
        return 2
    return 1

def log_event(text, status="info"):
    log = st.session_state.algorithm_log
    if len(log) < 400:
        log.append((text, status))

def maybe_start_timer():
    """Timer starts on the player's FIRST successful/attempted move, not on page load."""
    if st.session_state.start_time is None:
        st.session_state.start_time = time.time()

# ------------------------------------------------------------------
# GAME (RE)INITIALIZATION
# ------------------------------------------------------------------
def reset_game():
    n = st.session_state.board_size
    cfg = DIFFICULTY_CONFIG[st.session_state.difficulty]
    board, blocked = build_level_board(n, cfg["blocked"])

    st.session_state.board = board
    st.session_state.blocked_cells = blocked
    st.session_state.moves = 0
    st.session_state.conflicts = 0
    st.session_state.lives = cfg["lives"]
    st.session_state.max_lives = cfg["lives"]
    st.session_state.hints_left = cfg["hints"]
    st.session_state.hints_used = 0
    st.session_state.hint_cell = None
    st.session_state.conflict_cell = None
    st.session_state.history = []
    st.session_state.start_time = None
    st.session_state.finished_time = None
    st.session_state.won = False
    st.session_state.game_over = False
    st.session_state.algorithm_log = []
    st.session_state.algo_stats = {"recursive_calls": None, "backtracks": None, "execution_time_ms": None}
    st.session_state.last_message = None
    st.session_state.last_message_type = "info"

def on_board_size_change():
    st.session_state.board_size = st.session_state.board_size_select
    reset_game()

def on_difficulty_change():
    st.session_state.difficulty = st.session_state.difficulty_select
    reset_game()

if "board_size" not in st.session_state:
    st.session_state.board_size = 4

if "difficulty" not in st.session_state:
    st.session_state.difficulty = "Beginner"

if "board" not in st.session_state:
    reset_game()

# ------------------------------------------------------------------
# GLOBAL THEME — "Royal Study" palette (PERMANENT design system)
# ------------------------------------------------------------------
st.markdown(
    """
    <style>
    :root {
        --qg-bg: #F5F3EE;
        --qg-card-bg: #FFFFFF;
        --qg-border: #E6E1D3;
        --qg-navy: #1F2A44;
        --qg-navy-light: #33436B;
        --qg-gold: #C6A15B;
        --qg-gold-dark: #A9843F;
        --qg-text-muted: #6B6B7A;
        --qg-conflict: #B3261E;
        --qg-safe: #3E7A57;
        --qg-radius: 14px;
        --qg-header-height: 3.75rem;
    }

    .stApp { background-color: var(--qg-bg); }

    [data-testid="stHeader"], .stAppHeader {
        background-color: var(--qg-bg) !important;
        box-shadow: none !important;
        height: var(--qg-header-height);
    }
    [data-testid="stHeader"] svg, .stAppHeader svg { fill: var(--qg-navy) !important; }

    .block-container {
        padding-top: calc(var(--qg-header-height) + 0.3rem) !important;
        padding-bottom: 0.5rem;
        max-width: 1150px;
    }

    [data-testid="stVerticalBlock"] { gap: 0.5rem !important; }

    .st-key-main_row [data-testid="stHorizontalBlock"] {
        align-items: flex-start !important;
    }

    /* ---- Sidebar base ---- */
    /* Force the focus/selection ring to gold on every click, including
   the very first one after the app starts — closes the brief blue
   flash before Streamlit's theme color takes over. */
[data-testid="stSidebar"] [data-baseweb="select"] > div {
    border-color: var(--qg-border) !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] > div:focus-within {
    border-color: var(--qg-gold) !important;
    box-shadow: 0 0 0 1px var(--qg-gold) !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] [aria-selected="true"] {
    background-color: var(--qg-gold) !important;
    color: var(--qg-navy) !important;
}
div[data-baseweb="popover"] li[aria-selected="true"] {
    background-color: var(--qg-gold) !important;
    color: var(--qg-navy) !important;
}
    [data-testid="stSidebar"] { background-color: var(--qg-card-bg); border-right: 1px solid var(--qg-border); }
    [data-testid="stSidebar"] h2 { color: var(--qg-navy); font-weight: 700; }
    [data-testid="stSidebar"] label p { color: var(--qg-navy) !important; font-weight: 600 !important; }
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p { color: var(--qg-text-muted) !important; }

    /* ---- Sidebar dropdowns (Board Size / Difficulty) ----
       Fixes the near-invisible light-gray selected text and arrow
       by forcing every text/icon element inside the selectbox to
       navy, and giving the box itself a gold-on-focus border. */
    [data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div {
        border-color: var(--qg-border) !important;
        background-color: var(--qg-card-bg) !important;
    }
    [data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div:focus-within {
        border-color: var(--qg-gold) !important;
        box-shadow: 0 0 0 1px var(--qg-gold) !important;
    }
    [data-testid="stSidebar"] [data-testid="stSelectbox"] div[data-baseweb="select"] * {
        color: var(--qg-navy) !important;
        fill: var(--qg-navy) !important;
        opacity: 1 !important;
    }
    /* Dropdown menu popover (the list that opens) is rendered outside
       the sidebar in the DOM, so it needs its own rule, not scoped
       to [data-testid="stSidebar"]. */
    div[data-baseweb="popover"] li {
        color: var(--qg-navy) !important;
        background-color: var(--qg-card-bg) !important;
    }
    div[data-baseweb="popover"] li:hover {
        background-color: var(--qg-bg) !important;
    }

    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: var(--qg-card-bg);
        border: 1px solid var(--qg-border) !important;
        border-radius: var(--qg-radius) !important;
        box-shadow: 0 2px 10px rgba(31, 42, 68, 0.06);
        padding: 0.2rem 0.2rem;
        margin-bottom: 0.5rem;
    }

    .st-key-main_game_card { border-top: 4px solid var(--qg-gold) !important; padding-top: 1rem !important; }
    .st-key-controls_stack [data-testid="stVerticalBlock"] { gap: 0.35rem !important; }

    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li,
    [data-testid="stMarkdownContainer"] span { color: var(--qg-navy); }

    .qg-panel-title {
        font-size: 0.95rem; font-weight: 700; margin-bottom: 0.4rem;
        color: var(--qg-navy); letter-spacing: 0.2px; text-transform: uppercase;
    }
    .qg-note { color: var(--qg-gold-dark); font-size: 0.8rem; font-weight: 600; margin-top: 0.3rem; }
    .qg-conflict-msg { color: var(--qg-conflict); font-size: 0.85rem; font-weight: 700; text-align: center; margin-top: 0.6rem; }
    .qg-hint-msg { color: var(--qg-gold-dark); font-size: 0.85rem; font-weight: 700; text-align: center; margin-top: 0.4rem; }
    .qg-info-msg { color: var(--qg-safe); font-size: 0.85rem; font-weight: 700; text-align: center; margin-top: 0.4rem; }

    .qg-legend { color: var(--qg-text-muted); font-size: 0.75rem; text-align: center; margin-top: 0.4rem; }
    .qg-legend-swatch { display: inline-block; width: 10px; height: 10px; border-radius: 2px; margin-right: 4px; vertical-align: middle; }
    .qg-legend-swatch.qg-hint-swatch { background-color: var(--qg-gold); }
    .qg-legend-swatch.qg-conflict-swatch { background-color: var(--qg-conflict); margin-left: 12px; }

    .qg-hero { text-align: center; padding: 0.3rem 0 0.2rem; }
    .qg-title-row { display: flex; align-items: center; justify-content: center; gap: 0.55rem; }
    .qg-crown-inline { font-size: 2.5rem; line-height: 1; color: var(--qg-gold-dark); }
    .qg-title-text {
        font-family: "Georgia", "Cambria", serif; font-size: 2.75rem; font-weight: 800;
        color: var(--qg-navy); letter-spacing: 0.5px; line-height: 1; margin: 0;
    }
    .qg-subtitle { color: var(--qg-text-muted); margin: 0.3rem 0 0 0; font-size: 1rem; }
    .qg-title-rule { border: none; height: 3px; width: 90px; background-color: var(--qg-gold); margin: 0.5rem auto 0 auto; border-radius: 2px; }

    .qg-hud-strip { display: flex; justify-content: center; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 0.5rem; }
    .qg-hud-item { background-color: var(--qg-card-bg); border: 1px solid var(--qg-border); border-radius: 10px; padding: 0.32rem 0.85rem; text-align: center; min-width: 88px; }
    .qg-hud-label { display: block; font-size: 0.65rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; color: var(--qg-text-muted); }
    .qg-hud-value { display: block; font-size: 1rem; font-weight: 700; color: var(--qg-navy); }

    .qg-info-line { display: flex; justify-content: space-between; align-items: center; padding: 0.28rem 0.1rem; font-size: 0.88rem; color: var(--qg-navy); border-bottom: 1px dashed var(--qg-border); }
    .qg-info-line:last-child { border-bottom: none; }
    .qg-info-value { font-weight: 700; }
    .qg-info-value.qg-info-alert { color: var(--qg-conflict); }
    .qg-info-subhead {
        font-size: 0.95rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.2px;
        color: var(--qg-navy); margin: 0.9rem 0 0.4rem 0; padding-top: 0.6rem;
        border-top: 1px solid var(--qg-border);
    }

    .stButton > button {
        background-color: var(--qg-navy); color: #FFFFFF; border: none; border-radius: 10px;
        padding: 0.35rem 0.9rem; font-weight: 600; width: 100%; transition: background-color 0.15s ease-in-out;
        outline: none !important;
    }
    .stButton > button:hover:not(:disabled) { background-color: var(--qg-navy-light); color: #FFFFFF; }
    .stButton > button:focus:not(:disabled),
    .stButton > button:focus-visible:not(:disabled),
    .stButton > button:active:not(:disabled) {
        background-color: var(--qg-navy) !important;
        color: #FFFFFF !important;
        outline: none !important;
        box-shadow: none !important;
        border: none !important;
    }
    .stButton > button:disabled { background-color: #E9E5D8; color: #A9A6B0; }
    .stButton > button p { color: #FFFFFF !important; font-weight: 700 !important; }
    .stButton > button:hover:not(:disabled) p { color: #FFFFFF !important; }
    .stButton > button:disabled p { color: #A9A6B0 !important; }

    hr { border-color: var(--qg-border); }

    .qg-log-box {
        max-height: 240px; overflow-y: auto; background-color: var(--qg-bg);
        border: 1px solid var(--qg-border); border-radius: 10px; padding: 0.6rem 0.8rem;
    }
    .qg-log-entry { font-family: "Courier New", monospace; font-size: 0.8rem; padding: 0.16rem 0; border-bottom: 1px dashed var(--qg-border); color: var(--qg-navy); }
    .qg-log-entry:last-child { border-bottom: none; }
    .qg-log-entry .qg-log-num { color: var(--qg-text-muted); margin-right: 0.4rem; }
    .qg-log-entry.qg-log-safe { color: var(--qg-safe); font-weight: 600; }
    .qg-log-entry.qg-log-conflict { color: var(--qg-conflict); }
    .qg-log-entry.qg-log-backtrack { color: var(--qg-gold-dark); font-weight: 600; }
    .qg-log-entry.qg-log-solution { color: var(--qg-safe); font-weight: 800; }
    .qg-log-truncated { font-size: 0.75rem; color: var(--qg-text-muted); text-align: center; margin-top: 0.4rem; font-style: italic; }

    .qg-banner { border-radius: var(--qg-radius); padding: 1rem 1.2rem; margin-bottom: 0.5rem; text-align: center; }
    .qg-banner-win { background-color: #EAF3ED; border: 1px solid var(--qg-safe); }
    .qg-banner-lose { background-color: #FBEAE9; border: 1px solid var(--qg-conflict); }
    .qg-banner-title { font-family: "Georgia", "Cambria", serif; font-size: 1.8rem; font-weight: 800; margin-bottom: 0.3rem; }
    .qg-banner-win .qg-banner-title { color: var(--qg-safe); }
    .qg-banner-lose .qg-banner-title { color: var(--qg-conflict); }
    .qg-stars { font-size: 1.6rem; margin: 0.3rem 0; }
    .qg-banner-stats { display: flex; justify-content: center; gap: 1.4rem; flex-wrap: wrap; margin-top: 0.5rem; font-size: 0.9rem; color: var(--qg-navy); }
    .qg-banner-stats b { display: block; font-size: 1.05rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------
# SIDEBAR — Board Size and Difficulty, fully independent dropdowns
# ------------------------------------------------------------------
with st.sidebar:
    st.header("♛ Game Settings")

    st.selectbox(
        "Board Size",
        options=BOARD_SIZES,
        format_func=lambda s: f"{s}×{s}",
        index=BOARD_SIZES.index(st.session_state.board_size),
        key="board_size_select",
        on_change=on_board_size_change,
    )

    st.selectbox(
        "Difficulty",
        options=list(DIFFICULTY_CONFIG.keys()),
        index=list(DIFFICULTY_CONFIG.keys()).index(st.session_state.difficulty),
        key="difficulty_select",
        on_change=on_difficulty_change,
    )
# ------------------------------------------------------------------
# HERO HEADER
# ------------------------------------------------------------------
st.markdown(
    """
    <div class="qg-hero">
        <div class="qg-title-row">
            <span class="qg-crown-inline">♛</span>
            <span class="qg-title-text">QUEEN'S GUARD</span>
        </div>
        <p class="qg-subtitle">Interactive N-Queens Backtracking Puzzle</p>
        <hr class="qg-title-rule" />
    </div>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------
# LIVE HUD — one fragment, one block, reruns every 1s
# ------------------------------------------------------------------
@st.fragment(run_every=1)
def render_hud():
    queens_on_board = count_queens(st.session_state.board)
    score = calculate_score(queens_on_board, st.session_state.conflicts, st.session_state.hints_used)

    if st.session_state.start_time is None:
        elapsed = 0
    elif st.session_state.finished_time is not None:
        elapsed = int(st.session_state.finished_time - st.session_state.start_time)
    else:
        elapsed = int(time.time() - st.session_state.start_time)
    minutes, seconds = divmod(max(0, elapsed), 60)

    hearts = "".join(
        "❤️" if i < st.session_state.lives else "🖤"
        for i in range(st.session_state.max_lives)
    )

    st.markdown(
        f"""
        <div class="qg-hud-strip">
            <div class="qg-hud-item">
                <span class="qg-hud-label">Board</span>
                <span class="qg-hud-value">{st.session_state.board_size}×{st.session_state.board_size}</span>
            </div>
            <div class="qg-hud-item">
                <span class="qg-hud-label">Difficulty</span>
                <span class="qg-hud-value">{st.session_state.difficulty}</span>
            </div>
            <div class="qg-hud-item">
                <span class="qg-hud-label">Lives</span>
                <span class="qg-hud-value">{hearts}</span>
            </div>
            <div class="qg-hud-item">
                <span class="qg-hud-label">Score</span>
                <span class="qg-hud-value">{score}</span>
            </div>
            <div class="qg-hud-item">
                <span class="qg-hud-label">Time</span>
                <span class="qg-hud-value">{minutes:02d}:{seconds:02d}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

render_hud()

# ------------------------------------------------------------------
# GAME STATE FOR THIS RENDER
# ------------------------------------------------------------------
n = st.session_state.board_size
game_active = not (st.session_state.won or st.session_state.game_over)
queens_on_board = count_queens(st.session_state.board)
score = calculate_score(queens_on_board, st.session_state.conflicts, st.session_state.hints_used)

# ------------------------------------------------------------------
# GAME OVER / LEVEL COMPLETE BANNER
# ------------------------------------------------------------------
if st.session_state.won or st.session_state.game_over:
    start = st.session_state.start_time or (st.session_state.finished_time or time.time())
    elapsed = int((st.session_state.finished_time or time.time()) - start)
    minutes, seconds = divmod(max(0, elapsed), 60)

    if st.session_state.won:
        stars = get_stars(score)
        star_str = "⭐" * stars + "☆" * (3 - stars)
        st.markdown(
            f"""
            <div class="qg-banner qg-banner-win">
                <div class="qg-banner-title">🏆 LEVEL COMPLETE!</div>
                <div class="qg-stars">{star_str}</div>
                <div class="qg-banner-stats">
                    <div><b>{queens_on_board}/{n}</b>Queens</div>
                    <div><b>{st.session_state.moves}</b>Moves</div>
                    <div><b>{st.session_state.conflicts}</b>Conflicts</div>
                    <div><b>{st.session_state.hints_used}</b>Hints Used</div>
                    <div><b>{minutes:02d}:{seconds:02d}</b>Time</div>
                    <div><b>{score}</b>Score</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div class="qg-banner qg-banner-lose">
                <div class="qg-banner-title">💔 GAME OVER</div>
                <div class="qg-banner-stats">
                    <div><b>{queens_on_board}/{n}</b>Queens</div>
                    <div><b>{st.session_state.moves}</b>Moves</div>
                    <div><b>{st.session_state.conflicts}</b>Conflicts</div>
                    <div><b>{minutes:02d}:{seconds:02d}</b>Time</div>
                    <div><b>{score}</b>Score</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    left_pad, mid, right_pad = st.columns([1, 2, 1])
    with mid:
        st.button("🔄 Reset Game", on_click=reset_game, use_container_width=True)

# ------------------------------------------------------------------
# CELL CLICK HANDLER
# ------------------------------------------------------------------
def handle_cell_click(row, col):
    if not game_active:
        return

    board = st.session_state.board
    cell = board[row][col]

    st.session_state.hint_cell = None
    st.session_state.conflict_cell = None

    if cell == "X":
        return

    if cell == "Q":
        board[row][col] = "."
        st.session_state.moves += 1
        if (row, col) in st.session_state.history:
            st.session_state.history.remove((row, col))
        log_event(f"Player removed queen at Row {row + 1}, Column {col + 1}", "info")
        st.session_state.last_message = None
        return

    if count_queens(board) >= n:
        return

    st.session_state.moves += 1
    reason = check_conflict(board, row, col)

    if reason is None:
        board[row][col] = "Q"
        st.session_state.history.append((row, col))
        maybe_start_timer()
        log_event(f"Player placed queen at Row {row + 1}, Column {col + 1} — SAFE", "safe")
        st.session_state.last_message = None

        if count_queens(board) == n:
            st.session_state.won = True
            st.session_state.finished_time = time.time()
            log_event("Solution Found — Player completed the board", "solution")
    else:
        maybe_start_timer()
        st.session_state.conflicts += 1
        st.session_state.lives -= 1
        st.session_state.conflict_cell = (row, col)
        log_event(
            f"Conflict at Row {row + 1}, Column {col + 1} ({reason}) — 1 life lost",
            "conflict",
        )
        st.session_state.last_message = f"Conflict detected: {reason}. 1 life lost."
        st.session_state.last_message_type = "conflict"

        if st.session_state.lives <= 0:
            st.session_state.game_over = True
            st.session_state.finished_time = time.time()
            log_event("GAME OVER — no lives remaining", "conflict")

# ------------------------------------------------------------------
# UNDO / HINT / AUTO SOLVE / SHOW SOLUTION
# ------------------------------------------------------------------
def handle_undo_click():
    if not game_active or not st.session_state.history:
        return
    row, col = st.session_state.history.pop()
    st.session_state.board[row][col] = "."
    st.session_state.hint_cell = None
    st.session_state.conflict_cell = None
    log_event(f"Undo — removed queen at Row {row + 1}, Column {col + 1}", "info")

def get_current_columns(board):
    columns = [None] * n
    for r in range(n):
        for c in range(n):
            if board[r][c] == "Q":
                columns[r] = c
    return columns

def handle_hint_click():
    if not game_active:
        return
    st.session_state.conflict_cell = None
    if st.session_state.hints_left <= 0:
        st.session_state.last_message = "No hints remaining for this level."
        st.session_state.last_message_type = "hint"
        return

    board = st.session_state.board
    if count_queens(board) >= n:
        st.session_state.last_message = "The board is already full."
        st.session_state.last_message_type = "hint"
        return

    columns = get_current_columns(board)
    log = []
    t0 = time.perf_counter()
    solution, stats = solve_n_queens(n, blocked=st.session_state.blocked_cells, start_columns=columns, log=log)
    t1 = time.perf_counter()

    st.session_state.algo_stats = {
        "recursive_calls": stats["recursive_calls"],
        "backtracks": stats["backtracks"],
        "execution_time_ms": (t1 - t0) * 1000,
    }
    st.session_state.algorithm_log.append(("--- Hint requested ---", "info"))
    for text, status in log:
        log_event(text, status)

    if solution is None:
        st.session_state.last_message = "No safe continuation found from the current placement."
        st.session_state.last_message_type = "hint"
        return

    for row in range(n):
        if columns[row] is None:
            col = solution[row]
            st.session_state.hint_cell = (row, col)
            st.session_state.hints_left -= 1
            st.session_state.hints_used += 1
            st.session_state.last_message = f"Hint: try Row {row + 1}, Column {col + 1}."
            st.session_state.last_message_type = "hint"
            break

def handle_auto_solve_click():
    if not game_active:
        return
    st.session_state.hint_cell = None
    st.session_state.conflict_cell = None

    board = st.session_state.board
    columns = get_current_columns(board)
    log = []
    t0 = time.perf_counter()
    solution, stats = solve_n_queens(n, blocked=st.session_state.blocked_cells, start_columns=columns, log=log)

    if solution is None:
        log = []
        solution, stats = solve_n_queens(n, blocked=st.session_state.blocked_cells, log=log)
    t1 = time.perf_counter()

    st.session_state.algo_stats = {
        "recursive_calls": stats["recursive_calls"],
        "backtracks": stats["backtracks"],
        "execution_time_ms": (t1 - t0) * 1000,
    }
    st.session_state.algorithm_log.append(("--- Auto Solve requested ---", "info"))
    for text, status in log:
        log_event(text, status)

    if solution is None:
        st.session_state.last_message = "No solution could be found for this board."
        st.session_state.last_message_type = "hint"
        return

    maybe_start_timer()
    st.session_state.board = columns_to_board(solution, n, blocked=st.session_state.blocked_cells)
    st.session_state.won = True
    st.session_state.finished_time = time.time()
    log_event("Solution Found — Auto Solve complete", "solution")

def handle_show_solution_click():
    if not game_active:
        return
    st.session_state.hint_cell = None
    st.session_state.conflict_cell = None

    t0 = time.perf_counter()
    solution, stats = solve_n_queens(n, blocked=st.session_state.blocked_cells)
    t1 = time.perf_counter()

    st.session_state.algo_stats = {
        "recursive_calls": stats["recursive_calls"],
        "backtracks": stats["backtracks"],
        "execution_time_ms": (t1 - t0) * 1000,
    }

    if solution is None:
        st.session_state.last_message = "No solution could be found for this board."
        st.session_state.last_message_type = "hint"
        return

    maybe_start_timer()
    st.session_state.board = columns_to_board(solution, n, blocked=st.session_state.blocked_cells)
    log_event("Show Solution used Backtracking to compute a valid arrangement.", "info")
    log_event("Solution revealed — level marked complete.", "solution")
    st.session_state.won = True
    st.session_state.finished_time = time.time()

# ------------------------------------------------------------------
# CHESSBOARD CSS
# ------------------------------------------------------------------
LIGHT_SQUARE = "#F0D9B5"
DARK_SQUARE = "#B58863"
LIGHT_SQUARE_TEXT = "#3B2A1A"
DARK_SQUARE_TEXT = "#FFF8E7"
HINT_SQUARE = "#E9CE93"
HINT_TEXT = "#3B2A1A"
CONFLICT_SQUARE = "#B3261E"
CONFLICT_TEXT = "#FFFFFF"

BOARD_PX = 420
cell_px = BOARD_PX // n
queen_font_px = max(16, int(cell_px * 0.55))

board_css_rules = []
for r in range(n):
    for c in range(n):
        if st.session_state.conflict_cell == (r, c):
            bg, fg = CONFLICT_SQUARE, CONFLICT_TEXT
        elif st.session_state.hint_cell == (r, c):
            bg, fg = HINT_SQUARE, HINT_TEXT
        else:
            is_light = (r + c) % 2 == 0
            bg = LIGHT_SQUARE if is_light else DARK_SQUARE
            fg = LIGHT_SQUARE_TEXT if is_light else DARK_SQUARE_TEXT

        board_css_rules.append(
            f"""
            .st-key-cell_{r}_{c} button {{
                background-color: {bg} !important; color: {fg} !important; border: none !important;
                border-radius: 0 !important; box-shadow: none !important; aspect-ratio: 1 / 1 !important;
                width: 100% !important; font-size: {queen_font_px}px !important; font-weight: 700 !important;
                transition: filter 0.12s ease-in-out; outline: none !important;
            }}
            .st-key-cell_{r}_{c} button:hover {{ filter: brightness(0.9); }}
            .st-key-cell_{r}_{c} button:focus,
            .st-key-cell_{r}_{c} button:focus-visible,
            .st-key-cell_{r}_{c} button:active {{
                background-color: {bg} !important; color: {fg} !important;
                outline: none !important; box-shadow: none !important; border: none !important;
            }}
            """
        )

st.markdown(
    f"""
    <style>
    .st-key-board_wrap {{ max-width: {BOARD_PX}px; margin: 0 auto; border: 6px solid #3B2A1A; border-radius: 4px; overflow: hidden; }}
    .st-key-board_wrap [data-testid="stHorizontalBlock"] {{ gap: 0px !important; }}
    .st-key-board_wrap [data-testid="column"] {{ padding: 0 !important; }}
    {"".join(board_css_rules)}
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------
# MAIN GRID — Board + Game Info (with optional Algorithm Statistics) / Hint & Controls
# ------------------------------------------------------------------
with st.container(key="main_row"):
    board_col, side_col = st.columns([3, 2])

    with board_col:
        with st.container(border=True, key="main_game_card"):
            board = st.session_state.board

            with st.container(key="board_wrap"):
                for r in range(n):
                    cols = st.columns(n)
                    for c in range(n):
                        cell_value = board[r][c]
                        if cell_value == "Q":
                            label = "♛"
                        elif cell_value == "X":
                            label = "✕"
                        elif st.session_state.conflict_cell == (r, c):
                            label = "!"
                        elif st.session_state.hint_cell == (r, c):
                            label = "?"
                        else:
                            label = "\u00A0"

                        with cols[c]:
                            st.button(
                                label,
                                key=f"cell_{r}_{c}",
                                use_container_width=True,
                                on_click=handle_cell_click,
                                args=(r, c),
                                disabled=not game_active,
                            )

            if st.session_state.last_message:
                msg_class = {
                    "conflict": "qg-conflict-msg",
                    "hint": "qg-hint-msg",
                    "info": "qg-info-msg",
                }.get(st.session_state.last_message_type, "qg-info-msg")
                st.markdown(f'<div class="{msg_class}">{st.session_state.last_message}</div>', unsafe_allow_html=True)

            st.markdown(
                '<div class="qg-legend">'
                '<span class="qg-legend-swatch qg-hint-swatch"></span>Hint suggestion'
                '<span class="qg-legend-swatch qg-conflict-swatch"></span>Conflict attempt'
                '</div>',
                unsafe_allow_html=True,
            )

    with side_col:
        with st.container(border=True):
            st.markdown('<div class="qg-panel-title">Game Info</div>', unsafe_allow_html=True)
            st.markdown(
                f"""
                <div class="qg-info-line"><span>Queens placed</span><span class="qg-info-value">{queens_on_board} / {n}</span></div>
                <div class="qg-info-line"><span>Lives</span><span class="qg-info-value">{st.session_state.lives} / {st.session_state.max_lives}</span></div>
                <div class="qg-info-line"><span>Moves</span><span class="qg-info-value">{st.session_state.moves}</span></div>
                <div class="qg-info-line"><span>Conflicts</span><span class="qg-info-value{' qg-info-alert' if st.session_state.conflicts else ''}">{st.session_state.conflicts}</span></div>
                <div class="qg-info-line"><span>Hints used</span><span class="qg-info-value">{st.session_state.hints_used} (left: {st.session_state.hints_left})</span></div>
                <div class="qg-info-line"><span>Blocked cells</span><span class="qg-info-value">{len(st.session_state.blocked_cells)}</span></div>
                """,
                unsafe_allow_html=True,
            )
            if queens_on_board >= n and game_active:
                st.markdown('<div class="qg-note">Maximum queens placed</div>', unsafe_allow_html=True)

            # Algorithm Statistics: COMPLETELY absent (no heading, no "-")
            # until the solver has actually run for this game.
            stats = st.session_state.algo_stats
            if stats["backtracks"] is not None:
                st.markdown('<div class="qg-info-subhead">Algorithm Statistics</div>', unsafe_allow_html=True)
                st.markdown(
                    f"""
                    <div class="qg-info-line"><span>Backtracks</span><span class="qg-info-value">{stats['backtracks']}</span></div>
                    <div class="qg-info-line"><span>Recursive calls</span><span class="qg-info-value">{stats['recursive_calls']}</span></div>
                    <div class="qg-info-line"><span>Execution time</span><span class="qg-info-value">{stats['execution_time_ms']:.2f} ms</span></div>
                    """,
                    unsafe_allow_html=True,
                )

        with st.container(border=True):
            st.markdown('<div class="qg-panel-title">Hint &amp; Controls</div>', unsafe_allow_html=True)
            with st.container(key="controls_stack"):
                st.button("Hint", on_click=handle_hint_click, use_container_width=True,
                           disabled=not game_active or st.session_state.hints_left <= 0)
                st.button("Undo", on_click=handle_undo_click, use_container_width=True,
                           disabled=not game_active or len(st.session_state.history) == 0)
                st.button("Auto Solve", on_click=handle_auto_solve_click, use_container_width=True,
                           disabled=not game_active)
                st.button("Reset", on_click=reset_game, use_container_width=True)
                st.button("Show Solution", on_click=handle_show_solution_click, use_container_width=True,
                           disabled=not game_active)

# ------------------------------------------------------------------
# ALGORITHM ACTIVITY — hidden entirely until there's real activity
# ------------------------------------------------------------------
STATUS_CLASS = {
    "safe": "qg-log-safe",
    "conflict": "qg-log-conflict",
    "backtrack": "qg-log-backtrack",
    "solution": "qg-log-solution",
    "info": "",
}

log = st.session_state.algorithm_log
if log:
    with st.container(border=True):
        st.markdown('<div class="qg-panel-title">Algorithm Activity</div>', unsafe_allow_html=True)
        entries_html = []
        for i, (text, status) in enumerate(log, start=1):
            css_class = STATUS_CLASS.get(status, "")
            entries_html.append(f'<div class="qg-log-entry {css_class}"><span class="qg-log-num">{i}.</span>{text}</div>')
        st.markdown(f'<div class="qg-log-box">{"".join(entries_html)}</div>', unsafe_allow_html=True)
        if len(log) >= 400:
            st.markdown('<div class="qg-log-truncated">Log truncated at 400 entries.</div>', unsafe_allow_html=True)