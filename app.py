import streamlit as st
import os
import random
from PIL import Image
from dotenv import load_dotenv
from agent import get_thirukural_agent
from langchain_core.messages import HumanMessage, AIMessage

# Load environment variables
load_dotenv()

# --- Streamlit Cloud Compatibility ---
# Ensure OpenAI API Key is available for LangChain
if "OPENAI_API_KEY" in st.secrets:
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

# --- Page Config ---
icon_path = "assets/icon.png" if os.path.exists("assets/icon.png") else "📜"

st.set_page_config(
    page_title="Thirukural Scholar",
    page_icon=icon_path,
    layout="wide"
)

# --- Custom CSS for Warm/Classic UI ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Tamil:wght@400;500;700&family=Lora:ital,wght@0,400;0,700;1,400&family=Cinzel:wght@600&display=swap');

    /* Global Warm Theme - Parchment Style */
    .stApp {
        background-color: #fdfbf7;
        background-image: radial-gradient(#e5e7eb 1px, transparent 1px);
        background-size: 20px 20px;
        color: #2c3e50;
    }
    
    /* Main Container Width */
    .block-container {
        max-width: 1200px !important;
        padding-top: 1rem !important;
    }

    /* Top Right Floating Badge */
    .tamil-vellum-badge {
        position: fixed;
        top: 25px;
        right: 40px;
        z-index: 1000;
        font-family: 'Noto Sans Tamil', sans-serif;
        font-weight: 700;
        font-size: 1.3rem;
        background: linear-gradient(to right, #b45309, #d97706); /* Copper/Gold */
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        border: none !important;
        text-shadow: 0px 2px 4px rgba(180, 83, 9, 0.1);
        letter-spacing: 0.5px;
    }

    /* Header Styling */
    .main-header {
        font-family: 'Cinzel', serif;
        color: #78350f; /* Amber 900 */
        text-align: left;
        font-size: 3.5rem;
        text-shadow: 1px 1px 0px rgba(255, 255, 255, 0.8);
        margin-bottom: 0px;
        margin-left: 60px; /* Moved Right */
        padding-top: 10px;
    }
    
    .subtitle {
        font-family: 'Lora', serif;
        color: #57534e; /* Stone 600 */
        font-size: 1.3rem;
        margin-bottom: 30px;
        margin-left: 65px; /* Aligned with Header */
        font-style: italic;
    }

    /* Floating Tamil Words Animation (Subtle Gold) */
    @keyframes float {
        0% { transform: translateY(0px) rotate(0deg); opacity: 0; }
        50% { transform: translateY(-30px) rotate(10deg); opacity: 0.25; }
        100% { transform: translateY(0px) rotate(0deg); opacity: 0; }
    }

    .floating-word {
        position: fixed;
        color: #d97706; /* Amber 600 */ 
        font-family: 'Noto Sans Tamil', sans-serif;
        font-size: 1.5rem;
        pointer-events: none;
        z-index: 0;
    }

    /* Chat Interface Styling - Clean & Classic */
    .stChatMessage {
        background-color: #ffffff !important;
        border: 1px solid #e5e5e5 !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02) !important;
        border-radius: 15px !important;
        margin-bottom: 15px;
        padding: 1.5rem !important;
    }

    /* User Message Specifics */
    [data-testid="stChatMessage"]:nth-child(odd) {
         background-color: #f8fafc !important; /* Slate 50 */
         border-left: 4px solid #94a3b8 !important;
    }
    
    /* Assistant Message Specifics */
    [data-testid="stChatMessage"]:nth-child(even) {
         background-color: #ffffff !important;
         border-left: 4px solid #f59e0b !important; /* Amber */
    }

    /* Input Box Styling */
    .stChatInput input {
        background-color: #ffffff !important;
        border: 2px solid #e7e5e4 !important;
        border-radius: 30px !important;
        color: #44403c !important;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
        padding: 15px !important;
        font-family: 'Lora', serif;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #fffbf7;
        border-right: 1px solid #f3f4f6;
    }

    .sidebar-counselor-title {
        font-family: 'Cinzel', serif;
        font-size: 1.4rem;
        color: #78350f;
        margin-bottom: 25px;
        text-align: center;
        line-height: 1.5;
        font-weight: 600;
        border-bottom: 2px solid #fef3c7;
        padding-bottom: 15px;
    }
    
    .sample-q {
        background-color: #fff;
        padding: 12px 15px;
        border-radius: 8px;
        margin-bottom: 10px;
        font-size: 0.95em;
        color: #57534e;
        border: 1px solid #e7e5e4;
        cursor: pointer;
        transition: all 0.2s;
    }
    .sample-q:hover {
        transform: translateY(-2px);
        border-color: #d97706;
        box-shadow: 0 4px 6px rgba(217, 119, 6, 0.1);
    }
    
    /* Custom Response Formatting */
    .kural-highlight {
        font-family: 'Noto Sans Tamil', serif;
        font-size: 1.8rem;
        line-height: 1.6;
        font-weight: 700;
        font-style: italic;
        color: #92400e; /* Amber 800 */
        margin: 20px 0;
        padding: 20px;
        background: radial-gradient(circle, #fffbeb 0%, #fff 100%);
        border-radius: 12px;
        border: 1px solid #fcd34d;
        text-align: center;
        box-shadow: inset 0 0 20px rgba(251, 191, 36, 0.1);
    }
    
    .explanation-text {
        font-family: 'Lora', serif;
        font-size: 1.15rem;
        line-height: 1.8;
        color: #44403c;
        margin-bottom: 20px;
    }
    
    /* Make Strong text stand out */
    strong {
        color: #78350f;
        font-weight: 600;
    }

</style>
""", unsafe_allow_html=True)

# --- Top Right Badge ---
st.markdown('<div class="tamil-vellum-badge">தமிழ் வெல்லும்</div>', unsafe_allow_html=True)

# --- Floating Background Words ---
tamil_words = [
    'அறம்', 'பொருள்', 'இன்பம்', 'வீடு', 'ஊழ்', 'அன்பு', 'பண்பு', 'கல்வி', 'கேள்வி', 
    'அறிவு', 'ஒழுக்கம்', 'பொறை', 'நட்பு', 'வாய்மை', 'புகழ்', 'மானம்', 'பெருமை', 
    'சான்றாண்மை', 'நல்குரவு', 'நாடு', 'அரண்', 'படை'
]

background_html = ""
for _ in range(25):
    word = random.choice(tamil_words)
    top = random.randint(5, 95)
    left = random.randint(5, 95)
    duration = random.randint(12, 20)
    delay = random.randint(0, 5)
    size = random.randint(20, 32)
    
    background_html += f"""
    <div class="floating-word" style="
        top: {top}vh; 
        left: {left}vw; 
        animation: float {duration}s ease-in-out {delay}s infinite;
        font-size: {size}px;
    ">{word}</div>
    """
st.markdown(background_html, unsafe_allow_html=True)


# --- Sidebar ---
with st.sidebar:
    st.markdown('<div class="sidebar-counselor-title">Valluvar is your Counsellor</div>', unsafe_allow_html=True)
    
    # Load and display the image directly if it exists
    if os.path.exists("thiruvalluvar.jpg"):
        st.image("thiruvalluvar.jpg", use_container_width=True, caption="Universal Teacher")
    elif os.path.exists("assets/icon.png"):
        st.image("assets/icon.png", use_container_width=True, caption="Symbol of Wisdom")
    
    st.markdown("---")
    st.markdown("### 💡 Guidance for You:")
    
    sample_queries = [
        ("🎓 Education", "What does Kural say about learning?"),
        ("💰 Wealth", "How to manage money wisely?"),
        ("❤️ Love", "What is the sign of true love?"),
        ("🤝 Friendship", "How to choose good friends?"),
        ("🌱 Farming", "உழவு பற்றி என்ன சொல்கிறது?")
    ]

    for emoji, text in sample_queries:
        st.markdown(f'''
        <div class="sample-q">
            <b>{emoji}</b><br>
            <i>"{text}"</i>
        </div>
        ''', unsafe_allow_html=True)

    st.markdown("---")
    if st.button("🔄 Start New Conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.agent = get_thirukural_agent()
        st.rerun()


# --- Header Section ---
col1, col2 = st.columns([0.8, 10]) 
with col1:
    if os.path.exists("assets/icon.png"):
        st.image("assets/icon.png", width=90)
    else:
        st.markdown("## 📜")

with col2:
    st.markdown('<div class="main-header">Thirukural Scholar</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Ancient Wisdom for Modern Life</div>', unsafe_allow_html=True)

# --- Logic ---

# Initialize Agent
if "agent" not in st.session_state:
    with st.spinner("Opening the Ancient Manuscripts..."):
        try:
            st.session_state.agent = get_thirukural_agent()
        except Exception as e:
            st.error(f"Failed to initialize: {e}")

# Display Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    if message["role"] == "user":
        with st.chat_message("user"):
            st.markdown(message["content"])
    else:
        avatar = None
        if os.path.exists("thiruvalluvar.jpg"):
            avatar = "thiruvalluvar.jpg"
        elif os.path.exists("assets/icon.png"):
            avatar = "assets/icon.png"
            
        with st.chat_message("assistant", avatar=avatar):
             st.markdown(f'<div class="explanation-text">{message["content"]}</div>', unsafe_allow_html=True)

# User Input
if prompt := st.chat_input("Ask about Life, Love, Politics, Confusion and anything that troubles you"):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Prepare LangChain messages
    langchain_msgs = []
    history_window = st.session_state.messages[-10:] 
    for msg in history_window:
         if msg["role"] == "user":
             langchain_msgs.append(HumanMessage(content=msg["content"]))
         else:
             langchain_msgs.append(AIMessage(content=msg["content"]))
             
    # INSTRUCTION INJECTION
    if langchain_msgs and isinstance(langchain_msgs[-1], HumanMessage):
        original_content = langchain_msgs[-1].content
        instruction = """
        (IMPORTANT SYSTEM INSTRUCTION: 
        1. When quoting a Kural, wrap it in <div class="kural-highlight">...</div> HTML tags. This is CRITICAL for display.
        2. Do NOT use headers like "Tamil Explanation" or "English Explanation". Just provide the text naturally.
        3. Provide the Tamil explanation first, then the English explanation immediately after.
        4. Keep the explanation flowing naturally.
        5. AT THE END of your response, provide 3 related follow-up questions or themes.
           - If the user's input was in Tamil, use the conversational header "**அடுத்து இதைப் பற்றி பேசலாமா?**" and list them in Tamil.
           - If the user's input was in English, use the conversational header "**Shall we discuss this next?**" and list them in English.
        6. CRITICAL: If the user asks one of these follow-up questions, you MUST perform a NEW SEARCH using the tool. Do not just repeat the previous Kural. Find new ones.)
        """
        langchain_msgs[-1].content = f"{original_content} {instruction}"
    
    # Generate Response
    if "agent" in st.session_state:
        avatar = None
        if os.path.exists("thiruvalluvar.jpg"):
            avatar = "thiruvalluvar.jpg"
        elif os.path.exists("assets/icon.png"):
            avatar = "assets/icon.png"
            
        with st.chat_message("assistant", avatar=avatar):
            with st.spinner("The Scholar is thinking..."):
                try:
                    result = st.session_state.agent.invoke({"messages": langchain_msgs})
                    output = result["messages"][-1].content
                    
                    st.markdown(f'<div class="explanation-text">{output}</div>', unsafe_allow_html=True)
                    st.session_state.messages.append({"role": "assistant", "content": output})
                except Exception as e:
                    st.error(f"An error occurred: {e}")
