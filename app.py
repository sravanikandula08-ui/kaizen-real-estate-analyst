import streamlit as st
import boto3
import uuid

# --- PAGE CONFIG ---
st.set_page_config(page_title="Kaizen Real Estate Analyst", page_icon="🏢", layout="centered")
st.title("🏢 Kaizen AI Analyst")
st.subheader("Commercial Real Estate & Non-Performing Loan Diligence")

# --- 1. GLOBAL KILL SWITCH (Check this first) ---
if "APP_ENABLED" in st.secrets and st.secrets["APP_ENABLED"].lower() == "false":
    st.warning("⚠️ This demo is currently offline for maintenance.")
    st.stop()

# --- AWS CREDENTIALS ---
if "AWS_ACCESS_KEY_ID" in st.secrets:
    client = boto3.client(
        service_name='bedrock-agent-runtime',
        region_name=st.secrets["AWS_DEFAULT_REGION"],
        aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"]
    )
else:
    st.error("AWS Credentials not found. Please configure Streamlit Secrets.")
    st.stop()

# --- AGENT CONFIG ---
AGENT_ID = "O759JWQHSA" 
AGENT_ALIAS_ID = "NVEHDZ9DGP" 
MAX_CALLS = 10  # Set your usage limit here

# --- SESSION STATE ---
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize usage counter
if "usage_counter" not in st.session_state:
    st.session_state.usage_counter = 0

# --- CHAT INTERFACE ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 2. CHAT LOGIC (With Usage Guard) ---
# Only show the chat input if they haven't hit the limit
if st.session_state.usage_counter < MAX_CALLS:
    if prompt := st.chat_input("Ask about property financials, legal status, or risk..."):
        # Increment counter
        st.session_state.usage_counter += 1
        
        # Display user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Invoke Bedrock Agent
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = ""
            
            try:
                response = client.invoke_agent(
                    agentId=AGENT_ID,
                    agentAliasId=AGENT_ALIAS_ID,
                    sessionId=st.session_state.session_id,
                    inputText=prompt
                )
                
                for event in response.get("completion"):
                    if "chunk" in event:
                        chunk = event["chunk"]["bytes"].decode("utf-8")
                        full_response += chunk
                        response_placeholder.markdown(full_response + "▌")
                
                response_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
            except Exception as e:
                st.error(f"Error calling AI Analyst: {str(e)}")
    
    # Display a small footer showing usage
    st.caption(f"Questions used: {st.session_state.usage_counter} / {MAX_CALLS}")

else:
    st.error(f"🛑 Usage limit of {MAX_CALLS} messages reached for this session.")
    st.info("To protect against excessive costs, this public demo is capped. Please refresh to start over.")