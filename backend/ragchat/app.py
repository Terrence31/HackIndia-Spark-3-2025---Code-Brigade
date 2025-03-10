import os 
import json
import numpy as np
from datetime import datetime 
from dotenv import load_dotenv 
from langchain_cohere import ChatCohere, CohereEmbeddings
# from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.prompts import PromptTemplate 
from langchain.chains.question_answering import load_qa_chain 
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader, Docx2txtLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter 
from langchain_community.vectorstores import Chroma
from docx import Document
from langchain.chains import RetrievalQA 
from langchain.memory import ConversationBufferMemory 
from pypdf import PdfReader
import sys
from unicodedata import category


api_key = 'sApb7nP6OfEYkQHNUpqprz5Srck5c7ZOtETachC0'
model = ChatCohere(api_key=api_key, model_name='c4ai-aya-expanse-8b', temperature=0.5)
embeddings = CohereEmbeddings(api_key=api_key, model_name='embed-multilingual-v3.0')

def load_and_process(doc_source):
    all_docs = []
    documents = []
    if doc_source.endswith(".doc") or doc_source.endswith(".docx"):
        temp = DirectoryLoader(doc_source, glob='*.docx', loader_cls=Docx2txtLoader)
        # temp = Docx2txtLoader(doc_source)
        all_docs.append(temp)
    if doc_source.endswith(".pdf"):
        # temp = PyPDFLoader(doc_source)
        temp = DirectoryLoader(doc_source, glob='*.pdf', loader_cls=PyPDFLoader)
        all_docs.append(temp)
    if doc_source.endswith(".txt") or doc_source.endswith(".md"):
        # temp = TextLoader(doc_source)
        temp = DirectoryLoader(doc_source, glob='*.txt', loader_cls=TextLoader)
        all_docs.append(temp)
    for docs in all_docs:
        documents = docs.load()
    return documents

def split_text(documents):
    text_split = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    split_docs = text_split.split(documents)
    return split_docs


def vectordb_info(docs):
    vector_store = Chroma.from_documents(
        docs,
        embeddings=embeddings,
        persist_directory='vector_store',
    )
    vector_store.persist()
    return vector_store

def ragchat(vector_store):
    template = """ """
    QA_PROMPT = PromptTemplate(template)
    qa_chain = RetrievalQA.from_chain_type(
        llm = model,
        chain_type='retrieval',
        retriever = vector_store.as_retriever(
            search_kwargs={'k': 2}
        ),
        return_source_documents=True,
        chain_type_kwargs={'prompt': QA_PROMPT},
        memory=ConversationBufferMemory(memory_key='qa_chain_memory', return_messages=True)
    )
    return qa_chain

def response(qa_chain, question):
    try:
        result = qa_chain({'query': question})
        response = result['response']
        return response
    except Exception as e:
        return f"An Error has occured: {str(e)}"
    

def ragchat_pipeline(document_sources):
    processed_docs = load_and_process(document_sources)
    vector_store = vectordb_info(processed_docs)
    ragchat_chain = ragchat(vector_store)
    return ragchat_chain
