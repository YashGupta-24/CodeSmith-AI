from uagents import Agent, Context, Model, Protocol
from uagents.setup import fund_agent_if_low
from together import Together
from datetime import datetime
from uuid import uuid4
import os
from dotenv import load_dotenv

load_dotenv()

os.environ["TOGETHER_API_KEY"] = os.getenv("TOGETHER_API_KEY") #type:ignore

from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    EndSessionContent,
    StartSessionContent,
    TextContent,
    chat_protocol_spec,
)

client = Together()

code_smith = Agent(
    name="Code Smith AI",
    seed="I am a code generating agent",
    port=8080,
    mailbox=True,  
    readme_path="README.md",
    publish_agent_details=True

)

fund_agent_if_low(code_smith.wallet.address()) #type:ignore

chat_proto = Protocol(spec=chat_protocol_spec)

class CodeQuery(Model):
    prompt: str

class CodeResponse(Model):
    result: str

def create_text_chat(text: str, end_session: bool = True) -> ChatMessage:
    content = [TextContent(type="text", text=text)]
    if end_session:
        content.append(EndSessionContent(type="end-session")) #type:ignore
    return ChatMessage(
        timestamp=datetime.utcnow(),
        msg_id=uuid4(),
        content=content, #type:ignore
    ) 

def generate_with_together(prompt: str) -> str:
    try:
        response = client.chat.completions.create(
            model="Qwen/Qwen2.5-Coder-32B-Instruct",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            stream=False  
        )
        if hasattr(response, 'choices'):
            return response.choices[0].message.content #type:ignore
        return "Unable to generate a response."
    except Exception as e:
        return f"Error occurred: {str(e)}"

@chat_proto.on_message(ChatMessage)
async def handle_message(ctx: Context, sender: str, msg: ChatMessage):
    ctx.logger.info(f"Got a message from {sender}")
    ctx.storage.set(str(ctx.session), sender)
    
    await ctx.send(
        sender,
        ChatAcknowledgement(timestamp=datetime.utcnow(), acknowledged_msg_id=msg.msg_id),
    )
    
    for item in msg.content:
        if isinstance(item, StartSessionContent):
            ctx.logger.info(f"Got a start session message from {sender}")
            continue
        elif isinstance(item, TextContent):
            ctx.logger.info(f"Got a message from {sender}: {item.text}")
            
            result = generate_with_together(item.text)
            
            chat_message = create_text_chat(result)
            await ctx.send(sender, chat_message)
        else:
            ctx.logger.info(f"Got unexpected content from {sender}")

@chat_proto.on_message(ChatAcknowledgement)
async def handle_ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
    ctx.logger.info(
        f"Got an acknowledgement from {sender} for {msg.acknowledged_msg_id}"
    )

class HealthCheck(Model):
    pass

class HealthStatus(Model):
    status: str

@code_smith.on_message(model=HealthCheck)
async def handle_health_check(ctx: Context, sender: str, msg: HealthCheck):
    """Handle health check requests to ensure the agent is functioning properly"""
    try:
        test_result = generate_with_together("Hello")
        if test_result and "Error" not in test_result:
            await ctx.send(sender, HealthStatus(status="healthy"))
        else:
            await ctx.send(sender, HealthStatus(status="unhealthy"))
    except Exception:
        await ctx.send(sender, HealthStatus(status="unhealthy"))

@code_smith.on_message(model=CodeQuery)
async def handle_query(ctx: Context, sender: str, msg: CodeQuery):
    ctx.logger.info(f"Received code generation task: {msg.prompt}")
    # prompt='''
    #     query:{msg.prompt}
    #     Execute the query and generate the response in the following format, properly categorized:
    #     1. Code
    #     2. Explanation
    # '''
    # ctx.logger.info(prompt)
    # response = generate_with_together(prompt)
    response = generate_with_together(msg.prompt)
    await ctx.send(sender, CodeResponse(result=response))

code_smith.include(chat_proto, publish_manifest=True)

@code_smith.on_event('startup')
async def startup(ctx: Context):
    ctx.logger.info("Code Generation Agent started successfully!")

if __name__ == "__main__":
    code_smith.run()