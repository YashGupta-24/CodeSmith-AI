# Code Generation Agent  
![tag:innovationlab](https://img.shields.io/badge/innovationlab-3D8BD3)
![tag:ILIndia](https://img.shields.io/badge/ILIndia-3D8BD3)

The **Code Generation Agent** is an AI-powered uAgent that generates code or text responses based on user prompts. It utilizes the [Together API](https://www.together.ai/) with the powerful `Qwen2.5-Coder-32B-Instruct` model to produce high-quality code completions and explanations.

This agent supports both **chat-based messaging** and **direct message queries** via Fetch.ai's Agentverse framework. It is ideal for developers, coders, or anyone who wants to generate code snippets, logic, or explanations quickly and conversationally.

---

## Input Data Model

```python
class CodeQuery(Model):
    prompt: str
```
## Output Data Model
```python
class CodeResponse(Model):
    result: str
```