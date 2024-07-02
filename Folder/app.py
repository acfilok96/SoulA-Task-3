import chainlit as cl
from functions import *


@cl.on_chat_start
async def on_chat_start():
    database = "Image_Record_SQLDB.db"
    table_details = tableDetails(database)
    table_name = "Image_Record_SQLDB"
    feature_name = table_details[1]["Column Name"]
    details = f"""Here is the table details:\n\n
    table name: {table_name} & features name: {str(feature_name)}"""
    await cl.Message(content = details,).send()

@cl.step(type="tool")
async def tool():
    # Simulate a running task
    await cl.sleep(1)

    
@cl.on_message
async def main(message: cl.Message):
    
    database = "Image_Record_SQLDB.db"
   
    await on_chat_start()
    
    tool_res = await tool()
    
    response =  generateQuery(database, message.content)

    # Send a response back to the user
    await cl.Message(content = response,).send()