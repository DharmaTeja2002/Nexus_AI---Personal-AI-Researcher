import openai
import asyncio
async def test():
    client = openai.AsyncOpenAI(base_url='http://localhost:11434/v1', api_key='test')
    try:
        res = await client.chat.completions.create(model='qwen2.5:3b', messages=[{'role': 'user', 'content': 'hello'}])
        print(res.choices[0].message.content)
    except Exception as e:
        print(f"Exception: {e}")
asyncio.run(test())
