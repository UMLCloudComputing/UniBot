import boto3
import logging
import os
# import streamlit as st
# from langchain_openai import ChatOpenAI
# from typing import List, Dict
# from pydantic import BaseModel
from operator import itemgetter
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_aws import ChatBedrock
from langchain_aws import AmazonKnowledgeBasesRetriever
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_community.chat_message_histories import DynamoDBChatMessageHistory

# st.set_page_config(
#     page_title='RowdyLLM',
#     menu_items={
#         'Get Help': None,
#         'Report a bug': None,
#         'About': None
#     }
# )

DYNAMO_TABLE = os.getenv('DYNAMO_TABLE')

# os.environ["AWS_ACCESS_KEY_ID"] = os.getenv('AWS_ID')
# os.environ["AWS_SECRET_ACCESS_KEY"] = os.getenv('AWS_KEY')

# os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

# ------------------------------------------------------
# Log level

logging.getLogger().setLevel(logging.ERROR) # reduce log level

# ------------------------------------------------------
# Amazon Bedrock - settings

bedrock_runtime = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-east-1",
    # aws_access_key_id=os.getenv('AWS_ID'),
    # aws_secret_access_key=os.getenv('AWS_KEY'),
    # aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"],
    # aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"],
)

retrieval_runtime = boto3.client(
    service_name="bedrock-agent-runtime",
    region_name="us-east-1",
    # aws_access_key_id=os.getenv('AWS_ID'),
    # aws_secret_access_key=os.getenv('AWS_KEY'),
    # aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"],
    # aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"],
)

model_id = "anthropic.claude-3-haiku-20240307-v1:0"

model_kwargs =  { 
    "max_tokens": 2048,
    "temperature": 0.0,
    "top_k": 250,
    "top_p": 1,
    "stop_sequences": ["\n\nHuman"],
}

# ------------------------------------------------------
# LangChain - RAG chain with chat history


prompt_text = '''
You are Rowdy the Riverhawk, a chatbot for the University of Massachusetts Lowell. Provide answers in the style of a tour guide. 
Please only use answers that are present in the search results here:\n {context}
All users are full time students unless stated otherwise
Please only answer questions about the University of Massachusetts Lowell.
'''

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", prompt_text),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}"),
    ]
)

# Amazon Bedrock - KnowledgeBase Retriever 
retriever = AmazonKnowledgeBasesRetriever(
    knowledge_base_id=os.getenv("KB_ID"), # 👈 Set your Knowledge base ID
    client=retrieval_runtime,
    retrieval_config={"vectorSearchConfiguration": {"numberOfResults": 12}},
)

# # OpenAI - GPT-4o-mini model
# model = ChatOpenAI(model_name="gpt-4o-mini")
model = ChatBedrock(
    client=bedrock_runtime,
    model_id=model_id,
    model_kwargs=model_kwargs,
)



chain = (
    RunnableParallel({
        "context": itemgetter("question") | retriever,
        "question": itemgetter("question"),
        "history": itemgetter("history"),
    })
    .assign(response = prompt | model | StrOutputParser())
    .pick(["response", "context"])
)

# ------------------------------------------------------
# Pydantic data model and helper function for Citations

# class Citation(BaseModel):
#     page_content: str
#     metadata: Dict

# def extract_citations(response: List[Dict]) -> List[Citation]:
#     return [Citation(page_content=doc.page_content, metadata=doc.metadata) for doc in response]

# # # Initialize session state for messages if not already present
# # if "messages" not in st.session_state:
# #     st.session_state.messages = [{"role": "assistant", "content": "Ask me anything about UMass Lowell!"}]

# # Display chat messages
config = {"configurable": {"session_id": "any"}}


def invoke_llm(prompt, userID):
    # DynamoDB Chat History
    history = DynamoDBChatMessageHistory(table_name=DYNAMO_TABLE, session_id=userID)

    # Chain with History
    chain_with_history = RunnableWithMessageHistory(
        chain,
        lambda session_id: history,
        input_messages_key="question",
        history_messages_key="history",
        output_messages_key="response",
    )
    response = chain_with_history.invoke(
        {"question" : prompt, "history" : history},
        config
    )
    return response['response']


if __name__ == "__main__":
    print(invoke_llm("Wait what's my name again?"))

