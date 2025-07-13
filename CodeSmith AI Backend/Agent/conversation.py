from together import Together
from dotenv import load_dotenv
import os

load_dotenv()

os.environ["TOGETHER_API_KEY"] = os.getenv("TOGETHER_API_KEY") #type:ignore

client = Together()

GENERATE_PROMPT_STRING='''
You are an expert programmer. Execute the query:{query} and generate the response in the preferred language:{language}. The output format should be:
1. Code
2. Explanation
'''

DEBUG_PROMPT_STRING='''
You are a debugging assistant. Help me find and fix bugs in the following code.
Code:
{code}

(Optional) Description of the Issue:
{description}

The output format should be:
1. Code
2. Explanation
'''

TC_PROMPT_STRING='''
You are a QA engineer. Generate test cases for the following function or module.

Code:
{code}

(Optional) Description:
{description}

Provide relevant unit test cases using a suitable framework for the code's language (e.g., JUnit for Java, PyTest for Python, Jest for JavaScript).The output format should be:
1. Test cases
2. Explanation
'''

README_PROMPT_STRING='''
You are a technical writer. Create a clear and professional `README.md` file for the following project.

Code:
{code}

Description:
{description}

Include sections like:
- Project Title
- Description
- Features
- Installation
- Usage
- Example
- License
'''

def generate_with_together(query: str, language:str) -> str:
    try:
        final_prompt=GENERATE_PROMPT_STRING.format(query=query, language=language)
        response = client.chat.completions.create(
            model="Qwen/Qwen2.5-Coder-32B-Instruct",
            messages=[
                {
                    "role": "user",
                    "content": final_prompt
                }
            ],
            stream=False  
        )
        if hasattr(response, 'choices'):
            return response.choices[0].message.content #type:ignore
        return "Unable to generate a response."
    except Exception as e:
        return f"Error occurred: {str(e)}"