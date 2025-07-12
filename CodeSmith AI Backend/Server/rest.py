from uagents import Agent, Model, Context
from uagents.setup import fund_agent_if_low

class CodeQuery(Model):
    prompt: str

class DebugQuery(Model):
    code: str
    description:str

class CodeResponse(Model):
    result: str

rest=Agent(name="Rest Agent", seed="CodeSmith Rest Agent", port=8000, endpoint="http://localhost:8000/submit")

code_smith_agent="agent1qg609e07k000ft2tg7yvq5qmad53fhkd7ausvc27x5mxu5v8lue8zl6p54n"

fund_agent_if_low(rest.wallet.address()) #type: ignore

@rest.on_rest_get("/check", CodeResponse)
async def check(_: Context)->CodeResponse:
    return CodeResponse(result="Check Complete")

@rest.on_rest_post("/generate", CodeQuery, CodeResponse)
async def code_gen(ctx: Context, req:CodeQuery)->CodeResponse:
    print(f"Query received: {req.prompt}")
    response_tuple = await ctx.send_and_receive(code_smith_agent, CodeQuery(prompt=req.prompt), response_type=CodeResponse)
    if response_tuple and isinstance(response_tuple, tuple) and len(response_tuple) > 0 and response_tuple[0]:
        output = response_tuple[0].result  # type: ignore
        print(output)
        return CodeResponse(result=output)
    else:
        return CodeResponse(result="No response received")
    
@rest.on_rest_post("/debug", DebugQuery, CodeResponse)
async def code_debug(ctx:Context, req: DebugQuery)->CodeResponse:
    response_tuple = await ctx.send_and_receive(code_smith_agent, DebugQuery(code=req.code, description=req.description), response_type=CodeResponse)
    if response_tuple and isinstance(response_tuple, tuple) and len(response_tuple) > 0 and response_tuple[0]:
        output = response_tuple[0].result  # type: ignore
        print(output)
        return CodeResponse(result=output)
    else:
        return CodeResponse(result="No response received")

if __name__=="__main__":
    rest.run()