import streamlit as st
import json
import csv
from datetime import datetime
from twilio.rest import Client
from google import genai
from main_agent import get_recommendation,client, MODEL_ID, vector_db 

# CONFIGURATION & SETUP of TWILIO Notification Service (cannot provide SID, Token and Service SID on github public repository)
TWILIO_SID = 'YOUR_SID'
TWILIO_TOKEN = 'YOUR_TOKEN'
TWILIO_SERVICE_SID = 'YOUR_SERVICE_SID'
TARGET_PHONE = 'PHONE NUMBER'
LOG_FILE = 'interaction_logs.csv'

# Initializing CSV for tracking integration
def log_action(user_id, action, recommendation):
    with open(LOG_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now(), user_id, action, recommendation[:50] + "..."])

# Twilio SMS Function for sending messages
def send_sms_notification(product_name):
    try:
        client = Client(TWILIO_SID, TWILIO_TOKEN)
        # "Bank offer" : product name (sms formatting)
        message = client.messages.create(
            messaging_service_sid=TWILIO_SERVICE_SID,
            body=f'"Bank Offer" : {product_name} ',
            to=TARGET_PHONE
        )
        return message.sid
    except Exception as e:
        return f"Error: {str(e)}"

# STREAMLIT UI SETUP for the frontend
st.set_page_config(page_title="Nexora", layout="wide", page_icon="🏦")
st.title("Nexora")

# Load User Profiles
with open('mock_data.json', 'r') as f:
    customer_profiles = json.load(f)

# Sidebar for User Selection (Simulates Login/Historic Data of different user)
st.sidebar.header("👤 User Context")
selected_user_id = st.sidebar.selectbox("Select User Persona", [p['user_id'] for p in customer_profiles])
user_profile = next(p for p in customer_profiles if p['user_id'] == selected_user_id)

st.sidebar.divider()
st.sidebar.write(f"**Persona:** {user_profile['risk_profiling']['requirement']}")
st.sidebar.write(f"**Risk Tolerance:** {user_profile['risk_profiling']['tolerance']}")
st.sidebar.write(f"**Financial Goal:** {user_profile['questionnaire']['goals']}")

#  MAIN INTERFACE of the Agent
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("🛒 Event Simulation")
    st.caption("This simulates data arriving from the Streaming Data Bus.")
    
    description = st.text_input("Transaction Description", "Investment into Tech Stocks")
    amount = st.number_input("Transaction Amount ($)", min_value=0.0, value=5000.0)
    
    if st.button("Generate Recommendation", type="primary"):
        event = {
            "user_id": selected_user_id,
            "data": {"amount": amount, "description": description}
        }
        with st.spinner('Orchestrating AI & Checking Compliance...'):
            # Calls the Gemini + ChromaDB backend
            recommendation = get_recommendation(event)
            st.session_state['latest_rec'] = recommendation
            st.rerun()
#notification service for sending messages to digital channels
with col2:
    st.subheader("📲 Notification Service")
    
    if 'latest_rec' in st.session_state and st.session_state['latest_rec']:
        current_rec = st.session_state['latest_rec']
        
        # Display the AI Recommendation fetchted from LLM (Gemini)
        st.success(f"**New AI Recommendation for {selected_user_id}:**")
        
        if isinstance(current_rec, dict):
            display_text = current_rec.get('recommendation', "No recommendation text")
            product_name = current_rec.get('product_name', "Bank Product")
        else:
            display_text = str(current_rec)
            product_name = "Bank Product"

        st.write(display_text)
        
        st.divider()
        btn_col1, btn_col2 = st.columns(2)
        
        # Accept offer by SMS
        if btn_col1.button("✅ Accept & SMS", use_container_width=True):
            with st.spinner('Sending SMS...'):
                sid = send_sms_notification(product_name)
                if "Error" in sid:
                    st.error(sid)
                else:
                    st.toast(f"SMS Sent! ID: {sid}")
                    log_action(selected_user_id, "ACCEPTED", str(current_rec))
                    st.session_state['latest_rec'] = None # Clear after success
                    st.rerun()

        # Dismiss Action by user
        if btn_col2.button("❌ Dismiss", use_container_width=True):
            log_action(selected_user_id, "DISMISSED", str(current_rec))
            st.session_state['latest_rec'] = None
            st.rerun()
            
    else:
        st.info("No active recommendations. Simulate an event on the left.")

#  ANALYTICS ENGINE and Feedback loop (saves the logs of the user's interaction)
st.divider()
st.write("### 📈 Analytics Engine (Internal Logs)")
if st.checkbox("Show system interaction logs"):
    try:
        with open(LOG_FILE, 'r') as f:
            st.text(f.read())
    except FileNotFoundError:
        st.write("No logs recorded yet.")

st.divider()
st.subheader("💬 Ask Nexora..")
st.caption(" Anything about Loans, Insurance, or Investments.")

# Chat History Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input 
if prompt := st.chat_input("Ex: Suggest the best Home loan for me?"):
    # 1. Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. RAG Logic: Retrieve Context from ChromaDB
    with st.spinner("Consulting Bank Database..."):
        docs = vector_db.similarity_search(prompt, k=3)
        context = "\n".join([d.page_content for d in docs])

        # 3. Gemini Prompt for Chat
        chat_prompt = f"""
        You are a Smart Bank Assistant. Use the provided Product Context to answer the User Question.
        If the question is about Loans, Insurance, or Investments, give a 'Smart Recommendation' 
        based on the user's Profile: {user_profile['risk_profiling']['tolerance']} risk tolerance.
        
        CONTEXT FROM BANK DB:
        {context}
        
        USER QUESTION: {prompt}
        """

        response = client.models.generate_content(model=MODEL_ID, contents=chat_prompt)
        ai_response = response.text

    # 4. Show AI response
    st.session_state.messages.append({"role": "assistant", "content": ai_response})
    with st.chat_message("assistant"):
        st.markdown(ai_response)
        log_action(selected_user_id, "CHAT_QUERY", prompt)
