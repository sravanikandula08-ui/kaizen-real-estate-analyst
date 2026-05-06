import streamlit as st
import boto3
import uuid

# --- PAGE CONFIG ---
st.set_page_config(page_title="Kaizen Real Estate Analyst", page_icon="🏢", layout="centered")
st.title("🏢 Kaizen AI Analyst")
st.subheader("Commercial Real Estate & Non-Performing Loan Diligence")

# --- AWS CREDENTIALS (Sourced from Streamlit Secrets) ---
# When you deploy, you will put these in the 'Advanced Settings > Secrets' box
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
# Replace these with your actual IDs from the AWS Console
AGENT_ID = "O759JWQHSA" 
AGENT_ALIAS_ID = "FFNS2C0ID1" 

# --- SESSION STATE ---
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- CHAT INTERFACE ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- CHAT LOGIC ---
if prompt := st.chat_input("Ask about property financials, legal status, or risk..."):
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