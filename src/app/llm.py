import boto3
import logging
import os

# Data Modeling for Citations
from typing import List, Dict
from pydantic import BaseModel
from operator import itemgetter

# LangChain Core
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import StrOutputParser

# Message History
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import OpenAIEmbeddings
from langchain_community.chat_message_histories import DynamoDBChatMessageHistory

# Retrieval Augmented Generation
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from langchain_openai import ChatOpenAI

from dotenv import load_dotenv
load_dotenv()

DYNAMO_TABLE = os.getenv('DYNAMO_TABLE')
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

logging.getLogger().setLevel(logging.ERROR) # reduce log level
retrieval_runtime = boto3.client(service_name="bedrock-agent-runtime", region_name="us-east-1")

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


pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
vector_store = PineconeVectorStore(index=pc.Index(os.getenv("INDEX_NAME").lower()), embedding=OpenAIEmbeddings(model="text-embedding-3-small"))
retriever = vector_store.as_retriever()

# # OpenAI - GPT-4o-mini model
model = ChatOpenAI(model_name="gpt-4o-mini")

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

class Citation(BaseModel):
    page_content: str
    metadata: Dict

def extract_citations(response: List[Dict]) -> List[Citation]:
    return [Citation(page_content=doc.page_content, metadata=doc.metadata) for doc in response]

# ------------------------------------------------------
# Display chat messages
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

    citations = extract_citations(response["context"])
    
    citation_text = "Sources:\n"
    for x in range(0, 3):
        citation_text += citations[x].metadata['url'] + "\n"

    return response['response'] + "\n" + citation_text


if __name__ == "__main__":
    print(invoke_llm("what's my name", "12345"))

