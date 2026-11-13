"""
Page 9: Analytics Assistant
Rule-based deterministic AI Chatbot answering questions about active advertising campaigns,
platforms, audience segments, and budget optimization with 100% verified data calculations.
"""

import streamlit as st
from src.chatbot import AdvertisingAnalyticsAssistant

st.title("🤖 Advertising Analytics Assistant")
st.markdown("Ask natural language questions about your advertising data, metrics, and budget recommendations.")

df = st.session_state.get("active_df")
if df is None or df.empty:
    st.warning("No active dataset loaded. Please go to 'Dataset Management' to load data first.")
    st.stop()

# Initialize Assistant
if "chat_assistant" not in st.session_state or st.session_state.get("chat_assistant_data_len") != len(df):
    st.session_state["chat_assistant"] = AdvertisingAnalyticsAssistant(df)
    st.session_state["chat_assistant_data_len"] = len(df)

assistant = st.session_state["chat_assistant"]

# Initialize chat message history
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = [
        {"role": "assistant", "content": "👋 Hello! I am your Digital Advertising Analytics Assistant. Ask me anything about your campaigns, platform ROAS, CPA, or how to allocate Rs. 1,000,000!"}
    ]

# Suggested Questions Pills
st.markdown("#### 💡 Quick Prompts:")
prompts = [
    "Which platform generated the most revenue?",
    "Which platform has the best ROAS?",
    "What is the average CPC and CPA?",
    "Which campaign performed best?",
    "How should we distribute Rs. 1 million?",
    "Which campaigns have poor performance?",
    "Which audience group generated the most conversions?",
]

p_cols = st.columns(3)
clicked_prompt = None
for idx, p in enumerate(prompts):
    with p_cols[idx % 3]:
        if st.button(f"💬 {p}", key=f"p_{idx}", use_container_width=True):
            clicked_prompt = p

# Display Chat History
for msg in st.session_state["chat_history"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User Input Handling
user_query = st.chat_input("Ask a question about the active advertising data...") or clicked_prompt

if user_query:
    # Append user question
    st.session_state["chat_history"].append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    # Generate grounded response
    response_text = assistant.answer_query(user_query)
    st.session_state["chat_history"].append({"role": "assistant", "content": response_text})
    with st.chat_message("assistant"):
        st.markdown(response_text)

