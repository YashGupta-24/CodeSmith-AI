from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low
from conversation import main
from protocols import chat_proto

code_smith = Agent(
    name="Code Smith AI",
    seed="I am a code generating agent",
    port=8080,
    mailbox=True,  
    readme_path="README.md",
    publish_agent_details=True
)

fund_agent_if_low(code_smith.wallet.address()) #type:ignore

class CodeQuery(Model):
    task:str
    prompt: str
    language: str
    code:str
    description:str

class CodeResponse(Model):
    result: str

class HealthCheck(Model):
    pass

class HealthStatus(Model):
    status: str

@code_smith.on_message(model=HealthCheck)
async def handle_health_check(ctx: Context, sender: str, msg: HealthCheck):
    """Handle health check requests to ensure the agent is functioning properly"""
    try:
        test_result = main("Hello", "Java")
        if test_result and "Error" not in test_result:
            await ctx.send(sender, HealthStatus(status="healthy"))
        else:
            await ctx.send(sender, HealthStatus(status="unhealthy"))
    except Exception:
        await ctx.send(sender, HealthStatus(status="unhealthy"))

@code_smith.on_message(model=CodeQuery)
async def handle_query(ctx: Context, sender: str, msg: CodeQuery):
    ctx.logger.info(f"Received {msg.task} task")
    response = main(msg.task,msg.prompt, msg.language, msg.code, msg.description)
    await ctx.send(sender, CodeResponse(result=response))

code_smith.include(chat_proto, publish_manifest=True)

@code_smith.on_event('startup')
async def startup(ctx: Context):
    ctx.logger.info("Code Generation Agent started successfully!")

if __name__ == "__main__":
    code_smith.run()