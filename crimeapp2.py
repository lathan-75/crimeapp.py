import streamlit as st
import datetime
import json
import requests
import matplotlib.pyplot as plt
import pandas as pd
import folium
from streamlit_folium import folium_static
import hashlib
import time
import os
import google.generativeai as genai
import chromadb

GOOGLE_API_KEY = "AIzaSyBlAiRqnNHmm-Hfu8dCAx6dlVMROQ-c180" 
genai.configure(api_key=GOOGLE_API_KEY)

# Initialize the AI model
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(
    page_title="SECURO - Crime Mitigation AI Chat Bot",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="🤖",
    menu_items=None
)
st.markdown("""
    <style>
    /* Basic black theme for simplified view */
    .main, .main .block-container, .stApp {
        background-color: #000000 !important;
        color: #ffffff !important;
        font-family: 'Times New Roman', Times, serif !important;
    }
    h1, h2, h3, h4 {
        color: #FFFF00 !important; /* Yellow for titles */
        font-family: 'Times New Roman', Times, serif !important;
    }
    .stChatInput > div {
        background-color: #1a1a1a !important;
        border: 1px solid #333333 !important;
    }
    .stChatInput input {
        background-color: transparent !important;
        color: #ffffff !important;
    }
    .stButton > button {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        border: 1px solid #333333 !important;
    }
    .stButton > button:hover {
        background-color: #333333 !important;
    }
    /* Custom chat bubbles */
    .user-message, .bot-message {
        margin-bottom: 1rem;
        clear: both;
        overflow: hidden;
    }
    .user-bubble {
        background: #ffffff !important;
        color: #000000 !important;
        padding: 12px 16px !important;
        border-radius: 18px 18px 4px 18px !important;
        max-width: 70% !important;
        float: right;
        font-family: 'Times New Roman', Times, serif !important;
        box-shadow: 0 2px 8px rgba(255, 255, 255, 0.2) !important;
    }
    .bot-bubble {
        background: #2c2c2c !important;
        color: #ffffff !important;
        padding: 12px 16px !important;
        border-radius: 18px 18px 18px 4px !important;
        max-width: 75% !important;
        float: left;
        font-family: 'Times New Roman', Times, serif !important;
        box-shadow: 0 2px 8px rgba(255, 255, 255, 0.1) !important;
    }
    </style>
""", unsafe_allow_html=True)

class UserAuthentication:
    def __init__(self):
        # In a simplified version, we'll just use a default 'admin' user for demonstration
        if "users_db" not in st.session_state:
            st.session_state.users_db = {
                "admin": {
                    "password": self.hash_password("adminpass"),
                    "role": "Senior Criminologist",
                    "access_level": 5
                }
            }

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def login(self, username, password):
        if username not in st.session_state.users_db:
            return False, "Professional credentials not found"
        if st.session_state.users_db[username]["password"] != self.hash_password(password):
            return False, "Invalid credentials"

        user_data = st.session_state.users_db[username]
        st.session_state.logged_in = True
        st.session_state.current_user = username
        st.session_state.user_role = user_data["role"]
        st.session_state.access_level = user_data["access_level"]
        return True, "Professional access granted"

# --- RAG Components Integration ---
# Ensure ChromaDB client and collection are initialized only once
@st.cache_resource
def initialize_chromadb(csv_filename):
    client = chromadb.Client()
    collection_name = "securo_chatbot_enhanced"

    try:
        client.delete_collection(collection_name)
        print("🧹 Cleaned up old collection")
    except Exception as e:
        print(f"No old collection to clean or error deleting: {e}")

    rag_documents = []
    try:
        df_rag = pd.read_csv(csv_filename)
        if 'question' in df_rag.columns and 'answer' in df_rag.columns:
            rag_documents = (df_rag['question'] + " " + df_rag['answer']).tolist()
            collection = client.create_collection(name=collection_name)
            collection.add(
                documents=rag_documents,
                ids=[str(i) for i in range(len(rag_documents))]
            )
            print(f"✅ Smart memory ready with {len(rag_documents)} pieces of knowledge from '{csv_filename}'!")
            return collection
        else:
            st.error(f"Error: '{csv_filename}' must contain 'question' and 'answer' columns for RAG.")
            return None
    except FileNotFoundError:
        st.error(f"Error: RAG CSV file '{csv_filename}' not found. Please ensure it's in the same directory.")
        return None
    except Exception as e:
        st.error(f"Error loading RAG data from '{csv_filename}': {e}")
        return None

# Initialize collection using Streamlit's cache_resource
collection = initialize_chromadb("securo_crime.csv")

# Prompt template for better responses
def create_crime_mitigation_prompt(user_question, relevant_context):
    """Create a smart prompt for the AI using our knowledge"""
    
    prompt = f"""You are a helpful and friendly St. Kitts & Nevis crime mitigation assistant. You have access to specific crime prevention and mitigation information and you should use this information to provide accurate, helpful answers. Speak in an informative and warm, professional tone.

CRIME MITIGATION KNOWLEDGE (from our database):
{relevant_context}

USER QUESTION: {user_question}

INSTRUCTIONS:
- Use the crime mitigation knowledge provided to answer the question.
- Be warm and professional about crime mitigation.
- Include specific details like statistics, locations of police stations, and lawyer services if available in the context.
- If the information isn't in your provided knowledge, say so politely and professionally, and suggest other ways you can help.
- Keep your answer helpful and concise, typically 3-4 paragraphs.
- Use a warm, welcoming tone, but maintain professionalism.
- Address the user as "Officer" if the context implies a professional setting (which it does in this app).

ANSWER:"""
    
    return prompt

def ask_enhanced_chatbot(question):
    """Your super smart crime mitigation chatbot with Google AI and RAG!"""
    print(f"🤔 User asked: '{question}'")
    print("🔍 Searching smart memory...")
    
    if collection is None:
        return "Officer, my knowledge base is not fully loaded. Please ensure the 'securo_crime.csv' file is correctly set up."

    try:
        results = collection.query(
            query_texts=[question],
            n_results=3 # Get top 3 relevant pieces
        )
        
        relevant_info = "\n\n".join(results['documents'][0])
        print("✅ Found relevant information!")
        
        prompt_for_gemini = create_crime_mitigation_prompt(question, relevant_info)
        
        print("🤖 Google AI is thinking...")
        response = model.generate_content(prompt_for_gemini)
        answer = response.text
        
        print("\n🎯 Enhanced AI Response:")
        print("=" * 50)
        print(answer)
        print("=" * 50)
        
        return answer
            
    except Exception as e:
        st.error(f"❌ Error during enhanced AI response generation: {e}")
        return "Officer, I'm experiencing a technical issue with my advanced response system. Please try again or rephrase your inquiry."


class CriminologyProfessionalBot:
    def __init__(self):
        # The Gemini API is implicitly used by ask_enhanced_chatbot
        self.load_crime_data("securo_crime.csv") # Load data for charting/mapping specifically

        self.professional_contacts = {
            "police_hq": {
                "name": "Royal St. Christopher and Nevis Police Force HQ",
                "phone": "(869) 465-2241",
                "email": "info@police.kn",
                "address": "Cayon Street, Basseterre",
                "departments": ["CID", "Traffic", "Community Policing", "Narcotics"]
            },
            "forensics": {
                "name": "Police Forensic Unit",
                "phone": "(869) 465-2241 ext. 234",
                "specialties": ["DNA Analysis", "Ballistics", "Digital Forensics", "Crime Scene Processing"]
            },
        }

        self.legal_framework = {
            "primary_legislation": {
                "criminal_code": {
                    "title": "Criminal Code (St. Christopher and Nevis)",
                    "key_sections": {
                        "homicide": "Sections 87-102",
                        "assault": "Sections 56-74",
                        "theft": "Sections 201-250",
                        "fraud": "Sections 251-280",
                        "drug_offenses": "Drug Prevention of Misuse Act",
                        "domestic_violence": "Domestic Violence Act 2020"
                    }
                },
            }
        }

        self.investigation_protocols = {
            "crime_scene": {
                "initial_response": [
                    "Secure the perimeter",
                    "Document initial observations",
                    "Identify and separate witnesses",
                    "Call for appropriate specialists",
                    "Establish command post"
                ],
                "documentation": [
                    "Photography (wide, medium, close-up)",
                    "Sketch mapping",
                    "Evidence log",
                    "Witness statements",
                    "Environmental conditions"
                ]
            },
        }

    def load_crime_data(self, csv_file_path):
        """Loads crime data specifically for charts and maps, separate from RAG knowledge base."""
        try:
            self.crime_df = pd.read_csv(csv_file_path)
            if 'Date' in self.crime_df.columns:
                self.crime_df['Date'] = pd.to_datetime(self.crime_df['Date'], errors='coerce')
                self.crime_df.dropna(subset=['Date'], inplace=True) 
                self.crime_df['Year'] = self.crime_df['Date'].dt.year
            else:
                st.warning(f"'{csv_file_path}' does not have a 'Date' column. Charts by year will not function.")
                self.crime_df['Year'] = datetime.datetime.now().year # Default year for mapping if no date column

            st.success(f"Crime data for charts/maps loaded successfully from {csv_file_path}")
        except FileNotFoundError:
            st.error(f"Error: CSV file for charts/maps not found at {csv_file_path}. Please ensure it's in the same directory.")
            self.crime_df = pd.DataFrame() 
        except Exception as e:
            st.error(f"Error loading crime data for charts/maps: {e}")
            self.crime_df = pd.DataFrame()

    def get_legal_reference(self, query):
        query_lower = query.lower()
        legal_response = "**LEGAL REFERENCE - ST. KITTSON & NEVIS**\n\n"
        if any(word in query_lower for word in ["homicide", "murder", "killing"]):
            legal_response += """**HOMICIDE OFFENSES (Criminal Code Sections 87-102)**
            **Key Charges:**
            • Murder: Life imprisonment (Section 87)
            • Manslaughter: Up to 25 years (Section 92)
            • Infanticide: Up to 3 years (Section 95)
            **Critical Procedures:**
            • Mandatory autopsy required
            • Forensic pathologist engagement essential
            • Scene preservation: minimum 72 hours
            • Crown counsel consultation before charging
            **Next Step:** Secure scene and contact forensic pathologist immediately.
            """
        elif any(word in query_lower for word in ["theft", "stealing", "larceny"]):
            legal_response += """**THEFT OFFENSES (Criminal Code Sections 201-250)**
            **Key Charges:**
            • Theft: Up to 7 years imprisonment (Section 201)
            • Burglary: Up to 14 years (Section 206)
            • Robbery: Up to life imprisonment (Section 209)
            **Critical Procedures:**
            • Document scene for forced entry/exit
            • Collect fingerprints and tool marks
            • Interview witnesses for suspect descriptions/modus operandi
            • Check for CCTV footage
            **Next Step:** Initiate thorough scene processing and victim/witness statements.
            """
        else:
            legal_response += "Officer, I can provide legal guidance on various sections of the Criminal Code. Please specify the area of law you are inquiring about (e.g., 'assault law', 'drug offenses', 'domestic violence')."
        return legal_response

    def get_professional_directory(self):
        return """**PROFESSIONAL CONTACT DIRECTORY**
        **ROYAL ST. CHRISTOPHER AND NEVIS POLICE FORCE HQ**
        • Phone: (869) 465-2241
        • Address: Cayon Street, Basseterre
        • Departments: CID, Traffic, Community Policing, Narcotics

        **POLICE FORENSIC UNIT**
        • Phone: (869) 465-2241 ext. 234
        • Services: DNA, Ballistics, Digital Forensics, Crime Scene Processing

        **EASTERN CARIBBEAN SUPREME COURT - ST. KITTS CIRCUIT**
        • Phone: (869) 465-2366
        • Address: Government Road, Basseterre

        **MAGISTRATE'S COURT**
        • Phone: (869) 465-2521
        • Sessions: Criminal, Civil, Traffic

        **DIRECTOR OF PUBLIC PROSECUTIONS OFFICE**
        • Phone: (869) 467-1000
        • Services: Case Review, Legal Advice, Prosecution Oversight
        """

    def get_investigation_protocol(self, query):
        query_lower = query.lower()
        if any(word in query_lower for word in ["crime scene", "scene processing", "initial response"]):
            return """**CRIME SCENE INITIAL RESPONSE & DOCUMENTATION PROTOCOLS**
            **INITIAL RESPONSE**
            • Secure the perimeter immediately to prevent contamination.
            • Document initial observations (e.g., weather, time, light).
            • Identify and separate witnesses; obtain preliminary statements.
            • Call for appropriate specialists (e.g., forensics, K9).
            • Establish a clear command post for coordination.

            **DOCUMENTATION**
            • Photography: wide, medium, close-up shots of scene and evidence.
            • Sketch mapping: detailed diagrams with measurements.
            • Evidence log: chronological record of all collected items.
            • Witness statements: detailed accounts from all relevant parties.
            • Record environmental conditions that might affect evidence.
            **Officer, rapid and thorough scene management is paramount.**
            """
        elif any(word in query_lower for word in ["evidence handling", "chain of custody", "collection"]):
            return """**EVIDENCE HANDLING & CHAIN OF CUSTODY PROTOCOLS**
            **COLLECTION**
            • Use appropriate, sterile collection tools for each type of evidence.
            • Wear personal protective equipment to prevent contamination.
            • Maintain strict chain of custody from collection to analysis.
            • Use proper packaging (e.g., paper bags for biological, sealed containers).
            • Label all evidence clearly with case number, date, time, location found, and collecting officer's details.

            **STORAGE**
            • Store evidence in a climate-controlled, secure environment.
            • Access to evidence storage must be controlled and logged.
            • Conduct regular inventories to ensure accountability.
            • Prevent cross-contamination by maintaining segregation.
            **Officer, proper evidence handling can make or break your case in court.**
            """
        else:
            return """**GENERAL INVESTIGATION PROTOCOLS**
            **CASE INITIATION**
            • Complaint/report received and assessed
            • Case file creation with unique identifier
            • Resource allocation and team assignment
            • Investigation plan development

            **INVESTIGATION PROCESS**
            • Evidence collection and preservation
            • Witness interviews and statements
            • Suspect identification and questioning
            • Expert consultations as needed
            • Comprehensive case file compilation

            **CASE COMPLETION**
            • Evidence review and analysis
            • Prosecutor consultation
            • Charge recommendations
            • Court file preparation
            • Proper case closure documentation
            **Officer, for specific protocols consult the Operations Manual or contact your supervisor.**
            """

    def create_crime_statistics_chart(self, year):
        if self.crime_df.empty or 'Year' not in self.crime_df.columns:
            return None, "No crime data loaded or 'Year' column missing to create charts."
        
        yearly_data = self.crime_df[self.crime_df['Year'] == year]

        if yearly_data.empty:
            available_years = self.crime_df['Year'].unique()
            return None, f"No crime data available for {year}. Available years: {', '.join(map(str, available_years))}"

        crime_categories = yearly_data['Crime Type'].value_counts()
        
        if crime_categories.empty:
            return None, f"No specific crime type data available for {year}."

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        fig.patch.set_facecolor('black')

        categories = crime_categories.index.tolist()
        values = crime_categories.values.tolist()
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57', '#FF9FF3', '#BDB76B', '#ADFF2F'][:len(categories)]
        ax1.pie(values, labels=categories, autopct='%1.1f%%', colors=colors, startangle=90, textprops={'color': 'white', 'fontsize': 11})
        ax1.set_title(f'Crime Distribution {year}', color='white', fontsize=16, pad=20)
        ax1.set_facecolor('black')

        bars = ax2.bar(categories, values, color=colors, alpha=0.8)
        ax2.set_title(f'Crime Statistics {year}', color='white', fontsize=16, pad=20)
        ax2.set_ylabel('Number of Cases', color='white')
        ax2.set_facecolor('black')
        ax2.tick_params(colors='white', rotation=45)

        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 5, f'{int(height)}', ha='center', va='bottom', color='white', fontweight='bold', fontsize=10)

        plt.tight_layout()
        return fig, f"Crime statistics for {year} generated."

    def create_professional_crime_map(self):
        if self.crime_df.empty:
            return None, "No crime data loaded to create a map."

        st_kitts_center = [17.3578, -62.7822]

        m = folium.Map(
            location=st_kitts_center,
            zoom_start=11,
            tiles=None
        )

        folium.TileLayer(
            tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
            attr='Google Satellite',
            name='Satellite View',
            overlay=False,
            control=True
        ).add_to(m)
        folium.TileLayer(
            tiles='OpenStreetMap',
            name='OpenStreetMap',
            overlay=False,
            control=True
        ).add_to(m)

        if 'Latitude' in self.crime_df.columns and 'Longitude' in self.crime_df.columns:
            plot_df = self.crime_df.dropna(subset=['Latitude', 'Longitude'])

            if plot_df.empty:
                return None, "No valid Latitude/Longitude data found to plot on the map."

            location_counts = plot_df.groupby(['Latitude', 'Longitude', 'Location']).size().reset_index(name='Total Incidents')
            crime_types_by_location = plot_df.groupby(['Latitude', 'Longitude', 'Location', 'Crime Type']).size().reset_index(name='Count')

            for index, row in location_counts.iterrows():
                coords = [row['Latitude'], row['Longitude']]
                location_name = row['Location']
                total_incidents = row['Total Incidents']

                crime_types = crime_types_by_location[(crime_types_by_location['Latitude'] == row['Latitude']) & 
                                                      (crime_types_by_location['Longitude'] == row['Longitude'])]
                breakdown = ", ".join([f"{ct['Crime Type']}: {ct['Count']}" for idx, ct in crime_types.iterrows()])

                risk = "High" if total_incidents > 50 else ("Medium" if total_incidents > 20 else "Low")
                color = 'red' if risk == 'High' else 'orange' if risk == 'Medium' else 'green'

                folium.CircleMarker(
                    location=coords,
                    radius=total_incidents / 5, 
                    popup=f"""<b>{location_name}</b><br>
                              <b>Total Incidents:</b> {total_incidents}<br>
                              <b>Breakdown:</b> {breakdown}<br>
                              <b>Risk Level:</b> {risk}<br>
                              <b>Last Updated:</b> {datetime.datetime.now().strftime('%Y-%m-%d')}""",
                    color=color,
                    fill=True,
                    fillColor=color,
                    fillOpacity=0.7,
                    weight=2
                ).add_to(m)
        else:
            return None, "Latitude and Longitude columns not found in crime data. Cannot plot specific crime incidents on the map."

        folium.LayerControl().add_to(m)
        return m, "Crime map generated."

    def process_professional_query(self, user_input):
        user_input_lower = user_input.lower()

        if "statistics" in user_input_lower or "data analysis" in user_input_lower:
            year_match = [s for s in user_input_lower.split() if s.isdigit() and len(s) == 4]
            year = int(year_match[0]) if year_match else datetime.datetime.now().year
            
            if self.crime_df.empty or 'Year' not in self.crime_df.columns:
                return "Officer, my crime data for generating statistics is not available. Please ensure the CSV is correctly formatted."

            available_years = self.crime_df['Year'].unique()
            if year not in available_years:
                return f"Officer, I only have crime data for the years: {', '.join(map(str, available_years))}. Please request statistics for one of these years."

            fig, msg = self.create_crime_statistics_chart(year)
            if fig:
                st.pyplot(fig)
                plt.close(fig)
                return f"**CRIME STATISTICS FOR {year}**\n\n{msg}"
            else:
                return f"Officer, I encountered an issue generating crime statistics for {year}: {msg}"
        
        elif "map" in user_input_lower or "hotspot" in user_input_lower or "geospatial" in user_input_lower:
            m, msg = self.create_professional_crime_map()
            if m:
                st.markdown('<div class="crime-map-container">', unsafe_allow_html=True)
                folium_static(m, width=700, height=500)
                st.markdown('</div>', unsafe_allow_html=True)
                return f"**CRIME HOTSPOTS MAP**\n\n{msg}"
            else:
                return f"Officer, I encountered an issue generating the crime map: {msg}"

        elif any(word in user_input_lower for word in ["legal", "law", "statute", "criminal code"]):
            return self.get_legal_reference(user_input)
        elif any(word in user_input_lower for word in ["contact", "phone", "directory", "reach"]):
            return self.get_professional_directory()
        elif any(word in user_input_lower for word in ["protocol", "procedure", "how to", "steps", "investigation"]):
            return self.get_investigation_protocol(user_input)
        
        else:
            return ask_enhanced_chatbot(user_input)

def display_message(role, content):
    if role == "user":
        st.markdown(f'<div class="user-message"><div class="user-bubble">{content}</div></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bot-message"><div class="bot-bubble">{content}</div></div>', unsafe_allow_html=True)

# Main Application Flow
if "auth" not in st.session_state:
    st.session_state.auth = UserAuthentication()
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "messages" not in st.session_state:
    st.session_state.messages = []
if "bot" not in st.session_state:
    st.session_state.bot = CriminologyProfessionalBot()

if not st.session_state.logged_in:
    st.title("SECURO - Crime Mitigation AI Chat Bot (Professional Login)")
    st.subheader("Professional Access Login")
    username = st.text_input("Username (e.g., admin)", key="login_username")
    password = st.text_input("Password (e.g., adminpass)", type="password", key="login_password")

    if st.button("ACCESS SECURO SYSTEM", use_container_width=True, type="primary"):
        success, message = st.session_state.auth.login(username, password)
        if success:
            st.success(f"Access Granted: {message}")
            time.sleep(1)
            st.rerun()
        else:
            st.error(f"Access Denied: {message}")
else:
    st.title("SECURO - Crime Mitigation AI Chat Bot")
    st.markdown(f"""
        <div style="background: #1a4d1a; padding: 10px; border-radius: 8px; margin: 10px 0; text-align: center;">
        <strong> 🟢 SYSTEM ONLINE</strong><br>
        <small>Officer: {st.session_state.user_role}</small>
        </div>
        """, unsafe_allow_html=True)
    st.divider()

    st.subheader(" 🚨 Emergency Response")
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button(" 🚨 \nPolice\nDispatch", use_container_width=True, help="Emergency: 911 | HQ: (869) 465-2241"):
            st.markdown("""
                <div style="background: #8B0000; padding: 15px; border-radius: 8px; color: white; text-align: center; margin: 10px 0;">
                <h4> 🚨 POLICE DISPATCH</h4>
                <p><strong>Emergency:</strong> <a href="tel:911" style="color: #FFFF00;">911</a></p>
                <p><strong>HQ Direct:</strong> <a href="tel:+18694652241" style="color: #FFFF00;">(869) 465-2241</a></p>
                </div>
                """, unsafe_allow_html=True)
    with col_b:
        if st.button(" 🚑 \nMedical\nEmergency", use_container_width=True, help="Emergency: 911 | JNF Hospital: (869) 465-2551"):
            st.markdown("""
                <div style="background: #8B0000; padding: 15px; border-radius: 8px; color: white; text-align: center; margin: 10px 0;">
                <h4> 🚑 MEDICAL EMERGENCY</h4>
                <p><strong>Emergency:</strong> <a href="tel:911" style="color: #FFFF00;">911</a></p>
                <p><strong>JNF Hospital:</strong> <a href="tel:+18694652551" style="color: #FFFF00;">(869) 465-2551</a></p>
                </div>
                """, unsafe_allow_html=True)
    st.divider()

    for message in st.session_state.messages:
        display_message(message["role"], message["content"])

    if prompt := st.chat_input("Enter case details, legal query, or request professional assistance..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        display_message("user", prompt)

        with st.spinner("Processing professional inquiry..."):
            response = st.session_state.bot.process_professional_query(prompt)
            st.session_state.messages.append({"role": "bot", "content": response})
            display_message("bot", response)
