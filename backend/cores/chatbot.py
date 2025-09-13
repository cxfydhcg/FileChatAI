import os
from openai import OpenAI
from dotenv import load_dotenv
import logging
from utils.vector import  get_all_vector_store_info
from agents import Agent, Runner
import asyncio
from openai.types.responses import ResponseTextDeltaEvent
from utils.tools import generate_answer_for_file, generate_answer_for_order

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler("logs/chatbot.log", mode="w")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
logger.addHandler(file_handler)

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)


chatbot_agent = Agent(
    
    name="Chatbot",
    instructions="""
    You are a comprehensive chatbot that helps users find their order/financial information or find data from a specific file.
    
    **Your Capabilities:**
    1. Find orders or financial information for a customer (including all order details)
    2. Find datas in the specific file, such as some customers, inventory, detail, or pricelist.
    3. Use generate_answer_for_order to generate the answer for the question if the question is related to an order or financial information.
    4. Answer the question based on the data find from the tool call
    
    **For Example:**
    When users ask for order details related to a customer, you should use generate_answer_for_order to generate the answer.
    When users ask for information in the file, you should use generate_answer_for_file to generate the answer.
    
    Always provide clear, organized responses with all relevant information.
    """,
    model="gpt-4.1",
    tools=[generate_answer_for_file, generate_answer_for_order],
)
def get_answer(question: str) -> str:
    result = asyncio.run(Runner.run(chatbot_agent, question))
    logger.info(result)
    return result.final_output

async def run_agent(question: str) -> str:
    result = Runner.run_streamed(chatbot_agent, question)
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            yield event.data.delta
        

def get_answer_stream_helper(question: str):
    def generate():
        # Create event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                async def stream_chunks():
                    async for chunk in run_agent(question):
                        yield chunk  # Send each chunk immediately
                
                # Stream each chunk as it comes
                async_gen = stream_chunks()
                while True:
                    try:
                        chunk_data = loop.run_until_complete(async_gen.__anext__())
                        yield chunk_data
                    except StopAsyncIteration:
                        break
            finally:
                loop.close()
    return generate(), {"Content-Type": "text/event-stream"}
def get_file_hint_stream_helper() -> str:
    def generate():
        prompt = f"""
        Based on the vector store info, give me a brief description of all the files, and a few example questions users could ask about this data.
        Start with, I can help you with the following information...
        Customer (profile information):
        Inventory (order level information, linked to customer via CID):
        Detail (order details, linked to inventory via IID and to Pricelist vis item_id):
        Pricelist (item price information):

        {get_all_vector_store_info()}
        """
        stream = client.responses.create(
                model="gpt-4.1-nano",
                input=prompt,
                stream=True,
            )
        for event in stream:
            logger.info(f"Stream event {event}")
            if isinstance(event, ResponseTextDeltaEvent):
                logger.info(f"Stream event {event.delta}")
                yield event.delta
    return generate(), {"Content-Type": "text/event-stream"}



