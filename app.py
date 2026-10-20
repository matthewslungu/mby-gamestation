import streamlit as st
import pandas as pd
import datetime
import os
import time

# File name for your shared database history log
DATA_FILE = "mby_gamestation_history.csv"

# --- 1. DYNAMIC MOBILE SPLASH SCREEN ENGINE ---
if "splash_completed" not in st.session_state:
    st.session_state.splash_completed = False

if not st.session_state.splash_completed:
    st.markdown(
        """
        <style>
        .splash-container {
            position: fixed;
            top: 0; left: 0; width: 100vw; height: 100vh;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 30%, #11998e 70%, #38ef7d 100%);
            z-index: 999999;
            display: flex; flex-direction: column;
            justify-content: center; align-items: center;
            color: white; font-family: 'Arial Black', sans-serif; text-align: center;
        }
        .main-brand-title {
            font-size: 3.5rem; font-weight: 900; letter-spacing: 2px; margin-bottom: 10px;
            text-shadow: 2px 4px 10px rgba(0,0,0,0.3);
        }
        .motto-subtitle {
            font-size: 1.5rem; font-style: italic; opacity: 0.9;
            text-shadow: 1px 2px 5px rgba(0,0,0,0.3);
        }
        body { overflow: hidden; }
        </style>
        <div class="splash-container">
            <div class="main-brand-title">MBY GAMESTATION 🎮💯</div>
            <div class="motto-subtitle">Movin' Beyond Yesterday 🔥👻</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    time.sleep(3.0)
    st.session_state.splash_completed = True
    st.rerun()

# --- 2. PWA CONFIGURATION LINKING ---
st.set_page_config(page_title="MBY Gamestation", page_icon="🎮", layout="wide")
st.markdown('<link rel="manifest" href="/manifest.json">', unsafe_allow_html=True)

# --- 3. APP BRANDING HEADER ---
st.write("# **MBY GAMESTATION DASHBOARD 🎮💯**")
st.write("### *Movin' Beyond Yesterday 🔥👻*")
st.write("---")

# --- 4. STAFF LOGIN & SHIFT ATTENDANCE ---
operator = st.selectbox("👤 Current Shift Operator:", [
    "VeNom (Matthews)", 
    "Bob (Jacob)", 
    "Level (Immanuel)"
])

# Initialize memory for active gaming sessions
if "active_sessions" not in st.session_state:
    st.session_state.active_sessions = []

# --- 5. SHOP STATUS (POWER / LOAD-SHEDDING TRACKER) ---
st.write("### 🔌 Shop Operational Status")
shop_worked = st.checkbox("Did the shop operate normally today?", value=True)

if not shop_worked:
    reason_no_work = st.text_area("Reason for no business activity (e.g., No power the whole day):")
    if st.button("Submit Interruption Log"):
        now = datetime.datetime.now()
        interruption_row = {
            "Date": now.strftime("%Y-%m-%d"),
            "Day": now.strftime("%A"),
            "Month": now.strftime("%B"),
            "Year": now.strftime("%Y"),
            "Operator": operator,
            "Player": "N/A", "Console": "N/A", "Game": "SHOP CLOSED", "Qty": 0, "Amount Paid (K)": 0.0,
            "Start Time": "N/A", "Stop Time": "N/A", "Duration (Mins)": 0,
            "Notes": f"Closed: {reason_no_work}"
        }
        df_new = pd.DataFrame([interruption_row])
        if os.path.exists(DATA_FILE):
            pd.concat([pd.read_csv(DATA_FILE), df_new], ignore_index=True).to_csv(DATA_FILE, index=False)
        else:
            df_new.to_csv(DATA_FILE, index=False)
        st.warning("Closure reason logged to records.")
else:
    # --- 6. CORE DASHBOARD SPLIT LAYOUT ---
    left_col, right_col = st.columns(2)

    with left_col:
        st.write("### 📥 Start New Session")
        with st.form("entry_form", clear_on_submit=True):
            player_name = st.text_input("Player Name")
            console = st.selectbox("Select Console:", ["Xbox One", "PS5", "PS4", "PC Booth"])
            game_selected = st.selectbox("Select Game:", ["FC 27", "Blur", "Call of Duty (COD)", "GTA V"])
            quantity = st.number_input("Quantity (Matches / Laps / 5-Min Blocks):", min_value=1, value=1)
            amount_paid = st.number_input("Amount Paid (K):", min_value=0.0, format="%.2f")
            
            start_btn = st.form_submit_button("▶️ Start Active Session")
            
        if start_btn:
            if player_name.strip() == "":
                st.error("Please enter a Player Name!")
            else:
                now_time = datetime.datetime.now()
                target_mins = quantity * 5 if game_selected in ["Call of Duty (COD)", "GTA V"] else 9999
                target_stop = now_time + datetime.timedelta(minutes=target_mins)
                
                new_session = {
                    "Player": player_name, "Console": console, "Game": game_selected,
                    "Qty": quantity, "Amount": amount_paid,
                    "Start_Obj": now_time, "Start_Str": now_time.strftime("%H:%M"),
                    "Target_Stop": target_stop, "Alarm_Triggered": False
                }
                st.session_state.active_sessions.append(new_session)
                st.success(f"Session locked for {player_name}!")
                st.rerun()

    with right_col:
        st.write("### 🎮 Active Sessions Box")
        if not st.session_state.active_sessions:
            st.info("No active sessions right now.")
        else:
            now_check = datetime.datetime.now()
            for index, session in enumerate(st.session_state.active_sessions):
                is_time_up = now_check >= session["Target_Stop"] and session["Game"] in ["Call of Duty (COD)", "GTA V"]
                
                if is_time_up:
                    st.error(f"⏰ **TIME IS UP FOR {session['Player'].upper()} ON {session['Console'].upper()}!**")
                    st.components.v1.html(
                        '<audio autoplay><source src="https://soundjay.com" type="audio/mpeg"></audio>',
                        height=0
                    )
                
                st.success(
                    f"🕹️ **{session['Console']}** | Player: **{session['Player']}** | "
                    f"Game: **{session['Game']}** (Qty: {session['Qty']}) | Paid: **K{session['Amount']:.2f}** | 🕒 Started: {session['Start_Str']}"
                )

        # --- 7. END SESSION AND COMMIT RECORDS ---
        if st.session_state.active_sessions:
            st.write("---")
            st.write("### 🛑 Stop and Archive Session")
            choices = [f"{s['Console']} - {s['Player']}" for s in st.session_state.active_sessions]
            selected_session = st.selectbox("Choose active station to close:", choices)
            chosen_idx = choices.index(selected_session)
            
            if st.button("🔴 End Session & Log Cash"):
                stop_time = datetime.datetime.now()
                target = st.session_state.active_sessions[chosen_idx]
                delta = stop_time - target["Start_Obj"]
                elapsed_mins = max(1, round(delta.total_seconds() / 60))
                
                history_row = {
                    "Date": stop_time.strftime("%Y-%m-%d"),
                    "Day": stop_time.strftime("%A"),
                    "Month": stop_time.strftime("%B"),
                    "Year": stop_time.strftime("%Y"),
                    "Operator": operator,
                    "Player": target["Player"],
                    "Console": target["Console"],
                    "Game": target["Game"],
                    "Qty": target["Qty"],
                    "Amount Paid (K)": target["Amount"],
                    "Start Time": target["Start_Str"],
                    "Stop Time": stop_time.strftime("%H:%M"),
                    "Duration (Mins)": elapsed_mins,
                    "Notes": "Normal Session"
                }
                
                df_new = pd.DataFrame([history_row])
                if os.path.exists(DATA_FILE):
                    pd.concat([pd.read_csv(DATA_FILE), df_new], ignore_index=True).to_csv(DATA_FILE, index=False)
                else:
                    df_new.to_csv(DATA_FILE, index=False)
                    
                st.session_state.active_sessions.pop(chosen_idx)
                st.success("Transaction securely archived!")
                st.rerun()

# --- 8. MONTHLY FILTER & SEARCH HISTORY ENGINE ---
st.write("---")
st.write("### 📊 Search & Filter Ledger Records")
month_to_search = st.selectbox("Select Month to Inspect:", [
    "All Months", "January", "February", "March", "April", "May", 
    "June", "July", "August", "September", "October", "November", "December"
])

if os.path.exists(DATA_FILE):
    df_history = pd.read_csv(DATA_FILE)
    if month_to_search != "All Months":
        filtered_df = df_history[df_history["Month"] == month_to_search]
    else:
        filtered_df = df_history
        
    st.dataframe(filtered_df.sort_index(ascending=False), use_container_width=True)
    monthly_cash = filtered_df["Amount Paid (K)"].sum()
    st.metric(label=f"💸 Total Cash Collected for {month_to_search}", value=f"K {monthly_cash:,.2f}")
else:
    st.info("No history log database found yet.")