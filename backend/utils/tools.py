from concurrent.futures import ProcessPoolExecutor, as_completed
import os
from openai import OpenAI
from dotenv import load_dotenv
import logging
from pydantic import BaseModel
import pandas as pd
from utils.vector import get_all_vector_store_info, search_vector_store
import json
from agents import function_tool

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler("logs/tools.log", mode="w")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
logger.addHandler(file_handler)

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

class VectorStoresPickResponseFormat(BaseModel):
    vector_store_names: list[str]

class IDResponseFormat(BaseModel):
    ID: str

def filter_csv_pandas(file_name, column_name, target_value) -> list[dict]:
    try:
        logger.info(f"Filter {file_name} by {column_name} = {target_value}")
        file_name = "./files/" + file_name + ".csv"
        df = pd.read_csv(file_name)
        rows = df[df[column_name] == int(target_value)].to_dict(orient="records")
        logger.info(rows)
        return rows
    except Exception as e:
        logger.error(f"Error in filter_csv_pandas {file_name}: {e}")
        return []
        

@function_tool
def generate_answer_for_file(question: str) -> dict:
    """
    Use this tool to fetch data from specific, individual files. (e.g., a ticket number, an inventory ID, or a customer ID)
    Limitation: This tool can only retrieve one piece of data at a time. It cannot automatically find connections between different files (e.g., find all orders for a customer named "Amy").
    """
    all_vector_stores = get_all_vector_store_info()
    logger.info(all_vector_stores)
    system_prompt = f"""
    Based on the user's question, and the description of the vector stores, find the relevant vector stores. The answer must be the key of the dict, if 
    the user question is not related to any vector store, return an empty list.
    {all_vector_stores}
    """
    user_prompt = f"""
    Find the vector store retriever for the following user question:
    {question}
    """
    
    response = client.chat.completions.parse(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format=VectorStoresPickResponseFormat
    )
    logger.info(response)
    vector_store_names = response.choices[0].message.parsed.vector_store_names
    if len(vector_store_names) == 0:
        return "No relevant information found"
    if any(vector_store_name not in all_vector_stores for vector_store_name in vector_store_names):
        raise ValueError("Some vector store names are not valid")
    logger.info(vector_store_names)

    search_result = {}
    for vector_store_name in vector_store_names:
        search_result[vector_store_name] = search_vector_store(vector_store_name, question, 4)
        logger.info(f"Search result for {vector_store_name}: {search_result[vector_store_name]}")
    # with ProcessPoolExecutor(max_workers=5) as executor:
    #     future_to_vector_store_name = {executor.submit(search_vector_store, vector_store_name, question): vector_store_name for vector_store_name in vector_store_names}
    #     for future in as_completed(future_to_vector_store_name):
    #         vector_store_name = future_to_vector_store_name[future]
    #         try:
    #             search_result[vector_store_name] = future.result()
    #         except Exception as e:
    #             logger.error(f"Error in search_vector_store {vector_store_name}: {e}")
        
    logger.info(search_result)
    return search_result

@function_tool
def generate_answer_for_order(question: str) -> dict:
    """
    Use this tool to access all of the data related to a user, including the inventory, order, and price data
    You must provide the user infomation (e.g., customer name, customer ID, email, etc)

    """
    customer_documents = search_vector_store("customers", question)
    logger.info(f"customer_documents: {customer_documents}")
    if len(customer_documents) == 0:
        return "No relevant information found"
    customer_info = json.loads(customer_documents[0].page_content)
    inventory_rows = filter_csv_pandas("inventory", "CID", customer_info["CID"])
    logger.info(f"inventory_rows: {inventory_rows}")
    if len(inventory_rows) == 0:
        return "No relevant information found"
    detail_rows = []
    for item in inventory_rows:
        IID = item["IID"]
        detail_rows.extend(filter_csv_pandas("detail", "IID", IID))
    if len(detail_rows) == 0:
        return "No relevant information found"
    logger.info(f"detail_rows: {detail_rows}")
    pricelist_rows = []
    for item in detail_rows:
        item_id = item["Item_ID"]
        pricelist_rows.extend(filter_csv_pandas("pricelist", "item_id", item_id))
    logger.info(f"pricelist_rows: {pricelist_rows}")

    return {
        "customer_info": customer_info,
        "inventory_rows": inventory_rows,
        "detail_rows": detail_rows,
        "pricelist_rows": pricelist_rows,
    }
