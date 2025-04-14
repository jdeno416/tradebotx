import time
import pickle
import json
import os
import yfinance as yf
import random
from datetime import datetime
from PIL import Image
import streamlit as st
from streamlit_autorefresh import st_autorefresh
from streamlit_js_eval import streamlit_js_eval


# === File Paths ===
ASSESSMENT_FILE = "saved_assessments.json"
STRATEGY_FILE = "strategy_log.json"
TRADE_REVIEW_FILE = "trade_reviews.json"
logo_path = "logo.png"
# ====== Helper Functions ======
MINDSET_FILE = "mindset_data.pkl"

def load_mindset_data():
    if os.path.exists(MINDSET_FILE):
        with open(MINDSET_FILE, "rb") as f:
            return pickle.load(f)
    return []

def save_mindset_data(data):
    with open(MINDSET_FILE, "wb") as f:
        pickle.dump(data, f)

def get_daily_quote():
    quotes = [
        "Breathe. Patience is profit.",
        "Detach from the outcome. Execute the plan.",
        "Emotions are signals, not commands.",
        "Clarity over chaos. Trust your setup.",
        "Discipline builds freedom.",
        "You're not your PnL. You're your process.",
        "Every trade is a lesson. Be the student."
    ]
    # Correctly set the seed
    today = datetime.today().date()  # Corrected line
    random.seed(today.toordinal())  # Seed the random generator with the ordinal of today's date
    
    # Return a random quote
    return random.choice(quotes)

# === Load Logo ===
logo = Image.open(logo_path)
st.image(logo, width=200)

# === Session State Initialization ===
defaults = {
    "score": 0, "percentage": 0, "question_idx": 0, "questions": [],
    "assessment_started": False, "selected_assessment": None,
    "active_tab": "home", "percentage_history": [], "strategy_log": [],
    "monthly_wins": 0, "monthly_losses": 0, "entry_price": None,
    "exit_price": None, "target_price": None, "stop_loss": None,
    "stock_symbol": None, "current_price": None, "answers": []
}
for key, default in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = default

# === JSON Load/Save Functions ===
def load_json(file): return json.load(open(file)) if os.path.exists(file) else {}
def save_json(file, data): json.dump(data, open(file, "w"), indent=4)

saved_assessments = load_json(ASSESSMENT_FILE)
st.session_state.strategy_log = load_json(STRATEGY_FILE)
trade_reviews = load_json(TRADE_REVIEW_FILE)
def save_trade_reviews(data): save_json(TRADE_REVIEW_FILE, data)



def show_desktop_layout():
    st.title("TradeBotX - Desktop View")
    st.write("This is the layout for desktop users.")
    # Add your full desktop layout code here

def show_mobile_layout():
    st.title("TradeBotX - Mobile View")
    st.write("This is the layout for mobile users.")
    # Add your full mobile layout code here


screen_width = streamlit_js_eval(js_expressions="screen.width", key="SCR")

if screen_width:
    if screen_width < 768:
        st.markdown("### 📱 Mobile View")
        show_mobile_layout()
    else:
        st.markdown("### 💻 Desktop View")
        show_desktop_layout()


# === Styling ===
st.markdown("""
    <style>
        .stApp { background: linear-gradient(to right, #f8f9fa, #e9ecef); color: black; }
        .stButton>button { background-color: #000000; color: white; font-weight: bold;
            border-radius: 16px; padding: 12px; font-size: 16px; width: 115%; }
        .stButton>button:hover { background-color: #27ae60; }
        .critical-warning { color: red; font-size: 20px; font-weight: bold; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# === Bottom Nav ===
col1, col2, col3, col4, col5, col6 = st.columns([1.5, 2, 2, 1.5, 1.5, 1.5])
with col1:
    if st.button("🏠 Home"): st.session_state.active_tab = "home"; st.rerun()
with col2:
    if st.button("📁Assessments"): st.session_state.active_tab = "assessments"; st.rerun()
with col3:
    if st.button("📊 Progress"): st.session_state.active_tab = "progress"; st.rerun()
with col4:
    if st.button("📜 Notes"): st.session_state.active_tab = "strategy"; st.rerun()
with col5:
    if st.button("📈 Review"): st.session_state.active_tab = "review"; st.rerun()
with col6:
    if st.button("🧠 Mindset"): st.session_state.active_tab = "Mindset"; st.rerun()

# === Home Tab ===
if st.session_state.active_tab == "home":
    st.title("👥 TradeBotX")
    st.write("Welcome to your stock decision assistant.")
    st.subheader("💻 This Month's Performance")

    col1, col_reset, col2 = st.columns([1, 1, 1])
    with col1:
        st.markdown("<h3 style='text-align: center;'>☑ Wins</h3>", unsafe_allow_html=True)
        st.markdown(f"<h1 style='text-align: center; color: green;'>{st.session_state.monthly_wins}</h1>", unsafe_allow_html=True)
        col_win1, col_win2 = st.columns(2)
        if col_win1.button("➕", key="win_add"): st.session_state.monthly_wins += 1; st.rerun()
        if col_win2.button("➖", key="win_remove") and st.session_state.monthly_wins > 0: st.session_state.monthly_wins -= 1; st.rerun()

    with col_reset:
        if st.button("↻ Reset"): st.session_state.monthly_wins = 0; st.session_state.monthly_losses = 0; st.success("Reset!"); st.rerun()

    with col2:
        st.markdown("<h3 style='text-align: center;'>☒ Losses</h3>", unsafe_allow_html=True)
        st.markdown(f"<h1 style='text-align: center; color: red;'>{st.session_state.monthly_losses}</h1>", unsafe_allow_html=True)
        col_loss1, col_loss2 = st.columns(2)
        if col_loss1.button("➕", key="loss_add"): st.session_state.monthly_losses += 1; st.rerun()
        if col_loss2.button("➖", key="loss_remove") and st.session_state.monthly_losses > 0: st.session_state.monthly_losses -= 1; st.rerun()

    # === Stock Price Tracking ===
    st.subheader("💰 Stock Price Tracker")
    stock_symbol = st.text_input("Enter Stock Symbol (e.g., TSLA)", value=st.session_state.stock_symbol or "")
    if stock_symbol:
        st.session_state.stock_symbol = stock_symbol
        try:
            stock_data = yf.Ticker(stock_symbol)
            hist = stock_data.history(period="1d", interval="1m")
            if not hist.empty:
                st.session_state.current_price = hist["Close"].iloc[-1]
                st.write(f"📈 Current Price of {stock_symbol}: ${st.session_state.current_price:.2f}")
            else:
                st.warning("⚠ No data available for the selected stock. Please try again later.")
        except Exception as e:
            st.error(f"Failed to fetch stock price: {e}")

        st_autorefresh(interval=1000, key="stock_refresh")

        entry_price = st.number_input("Set Entry Price", value=st.session_state.entry_price or 0.0)
        if entry_price:
            st.session_state.entry_price = entry_price
            st.write(f"📍 Entry Price Set: ${st.session_state.entry_price:.2f}")

        target_price = st.number_input("Set Target Price", value=st.session_state.target_price or 0.0)
        if target_price:
            st.session_state.target_price = target_price
            st.write(f"🎯 Target Price Set: ${st.session_state.target_price:.2f}")

        stop_loss = st.number_input("Set Stop-Loss Price", value=st.session_state.stop_loss or 0.0)
        if stop_loss:
            st.session_state.stop_loss = stop_loss
            st.write(f"⛔ Stop-Loss Price Set: ${st.session_state.stop_loss:.2f}")

        if st.session_state.entry_price and st.session_state.target_price and st.session_state.stop_loss and st.session_state.current_price:
            if st.session_state.current_price >= st.session_state.target_price:
                st.success(f"🎯 Target Price of ${st.session_state.target_price:.2f} reached!")
            elif st.session_state.current_price <= st.session_state.stop_loss:
                st.error(f"⛔ Stop-Loss of ${st.session_state.stop_loss:.2f} triggered!")

# === Continue with your existing Assessments, Progress, Strategy, and Review tabs ===


# === Assessments Tab ===
elif st.session_state.active_tab == "assessments":
    st.subheader("📁 Saved Assessments")
    selected = st.selectbox("Select an assessment", ["New Assessment"] + list(saved_assessments.keys()))
    if selected != st.session_state.selected_assessment:
        st.session_state.selected_assessment = selected
        st.session_state.questions = [] if selected == "New Assessment" else saved_assessments[selected]
        st.session_state.assessment_started = False
        st.session_state.score = 0
        st.session_state.percentage = 0
        st.session_state.question_idx = 0
        st.session_state.percentage_history = []
        st.rerun()

    if not st.session_state.assessment_started:
        num_q = st.number_input("How many questions?", min_value=1, value=max(1, len(st.session_state.questions)), step=1)
        st.session_state.questions = st.session_state.questions[:num_q] + [{}] * (num_q - len(st.session_state.questions))

        for i in range(num_q):
            st.session_state.questions[i] = {
                "question": st.text_input(f"Question {i+1}", st.session_state.questions[i].get("question", ""), key=f"q_{i}"),
                "weight_yes": st.number_input(f"Weight Yes - Q{i+1}", value=st.session_state.questions[i].get("weight_yes", 10), key=f"w_yes_{i}"),
                "weight_no": st.number_input(f"Weight No - Q{i+1}", value=st.session_state.questions[i].get("weight_no", -10), key=f"w_no_{i}"),
                "critical": st.checkbox(f"Critical (Yes resets score)? - Q{i+1}", value=st.session_state.questions[i].get("critical", False), key=f"crit_{i}")
            }

        assessment_name = st.text_input("Assessment Name", value=st.session_state.selected_assessment if selected != "New Assessment" else "")
        if st.button("💾 Save Assessment") and assessment_name:
            saved_assessments[assessment_name] = st.session_state.questions
            save_json(ASSESSMENT_FILE, saved_assessments)
            st.success("Assessment saved!")
            st.rerun()

        if st.button("✅ Start Assessment"):
            st.session_state.assessment_started = True
            st.session_state.score = 0
            st.session_state.percentage = 0
            st.session_state.question_idx = 0
            st.session_state.percentage_history = []
            st.session_state.answers = []
            st.rerun()

    else:
        st.subheader("🧠 Answer the Questions")

        responses = {}
        score = 0
        critical_triggered = False
        total_yes_weight = sum(q["weight_yes"] for q in st.session_state.questions)

        for i, q in enumerate(st.session_state.questions):
            col1, col2 = st.columns([6, 4])
            with col1:
                st.markdown(f"**{q['question']}**")
            with col2:
                response = st.radio(
                    f"answer_{i}", ["Unanswered", "Yes", "No"], key=f"resp_{i}", horizontal=True, label_visibility="collapsed"
                )
                responses[i] = response

        answers = []
        for i, q in enumerate(st.session_state.questions):
            answer = responses[i]
            if answer == "Yes":
                if q["critical"]:
                    critical_triggered = True
                else:
                    score += q["weight_yes"]
            elif answer == "No":
                score += q["weight_no"]

            if answer in ["Yes", "No"]:
                answers.append({
                    "question": q["question"],
                    "answer": answer,
                    "weight_yes": q["weight_yes"],
                    "weight_no": q["weight_no"],
                    "critical": q["critical"]
                })

        if critical_triggered:
            st.markdown(
                "<h3 style='color:red;'>⚠️ Warning: You Are Over Trading Limit. Maximum Loss Hit.</h3>",
                unsafe_allow_html=True
            )
            score = 0

        if any(a in ["Yes", "No"] for a in responses.values()):
            percentage = round((score / total_yes_weight) * 100 if total_yes_weight else 0, 2)
            st.markdown(f"### ✅ Live Score: **{percentage}%**")
            st.session_state.score = score
            st.session_state.percentage = percentage
            st.session_state.answers = answers

            if st.button("💾 Save to Trade Review"):
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                trade_reviews[timestamp] = {
                    "assessment": st.session_state.selected_assessment,
                    "score": score,
                    "percentage": percentage,
                    "answers": answers,
                    "result": "Pending"
                }
                save_trade_reviews(trade_reviews)
                st.success("Saved to Trade Review!")

      	
# === Progress Chart ===
elif st.session_state.active_tab == "progress":
    st.subheader("📊 Score Progress Chart")
    if st.session_state.percentage_history:
        st.line_chart(st.session_state.percentage_history)
    else:
        st.info("No progress yet.")

# === Strategy Notes ===
elif st.session_state.active_tab == "strategy":
    st.subheader("♟️ Notes Log")
    with st.form("strategy_form"):
        result = st.text_input("What happened? (e.g., TSLA went up $4)")
        if st.form_submit_button("➕ Log Result"):
            st.session_state.strategy_log.append(result)
            save_json(STRATEGY_FILE, st.session_state.strategy_log)
            st.success("Logged!")
    if st.session_state.strategy_log:
        for idx, entry in enumerate(reversed(st.session_state.strategy_log), 1):
            st.write(f"{idx}. {entry}")

# === Trade Review Tab ===
elif st.session_state.active_tab == "review":
    st.subheader("📈 Trade Review")
    if trade_reviews:
        for ts, trade in reversed(trade_reviews.items()):
            st.markdown(f"### 🕒 {ts}")
            st.write(f"**Assessment**: {trade['assessment']}")
            st.write(f"**Score**: {trade['score']} | **%**: {trade['percentage']}%")
            st.write("**Answers:**")
            for a in trade["answers"]:
                st.markdown(f"- **{a['question']}** → `{a['answer']}` | Crit: {a['critical']}")
            result = st.radio("Did the trade work?", ["Pending", "Worked", "Didn’t Work"], index=["Pending", "Worked", "Didn’t Work"].index(trade["result"]), key=ts)
            if result != trade["result"]:
                trade_reviews[ts]["result"] = result
                save_trade_reviews(trade_reviews)
                st.success("Trade result updated!")
    else:
        st.info("No completed assessments saved yet.")

# ====== Mindset Tab ======
elif st.session_state.active_tab == "Mindset":
    st.title("🧠 Mindset")

    # Daily Calm Quote
    st.markdown("### 🧘 Calm Daily Quote")
    st.info(get_daily_quote())

    # Load and store journal entries
    journal_entries = load_mindset_data()

    # Entry Form
    st.markdown("### ✍️ Journal Entry")
    entry_type = st.selectbox("Entry Type", ["Before Trade", "After Trade"])
    mood = st.selectbox("Mood", ["Calm", "Anxious", "Greedy", "Fearful", "Confident", "Frustrated"])
    text = st.text_area("Your thoughts...")

    if st.button("Save Entry"):
        if text.strip():
            journal_entries.append({
                "timestamp": datetime.now(),
                "type": entry_type,
                "mood": mood,
                "text": text.strip()
            })
            save_mindset_data(journal_entries)
            st.success("Entry saved!")

    # Filters
    st.markdown("### 🔍 Filter Entries")
    mood_filter = st.selectbox("Filter by Mood", ["All"] + list(set(e['mood'] for e in journal_entries)))
    type_filter = st.selectbox("Filter by Entry Type", ["All", "Before Trade", "After Trade"])

    # Filtered Entries
    filtered_entries = [
        e for e in journal_entries
        if (mood_filter == "All" or e["mood"] == mood_filter) and
           (type_filter == "All" or e["type"] == type_filter)
    ]

    st.markdown("### 📘 Journal History")
    for entry in reversed(filtered_entries):
        with st.container():
            st.markdown(f"**🕒 {entry['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}**  \n"
                        f"**📝 Type:** {entry['type']}  \n"
                        f"**😌 Mood:** {entry['mood']}  \n"
                        f"{entry['text']}")
            st.markdown("---")


















