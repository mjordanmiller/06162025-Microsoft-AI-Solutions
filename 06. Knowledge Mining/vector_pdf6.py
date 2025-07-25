'''
This code contains helpers for creating a vector database from a PDF document using LangChain and Chroma.
It is used in the create_responses.py file
'''

import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
import chromadb

def create_vector_db_from_pdf(
    pdf_path: str = "./Data/testContract1.pdf",
    collection_name: str = "pdf_vectors",
    embedding_model_name: str = "mxbai-embed-large",
    knn: int = 5
):
    # Initialize embedding 
    embed_model = OllamaEmbeddings(model=embedding_model_name)

    #chroma_client = chromadb.Client()
    chroma_client = chromadb.PersistentClient()

    #Check if collection already exists
    #USE LINE BELOW THIS COMMENT FOR EASY RESETS OF YOUR DATABASE -- FOR TESTING
    [chroma_client.delete_collection(name=col.name) for col in chroma_client.list_collections()] #workaround for weird duplication issue
    existing_collections = [col.name for col in chroma_client.list_collections()]
    print("Existing Collections:", existing_collections)
    is_new_collection = collection_name not in existing_collections
    print(f"New collection? : {is_new_collection}")

 

    vector_store_from_client = Chroma(
        client=chroma_client,
        collection_name=collection_name,
        embedding_function=embed_model,
    )

    if is_new_collection:
        # Load and process PDF
        loader = PyPDFLoader(pdf_path)
        raw_documents = loader.load()
        splitter = RecursiveCharacterTextSplitter(chunk_size=7000, chunk_overlap=100)
        chunked_documents = splitter.split_documents(raw_documents)
        print(f"Loaded {len(raw_documents)} pages, split into {len(chunked_documents)} chunks.")
        ids = [str(i) for i in range(len(chunked_documents))]

        vector_store_from_client.add_documents(documents=chunked_documents, ids=ids)
        print(f"Stored {len(chunked_documents)} chunks into new collection '{collection_name}'.")
    else:
        print(f"Collection '{collection_name}' already exists. Skipping document insertion.")

    
    return vector_store_from_client.as_retriever(search_type="similarity",search_kwargs={"k": knn}) # mmr is useful if your dataset has many similar documents

#the as_retriever is a place for experimentation
#https://api.python.langchain.com/en/latest/vectorstores/langchain_community.vectorstores.chroma.Chroma.html#langchain_community.vectorstores.chroma.Chroma.as_retriever