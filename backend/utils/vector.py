from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
import os
import pandas as pd
import logging
import json

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler("logs/vector.log", mode="w")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
logger.addHandler(file_handler)


_all_vector_store_info = {
    "customers": "",
    "detail": "",
    "pricelist": "",
    "inventory": ""
}
db_location = "./vector_db"
if not os.path.exists(db_location):
    os.makedirs(db_location)
embeddings = OllamaEmbeddings(model="mxbai-embed-large", base_url=os.getenv("OLLAMA_API_URL"))
file_location = "./files"

def create_vector_store(file_name: str) -> None:

    file_path = os.path.join(file_location, file_name)
    # Create vector store for each file
    df = pd.read_csv(file_path)
    documents = []
    ids = []
    logger.info(f"Create vector store for file {file_name}")
    for i, row in df.iterrows():
        document = Document(
            page_content=json.dumps(row.to_dict(), default=str),
            metadata={
                "file": file_name.split(".")[0],
                "row": i
            },
            id=str(i)
        )
        ids.append(str(i))
        documents.append(document)
        
    vector_store = Chroma(
        collection_name=file_name.split(".")[0],
        persist_directory=db_location,
        embedding_function=embeddings
    )

    vector_store.add_documents(documents=documents, ids=ids)
    # Store the header information 
    _all_vector_store_info[file_name.split(".")[0]] = f"""
    This vector store {file_name.split(".")[0]} contains the following information:
    {df.columns.tolist()}
    """
    
    logger.info(f"Create vector store for file {file_name} done")
    logger.info(f"Vector store {file_name.split('.')[0]} contains {len(documents)} documents")

def search_vector_store(vector_store_name: str, query: str, k: int = 1) -> list[Document]:
    vector_store = Chroma(
        collection_name=vector_store_name,
        persist_directory=db_location,
        embedding_function=embeddings
    )
    retriever = vector_store.as_retriever(
        search_kwargs={"k": k}
    )
    documents = retriever.invoke(query)
    logger.info(f"Search vector store {vector_store_name} with query {query}, get {len(documents)} documents")
    logger.info(f"Documents: {documents}")
    return documents

def get_all_vector_store_info() -> dict:
    return _all_vector_store_info.copy()

