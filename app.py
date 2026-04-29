"""
FlightSage - Simple Working Version
"""

import streamlit as st
import re
from datetime import datetime
from orchestrator import FlightSageOrchestrator

st.set_page_config(
    page_title="FlightSage · AI Travel Strategist",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# CSS
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

#MainMenu, footer, header, [data-testid="stToolbar"] {visibility: hidden !important;}

.main .block-container {
    padding-top: 1rem !important;
    max-width: 1100px !important;
}

html, body, [data-testid="stAppViewContainer"] {
    background: #0a0a0f !important;
    color: #ffffff !important;
    font-family: 'Inter', sans-serif !important;
}

.stApp {
    background: 
        radial-gradient(circle at 20% 20%, rgba(139, 92, 246, 0.15) 0%, transparent 50%),
        radial-gradient(circle at 80% 80%, rgba(236, 72, 153, 0.15) 0%, transparent 50%),
        #0a0a0f !important;
}

.brand-logo {
    width: 44px; height: 44px;
    background: linear-gradient(135deg, #8b5cf6, #ec4899);
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.5rem;
}

.brand-name {
    font-size: 1.5rem;
    font-weight: 800;
    background: linear-gradient(120deg, #ffffff, #c4b5fd);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.brand-tagline {
    font-size: 0.7rem;
    color: #71717a;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}

.header-stat {
    display: inline-flex; align-items: center; gap: 0.4rem;
    padding: 0.4rem 0.85rem;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 100px;
    font-size: 0.75rem;
    color: #a1a1aa;
}

.pulse-dot {
    width: 6px; height: 6px;
    background: #10b981;
    border-radius: 50%;
}

.hero-headline {
    font-size: 3rem;
    font-weight: 800;
    text-align: center;
    margin: 2rem 0 1rem 0;
}

.gradient-text {
    background: linear-gradient(120deg, #8b5cf6, #ec4899, #f59e0b);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-sub {
    text-align: center;
    color: #a1a1aa;
    margin-bottom: 2rem;
}

.welcome-card {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 20px;
    padding: 2rem;
    margin: 1.5rem 0;
}

.welcome-greeting {
    font-size: 1.5rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
    color: #ffffff;
}

.welcome-text {
    color: #a1a1aa;
    margin-bottom: 1.5rem;
}

.prompts-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
}

.prompt-box {
    background: rgba(139, 92, 246, 0.05);
    border: 1px solid rgba(139, 92, 246, 0.15);
    border-radius: 12px;
    padding: 1.5rem 1rem;
    color: #c4b5fd;
    text-align: center;
    font-size: 0.9rem;
    cursor: pointer;
    transition: all 0.3s;
    min-height: 110px;
}

.prompt-box:hover {
    background: rgba(139, 92, 246, 0.12);
    transform: translateY(-2px);
}

.prompt-emoji {
    font-size: 2rem;
    margin-bottom: 0.5rem;
}

.dashboard-card {
    background: linear-gradient(135deg, rgba(139, 92, 246, 0.08), rgba(236, 72, 153, 0.08));
    border: 1px solid rgba(139, 92, 246, 0.2);
    border-radius: 20px;
    padding: 1.5rem;
    margin: 1.5rem 0;
}

.dashboard-header {
    color: #c4b5fd;
    font-weight: 600;
    text-transform: uppercase;
    margin-bottom: 1rem;
    font-size: 0.85rem;
}

.stat-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
}

.stat-tile {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    padding: 1rem;
}

.stat-icon { font-size: 1.2rem; margin-bottom: 0.5rem; }

.stat-number {
    font-size: 1.7rem;
    font-weight: 800;
    color: #ffffff;
}

.stat-name {
    font-size: 0.7rem;
    color: #a1a1aa;
    text-transform: uppercase;
}

.stTextInput > div > div > input {
    background-color: #1a1a2e !important;
    color: #ffffff !important;
    border: 1px solid rgba(139, 92, 246, 0.2) !important;
    border-radius: 14px !important;
    padding: 1rem 1.25rem !important;
}

.stButton > button {
    background: linear-gradient(135deg, #8b5cf6, #ec4899) !important;
    color: white !important;
    border: none !important;
    border-radius: 14px !important;
    font-weight: 600 !important;
}

h1, h2, h3, h4, h5, h6 { color: white !important; }
/* FIX CHAT MESSAGE COLORS */
[data-testid="stChatMessage"] {
    background: rgba(255, 255, 255, 0.04) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 12px !important;
    margin-bottom: 1rem !important;
}

[data-testid="stChatMessage"] * {
    color: #e4e4e7 !important;
}

[data-testid="chatAvatarIcon-user"],
[data-testid="chatAvatarIcon-assistant"] {
    background: linear-gradient(135deg, #8b5cf6, #ec4899) !important;
}

.app-footer {
    text-align: center;
    padding: 2rem 0;
    margin-top: 2rem;
    color: #52525b;
    font-size: 0.8rem;
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# HELPERS
# ============================================================
def sanitize_markdown(text):
    if not text:
        return text
    text = re.sub(r'\$(?=\d|\w)', '\\$', text)
    return text

def get_time():
    return datetime.now().strftime("%I:%M %p")


# ============================================================
# STATE
# ============================================================
if 'orchestrator' not in st.session_state:
    st.session_state.orchestrator = FlightSageOrchestrator()
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'last_trip_plan' not in st.session_state:
    st.session_state.last_trip_plan = None
if 'show_trip_dashboard' not in st.session_state:
    st.session_state.show_trip_dashboard = False
if 'input_counter' not in st.session_state:
    st.session_state.input_counter = 0


def send_message(text):
    if not text or not text.strip():
        return
    
    text = text.strip()
    
    st.session_state.messages.append({
        "role": "user",
        "content": text,
        "time": get_time()
    })
    
    result = st.session_state.orchestrator.chat(text)
    
    if result.get("success"):
        ai_message = result.get("message", "Hmm, something went wrong.")
        st.session_state.messages.append({
            "role": "assistant",
            "content": ai_message,
            "time": get_time()
        })
        
        if result.get("type") == "trip_plan":
            st.session_state.last_trip_plan = result
            st.session_state.show_trip_dashboard = True
        else:
            st.session_state.show_trip_dashboard = False
    
    elif result.get("type") == "no_results":
        st.session_state.messages.append({
            "role": "assistant",
            "content": result.get("message", "No flights found. Try a different budget."),
            "time": get_time()
        })
        st.session_state.show_trip_dashboard = False
    
    else:
        st.session_state.messages.append({
            "role": "assistant",
            "content": "❌ Something went wrong. Please try again.",
            "time": get_time()
        })
        st.session_state.show_trip_dashboard = False
    
    st.session_state.input_counter += 1


def process_message():
    user_input = st.session_state.get(f"chat_input_{st.session_state.input_counter}", "")
    if user_input:
        send_message(user_input)


# ============================================================
# HEADER
# ============================================================
header_col1, header_col2 = st.columns([3, 2])

with header_col1:
    st.markdown("""
<div style="display: flex; align-items: center; gap: 0.75rem; padding: 1rem 0;">
<div class="brand-logo">✈️</div>
<div>
<div class="brand-name">FlightSage</div>
<div class="brand-tagline">AI Travel Strategist</div>
</div>
</div>
""", unsafe_allow_html=True)

with header_col2:
    st.markdown("""
<div style="display: flex; gap: 0.5rem; justify-content: flex-end; padding: 1rem 0;">
<div class="header-stat">
<div class="pulse-dot"></div>
<span>4 agents online</span>
</div>
<div class="header-stat">⚡ Powered by Claude</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<hr style="border-color: rgba(255,255,255,0.05); margin: 0 0 1.5rem 0;">', unsafe_allow_html=True)


# ============================================================
# MAIN AREA
# ============================================================
if not st.session_state.messages:
    # WELCOME STATE
    st.markdown("""
<div class="hero-headline">
Plan smarter trips with<br>
<span class="gradient-text">AI that actually thinks.</span>
</div>
<div class="hero-sub">
Tell me where you want to go and I'll plan the perfect trip.
</div>
""", unsafe_allow_html=True)
    
    st.markdown("""
<div class="welcome-card">
<div class="welcome-greeting">👋 Hey there!</div>
<div class="welcome-text">I'm FlightSage. Try one of these or describe your own:</div>
<div class="prompts-grid">
<div class="prompt-box">
<div class="prompt-emoji">🌴</div>
<div>Warm beach trip<br>March under $800</div>
</div>
<div class="prompt-box">
<div class="prompt-emoji">🌸</div>
<div>Cherry blossoms<br>Japan, $1500</div>
</div>
<div class="prompt-box">
<div class="prompt-emoji">💕</div>
<div>Romantic<br>Paris in spring</div>
</div>
<div class="prompt-box">
<div class="prompt-emoji">🗼</div>
<div>Adventure in Asia<br>under $1500</div>
</div>
</div>
</div>
""", unsafe_allow_html=True)

else:
    # CHAT MODE
    chat_col1, chat_col2 = st.columns([4, 1])
    
    with chat_col1:
        st.markdown("### 💬 Conversation")
    
    with chat_col2:
        if st.button("🔄 New Chat", key="reset_btn", use_container_width=True):
            st.session_state.orchestrator.reset_conversation()
            st.session_state.messages = []
            st.session_state.last_trip_plan = None
            st.session_state.show_trip_dashboard = False
            st.session_state.input_counter += 1
            st.rerun()
    
    # Display messages using Streamlit's native chat
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            with st.chat_message("user", avatar="👤"):
                st.markdown(msg["content"])
                st.caption(msg.get("time", ""))
        else:
            with st.chat_message("assistant", avatar="✨"):
                safe_content = sanitize_markdown(msg["content"])
                st.markdown(safe_content)
                st.caption(f"FlightSage · {msg.get('time', '')}")


# ============================================================
# DASHBOARD
# ============================================================
if st.session_state.show_trip_dashboard and st.session_state.last_trip_plan:
    result = st.session_state.last_trip_plan
    
    budget = result["understood_as"].get("budget_max", "N/A")
    best_price = result["best_deal"]["flight"]["price_usd"] if result["best_deal"].get("success") else None
    destinations_found = result["search_results"]["destinations_with_results"]
    tips_used = len(result.get("insider_tips", []))
    
    st.markdown(f"""
<div class="dashboard-card">
<div class="dashboard-header">✨ Your Trip Plan</div>
<div class="stat-grid">
<div class="stat-tile">
<div class="stat-icon">💰</div>
<div class="stat-number">${budget}</div>
<div class="stat-name">Budget</div>
</div>
<div class="stat-tile">
<div class="stat-icon">🏆</div>
<div class="stat-number">{'$' + str(best_price) if best_price else 'N/A'}</div>
<div class="stat-name">Best Deal</div>
</div>
<div class="stat-tile">
<div class="stat-icon">🌍</div>
<div class="stat-number">{destinations_found}</div>
<div class="stat-name">Destinations</div>
</div>
<div class="stat-tile">
<div class="stat-icon">💡</div>
<div class="stat-number">{tips_used}</div>
<div class="stat-name">Insider Tips</div>
</div>
</div>
</div>
""", unsafe_allow_html=True)
    
    if result["search_results"].get("results"):
        with st.expander("✈️ View Flight Details"):
            for dest, data in result["search_results"]["results"].items():
                st.markdown(f"#### 📍 {data['destination_city']}, {data['destination_country']}")
                if data.get("flights"):
                    for flight in data["flights"]:
                        price_str = f"\\${flight['price_usd']:.2f}"
                        st.markdown(f"- **{flight['airline']} {flight['flight_number']}**: {price_str} ({flight['duration_hours']}h)")
                st.markdown("---")
    
    if result.get("insider_tips"):
        with st.expander("💡 Insider Tips Used"):
            for tip in result["insider_tips"]:
                st.markdown(f"**{tip['destination']} · {tip['category']}** ({tip.get('relevance_score', 0):.0%} match)")
                st.markdown(f"_{tip['tip']}_")
                st.markdown("---")


# ============================================================
# INPUT
# ============================================================
st.markdown("<br>", unsafe_allow_html=True)

input_col1, input_col2 = st.columns([6, 1])

with input_col1:
    user_input = st.text_input(
        "Type your message:",
        placeholder="Tell me about your dream trip... (Press Enter to send)",
        key=f"chat_input_{st.session_state.input_counter}",
        label_visibility="collapsed",
        on_change=process_message
    )

with input_col2:
    send_clicked = st.button("Send →", key="send_btn", use_container_width=True)

if send_clicked:
    user_input_value = st.session_state.get(f"chat_input_{st.session_state.input_counter}", "")
    if user_input_value:
        send_message(user_input_value)
        st.rerun()


# ============================================================
# FOOTER
# ============================================================
st.markdown("""
<div class="app-footer">
Built with multi-agent AI · 🧠 Claude · 📚 ChromaDB · 🐍 Python · ⚡ Streamlit
</div>
""", unsafe_allow_html=True)