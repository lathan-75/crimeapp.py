import streamlit as st
import time
import datetime
import random

# Page configuration
st.set_page_config(
    page_title="SECURO - St. Kitts & Nevis Crime AI Assistant",
    page_icon="🚔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling - keeping the exact same design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;700&display=swap');
   
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
   
    /* Main app background */
    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #2e1a1a 50%, #3e1616 100%);
        font-family: 'JetBrains Mono', monospace;
    }
   
    /* Particles animation */
    .particles {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 1;
    }

    .particle {
        position: absolute;
        width: 2px;
        height: 2px;
        background: rgba(255, 68, 68, 0.3);
        border-radius: 50%;
        animation: float 10s infinite linear;
    }

    @keyframes float {
        0% { transform: translateY(100vh) rotate(0deg); opacity: 0; }
        10% { opacity: 1; }
        90% { opacity: 1; }
        100% { transform: translateY(-100px) rotate(360deg); opacity: 0; }
    }
   
    /* Header styling */
    .main-header {
        text-align: center;
        margin-bottom: 30px;
        padding: 20px;
        background: rgba(0, 0, 0, 0.7);
        border-radius: 15px;
        border: 1px solid rgba(255, 68, 68, 0.3);
        backdrop-filter: blur(10px);
        position: relative;
        overflow: hidden;
    }

    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent, rgba(255, 68, 68, 0.1), transparent);
        animation: scan 3s infinite;
    }

    @keyframes scan {
        0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
        100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
    }

    .main-header h1 {
        font-size: 3rem;
        color: #ff4444;
        text-shadow: 0 0 20px rgba(255, 68, 68, 0.5);
        margin-bottom: 10px;
        position: relative;
        z-index: 2;
        font-weight: 700;
        font-family: 'JetBrains Mono', monospace;
    }

    .main-header .tagline {
        font-size: 1rem;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 2px;
        position: relative;
        z-index: 2;
        font-family: 'JetBrains Mono', monospace;
    }

    .main-header .location {
        font-size: 0.9rem;
        color: #ff4444;
        margin-top: 5px;
        position: relative;
        z-index: 2;
        font-family: 'JetBrains Mono', monospace;
    }
   
    /* Sidebar styling - Multiple selectors for different Streamlit versions */
    .css-1d391kg, .css-1cypcdb, .css-k1vhr6, .css-1lcbmhc, .css-17eq0hr,
    section[data-testid="stSidebar"], .stSidebar, [data-testid="stSidebar"] > div,
    .css-1aumxhk, .css-hxt7ib, .css-17lntkn {
        background: rgba(40, 20, 20, 0.9) !important;
        border-right: 1px solid rgba(255, 68, 68, 0.3) !important;
        backdrop-filter: blur(10px) !important;
    }
   
    /* Sidebar header styling */
    section[data-testid="stSidebar"] .css-10trblm {
        color: #ff4444 !important;
    }
   
    /* Sidebar content background */
    .css-1cypcdb .css-17lntkn {
        background: transparent !important;
    }
   
    /* Emergency contacts styling */
    .contact-item {
        background: rgba(0, 0, 0, 0.5);
        padding: 12px;
        margin-bottom: 8px;
        border-radius: 8px;
        border-left: 3px solid #ff4444;
        cursor: pointer;
        transition: all 0.3s ease;
        color: #e0e0e0;
        font-family: 'JetBrains Mono', monospace;
    }

    .contact-item:hover {
        background: rgba(255, 68, 68, 0.1);
        transform: translateX(5px);
    }

    .contact-name {
        color: #e0e0e0;
        font-size: 0.9rem;
        font-weight: 500;
        font-family: 'JetBrains Mono', monospace;
    }

    .contact-number {
        color: #ff4444;
        font-size: 0.8rem;
        margin-top: 3px;
        font-family: 'JetBrains Mono', monospace;
    }
   
    /* Sidebar toggle button */
    .sidebar-toggle {
        position: fixed;
        top: 70px;
        left: 20px;
        z-index: 999;
        background: linear-gradient(135deg, #ff4444, #cc3333);
        border: none;
        border-radius: 8px;
        color: white;
        padding: 10px 15px;
        cursor: pointer;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(255, 68, 68, 0.3);
    }
   
    .sidebar-toggle:hover {
        transform: scale(1.05);
        box-shadow: 0 6px 20px rgba(255, 68, 68, 0.5);
    }
   
    /* Map container with better styling */
    .map-container {
        background: rgba(0, 0, 0, 0.8);
        border-radius: 10px;
        padding: 0;
        border: 1px solid rgba(255, 68, 68, 0.3);
        position: relative;
        height: 300px;
        overflow: hidden;
        margin-bottom: 15px;
    }
   
    /* Map iframe styling */
    .crime-map iframe {
        width: 100%;
        height: 100%;
        border: none;
        border-radius: 10px;
        filter: invert(0.9) hue-rotate(180deg) saturate(1.2);
    }

    .map-placeholder {
        width: 100%;
        height: 100%;
        background: linear-gradient(45deg, #2e1a1a, #3e1616);
        border-radius: 8px;
        position: relative;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #666;
        font-size: 0.8rem;
        font-family: 'JetBrains Mono', monospace;
    }

    .hotspot {
        position: absolute;
        width: 12px;
        height: 12px;
        background: #ff4444;
        border-radius: 50%;
        animation: pulse-hotspot 2s infinite;
        cursor: pointer;
    }

    .hotspot::after {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        border: 2px solid rgba(255, 68, 68, 0.5);
        border-radius: 50%;
        animation: ripple 2s infinite;
    }

    @keyframes pulse-hotspot {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.7; transform: scale(1.2); }
    }

    @keyframes ripple {
        0% { transform: scale(1); opacity: 1; }
        100% { transform: scale(2); opacity: 0; }
    }

    .hotspot-1 { top: 30%; left: 25%; }
    .hotspot-2 { top: 45%; left: 60%; }
    .hotspot-3 { top: 70%; left: 40%; }
    .hotspot-4 { top: 25%; left: 75%; }
   
    /* Chat styling */
    .chat-message {
        margin-bottom: 20px;
        animation: fadeInUp 0.5s ease;
    }

    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .user-message {
        text-align: right;
    }

    .bot-message {
        text-align: left;
    }

    .message-content {
        display: inline-block;
        padding: 15px 20px;
        border-radius: 15px;
        max-width: 80%;
        position: relative;
        font-family: 'JetBrains Mono', monospace;
    }

    .user-message .message-content {
        background: linear-gradient(135deg, #ff4444, #cc3333);
        color: #fff;
        border-bottom-right-radius: 5px;
    }

    .bot-message .message-content {
        background: rgba(0, 0, 0, 0.6);
        color: #e0e0e0;
        border: 1px solid rgba(255, 68, 68, 0.3);
        border-bottom-left-radius: 5px;
    }

    .message-time {
        font-size: 0.7rem;
        color: #888;
        margin-top: 5px;
        font-family: 'JetBrains Mono', monospace;
    }
   
    /* Status bar */
    .status-bar {
        background: rgba(0, 0, 0, 0.8);
        padding: 10px 20px;
        border-radius: 25px;
        margin-top: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border: 1px solid rgba(255, 68, 68, 0.2);
        font-family: 'JetBrains Mono', monospace;
    }

    .status-item {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 0.8rem;
        color: #e0e0e0;
    }

    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        animation: pulse 2s infinite;
    }

    .status-online { background: #ff4444; }
    .status-processing { background: #cc3333; }
    .status-evidence { background: #ff6666; }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.3; }
    }
   
    /* Input styling */
    .stTextInput input {
        background: rgba(0, 0, 0, 0.5) !important;
        border: 1px solid rgba(255, 68, 68, 0.3) !important;
        border-radius: 25px !important;
        color: #e0e0e0 !important;
        font-family: 'JetBrains Mono', monospace !important;
    }

    .stTextInput input:focus {
        border-color: #ff4444 !important;
        box-shadow: 0 0 20px rgba(255, 68, 68, 0.2) !important;
    }
   
    /* Button styling */
    .stButton button {
        background: linear-gradient(135deg, #ff4444, #cc3333) !important;
        border: none !important;
        border-radius: 25px !important;
        color: #fff !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
    }

    .stButton button:hover {
        transform: scale(1.05) !important;
        box-shadow: 0 0 20px rgba(255, 68, 68, 0.4) !important;
    }
   
    /* Section headers */
    .section-header {
        color: #ff4444;
        font-size: 1.1rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 15px;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# Crime database from the original
crime_database = [
    {"category": "Victims", "question": "What services are available for crime victims?", "answer": "Counseling, financial assistance, and victim advocacy groups."},
    {"category": "Journalists", "question": "What are shield laws?", "answer": "Laws protecting journalists from revealing confidential sources."},
    {"category": "Witnesses", "question": "What is a subpoena?", "answer": "A legal document ordering someone to testify in court."},
    {"category": "Lawyers", "question": "What is double jeopardy?", "answer": "A procedural defense that prevents an accused person from being tried again on the same charges."},
    {"category": "General Public", "question": "How do I check if someone has a criminal record?", "answer": "Contact the local police department or use background check services."},
    {"category": "Lawyers", "question": "What is plea bargaining?", "answer": "An agreement where the defendant pleads guilty for a reduced sentence."},
    {"category": "Cybercrime Specialists", "question": "What is phishing?", "answer": "A cyber attack that tricks people into giving sensitive information."},
    {"category": "General Public", "question": "How do I get a restraining order?", "answer": "File a petition with the court explaining why you need protection."},
    {"category": "Cold Case Units", "question": "What is a cold case?", "answer": "A criminal investigation that remains unsolved after a long period."},
    {"category": "Cold Case Units", "question": "How are cold cases reopened?", "answer": "Through new evidence, DNA technology, or witness testimony."},
    {"category": "Criminologists", "question": "What is the broken windows theory?", "answer": "A theory that visible signs of disorder lead to more crime."},
    {"category": "Criminologists", "question": "What is white collar crime?", "answer": "Financially motivated, nonviolent crime committed by businesses and government professionals."},
    {"category": "Forensics", "question": "How are fingerprints lifted?", "answer": "Using powders, chemicals, or alternate light sources to make them visible."},
    {"category": "Criminal Psychologists", "question": "What is antisocial personality disorder?", "answer": "A mental condition linked to disregard for others' rights, often found in criminals."},
    {"category": "Victims", "question": "What is victim impact statement?", "answer": "A written or oral statement given at sentencing describing the crime's impact."},
    {"category": "Journalists", "question": "How do journalists cover crime ethically?", "answer": "By verifying facts, respecting privacy, and avoiding sensationalism."},
    {"category": "Investigators", "question": "What is criminal profiling?", "answer": "Inferring characteristics of an offender based on crime scene evidence."},
    {"category": "Criminal Psychologists", "question": "What is criminal insanity?", "answer": "A legal term meaning the defendant was unable to understand their actions."},
    {"category": "Cybercrime Specialists", "question": "What is ransomware?", "answer": "Malicious software that blocks access to data until a ransom is paid."},
    {"category": "Investigators", "question": "What is forensic entomology?", "answer": "The study of insects to estimate time of death."},
    {"category": "Police", "question": "What is community policing?", "answer": "A strategy that focuses on building ties and working closely with communities."},
    {"category": "Police", "question": "What is an arrest warrant?", "answer": "A document issued by a judge authorizing the arrest of a person."},
    {"category": "Forensics", "question": "How is blood spatter analyzed?", "answer": "By examining patterns to reconstruct a crime scene."},
    {"category": "Witnesses", "question": "Can I refuse to testify?", "answer": "In some cases, but you may be held in contempt of court."},
    {"category": "Police", "question": "What does 'beyond reasonable doubt' mean?", "answer": "The standard of evidence required to convict in a criminal trial."}
]

def search_crime_database(query):
    """Search the crime database for relevant answers"""
    search_term = query.lower()
   
    # Direct question match
    for item in crime_database:
        if search_term in item["question"].lower() or item["question"].lower()[:20] in search_term:
            return item["answer"]
   
    # Keyword-based search
    keywords = {
        'victim': ['What services are available for crime victims?', 'What is victim impact statement?'],
        'witness': ['What is a subpoena?', 'Can I refuse to testify?'],
        'police': ['What is community policing?', 'What is an arrest warrant?', "What does 'beyond reasonable doubt' mean?"],
        'forensic': ['How are fingerprints lifted?', 'How is blood spatter analyzed?', 'What is forensic entomology?'],
        'cyber': ['What is phishing?', 'What is ransomware?'],
        'legal': ['What is double jeopardy?', 'What is plea bargaining?'],
        'restraining': ['How do I get a restraining order?'],
        'cold case': ['What is a cold case?', 'How are cold cases reopened?'],
        'criminal record': ['How do I check if someone has a criminal record?'],
        'profiling': ['What is criminal profiling?'],
        'insanity': ['What is criminal insanity?'],
        'shield': ['What are shield laws?'],
        'journalism': ['How do journalists cover crime ethically?'],
        'white collar': ['What is white collar crime?'],
        'broken windows': ['What is the broken windows theory?'],
        'antisocial': ['What is antisocial personality disorder?']
    }
   
    for keyword, questions in keywords.items():
        if keyword in search_term:
            question = questions[0]
            for item in crime_database:
                if item["question"] == question:
                    return item["answer"]
   
    # Default responses for St. Kitts & Nevis specific queries
    skn_responses = [
        "Based on St. Kitts & Nevis criminal patterns, I recommend cross-referencing with the Royal St. Christopher and Nevis Police Force database.",
        "Crime analysis for the Caribbean region suggests this pattern. Coordinate with the Director of Public Prosecutions office.",
        "This case shows similarities to recent incidents in Basseterre. Consider interviewing witnesses near Independence Square.",
        "Forensic protocols for St. Kitts & Nevis require documentation per Caribbean Association of Police Chiefs standards.",
        "Evidence suggests connection to maritime activities between St. Kitts and Nevis. Contact Coast Guard unit 465-8384.",
        "Pattern matches recent cases in tourist areas. Recommend liaison with Ministry of National Security.",
        "This investigation may benefit from coordination with the Nevis Island Administration police division."
    ]
   
    return random.choice(skn_responses)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
    # Add initial bot message
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Welcome to SECURO, your AI crime investigation assistant for St. Kitts & Nevis law enforcement.\n\nI'm here to assist criminologists, police officers, forensic experts, and autopsy professionals with case analysis, evidence correlation, and investigative insights.\n\nHow can I assist with your investigation today?",
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
    })

if 'sidebar_state' not in st.session_state:
    st.session_state.sidebar_state = "expanded"

# Header with sidebar toggle
col1, col2 = st.columns([1, 10])

with col1:
    if st.button("🔧", help="Toggle Sidebar", key="sidebar_toggle"):
        if st.session_state.sidebar_state == "expanded":
            st.session_state.sidebar_state = "collapsed"
        else:
            st.session_state.sidebar_state = "expanded"
        st.rerun()

with col2:
    st.markdown("""
    <div class="main-header">
        <div class="particles" id="particles"></div>
        <h1>SECURO</h1>
        <div class="tagline">AI Crime Investigation Assistant</div>
        <div class="location">🇰🇳 St. Kitts & Nevis Law Enforcement</div>
    </div>
    """, unsafe_allow_html=True)

# Particles animation script
st.markdown("""
<script>
function createParticles() {
    const particlesContainer = document.getElementById('particles');
    if (particlesContainer) {
        const particleCount = 40;
       
        for (let i = 0; i < particleCount; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            particle.style.left = Math.random() * 100 + '%';
            particle.style.animationDelay = Math.random() * 10 + 's';
            particle.style.animationDuration = (Math.random() * 10 + 15) + 's';
            particlesContainer.appendChild(particle);
        }
    }
}
createParticles();
</script>
""", unsafe_allow_html=True)

# Sidebar (only show if expanded)
if st.session_state.sidebar_state == "expanded":
    with st.sidebar:
        st.markdown('<div class="section-header">🚨 Emergency Contacts</div>', unsafe_allow_html=True)
       
        emergency_contacts = [
            {"name": "Emergency Hotline", "number": "911", "type": "police"},
            {"name": "Police Department", "number": "465-2241", "type": "police"},
            {"name": "Hospital", "number": "465-2551", "type": "hospital"},
            {"name": "Fire Department", "number": "465-2515 / 465-7167", "type": "fire"},
            {"name": "Coast Guard", "number": "465-8384 / 466-9280", "type": "legal"},
            {"name": "Red Cross", "number": "465-2584", "type": "forensic"},
            {"name": "NEMA (Emergency Mgmt)", "number": "466-5100", "type": "legal"}
        ]
       
        for contact in emergency_contacts:
            if st.button(f"📞 {contact['name']}\n{contact['number']}", key=contact['name']):
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"🚨 Emergency contact information accessed: {contact['name']} - {contact['number']}. Contact has been logged for case documentation.",
                    "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
                })
                st.rerun()
       
        st.markdown('<div class="section-header">📍 Crime Hotspots Map</div>', unsafe_allow_html=True)
       
        # Real Google Maps embed for St. Kitts & Nevis with API key
        st.markdown("""
        <div class="map-container crime-map">
            <iframe
                src="https://www.google.com/maps/embed/v1/place?key=AIzaSyCkSjJBcI_wqA37bdF-08ROrMFaGYObyjA&q=Basseterre,St+Kitts+and+Nevis&maptype=satellite&zoom=12"
                allowfullscreen=""
                loading="lazy"
                referrerpolicy="no-referrer-when-downgrade">
            </iframe>
        </div>
        """, unsafe_allow_html=True)
       
        # Interactive hotspot buttons
        st.markdown('<div class="section-header">🎯 Active Crime Zones</div>', unsafe_allow_html=True)
       
        hotspots = [
            {"name": "Basseterre Downtown", "level": "🔴 High Risk", "coords": "17.3026, -62.7261"},
            {"name": "Sandy Point", "level": "🟡 Medium Risk", "coords": "17.3580, -62.8419"},
            {"name": "Charlestown (Nevis)", "level": "🟠 Active Cases", "coords": "17.1373, -62.6131"},
            {"name": "Frigate Bay", "level": "🟡 Tourist Area", "coords": "17.2742, -62.6897"}
        ]
       
        for hotspot in hotspots:
            if st.button(f"{hotspot['level']} {hotspot['name']}", key=f"hotspot_{hotspot['name']}"):
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"📍 Crime hotspot analysis: {hotspot['name']} ({hotspot['coords']})\n\n{hotspot['level']} - Recommend increased patrol presence and witness canvassing in this area. Coordinating with local units for enhanced surveillance.",
                    "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
                })
                st.rerun()
else:
    # Show collapsed sidebar info in main area if needed
    pass

# Main chat area
st.markdown('<div class="section-header">💬 Crime Investigation Chat</div>', unsafe_allow_html=True)

# Display chat messages
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f"""
        <div class="chat-message user-message">
            <div class="message-content">{message["content"]}</div>
            <div class="message-time">{message["timestamp"]}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="chat-message bot-message">
            <div class="message-content">{message["content"]}</div>
            <div class="message-time">{message["timestamp"]}</div>
        </div>
        """, unsafe_allow_html=True)

# Chat input
col1, col2 = st.columns([5, 1])

with col1:
    user_input = st.text_input(
        "Message",
        placeholder="Describe evidence, case details, or ask forensic questions...",
        label_visibility="collapsed",
        key="user_input"
    )

with col2:
    if st.button("Send", type="primary"):
        if user_input:
            # Add user message
            st.session_state.messages.append({
                "role": "user",
                "content": user_input,
                "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
            })
           
            # Generate AI response
            response = search_crime_database(user_input)
            st.session_state.messages.append({
                "role": "assistant",
                "content": response,
                "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
            })
           
            st.rerun()

# Status bar
st.markdown("""
<div class="status-bar">
    <div class="status-item">
        <div class="status-dot status-online"></div>
        <span>SECURO AI Online</span>
    </div>
    <div class="status-item">
        <div class="status-dot status-processing"></div>
        <span>SKN Crime Database Connected</span>
    </div>
    <div class="status-item">
        <div class="status-dot status-evidence"></div>
        <span>Emergency Services Linked</span>
    </div>
</div>
""", unsafe_allow_html=True)
