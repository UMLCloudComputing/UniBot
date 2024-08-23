# ------------------------------------------------------
# Streamlit
# Knowledge Bases for Amazon Bedrock and LangChain 🦜️🔗
# ------------------------------------------------------

import app.llm as llm
import streamlit as st
import secrets
from langchain_openai import ChatOpenAI
from typing import List, Dict
from pydantic import BaseModel
from operator import itemgetter
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_aws import ChatBedrock
from langchain_aws import AmazonKnowledgeBasesRetriever
from langchain_community.chat_message_histories import StreamlitChatMessageHistory

st.set_page_config(
    page_title='RowdyLLM',
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# ------------------------------------------------------
# Pydantic data model and helper function for Citations

class Citation(BaseModel):
    page_content: str
    metadata: Dict

def extract_citations(response: List[Dict]) -> List[Citation]:
    return [Citation(page_content=doc.page_content, metadata=doc.metadata) for doc in response]

# Initialize session state for messages if not already present
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Ask me anything about UMass Lowell!"}]

# Display chat messages
for message in st.session_state.messages:
    if message["role"] == "assistant":
        with st.chat_message(message["role"], avatar="https://www.uml.edu/Images/logo_tcm18-196751.svg"):
            st.write(message["content"])
    else:
        with st.chat_message(message["role"]):
            st.write(message["content"])


# Generate random session ID securely
def random_id():
    return secrets.token_hex(16) 

if 'session_id' not in st.session_state:
    st.session_state.session_id = random_id()

# Chat Input - User Prompt 
if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    config = {"configurable": {"session_id": "any"}}
    # Chain - Stream
    with st.chat_message("assistant", avatar="https://www.uml.edu/Images/logo_tcm18-196751.svg"):
        placeholder = st.empty()
        full_response = ''
        for chunk in llm.stream_llm(prompt, st.session_state.session_id):
            if 'response' in chunk:
                full_response += chunk['response']
                placeholder.markdown(full_response.replace('$', r'\$'))
            else:
                full_context = chunk['context']
        placeholder.markdown(full_response.replace('$', r'\$'))

        citations = extract_citations(full_context)
        with st.expander("Show source details >"):
            for citation in citations:
                st.write("Page Content:", citation.page_content)
                st.write("URL:", citation.metadata['url'])
        # session_state append
        st.session_state.messages.append({"role": "assistant", "content": full_response})