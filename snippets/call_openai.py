"""
File   : call_openai.py
Desc   : 调用 OpenAI API 的示例
Date   : 2025/04/16
Author : Tianyu Chen
https://platform.openai.com/docs/guides/function-calling?api-mode=responses
"""


from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()
MODEL = "qwen-max"

tools = [
{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Retrieves current weather for the given location.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City and country e.g. Bogotá, Colombia"
                },
                "units": {
                    "type": "string",
                    "enum": [
                        "celsius",
                        "fahrenheit"
                    ],
                    "description": "Units the temperature will be returned in."
                }
            },
            "required": [
                "location",
                "units"
            ],
            "additionalProperties": False
        },
        "strict": True
    }
}
]
messages = [{"role": "user", "content": "What's the weather like in Beijing today?"}]
completion = client.chat.completions.create(
  model=MODEL,
  messages=messages,
  tools=tools,
  tool_choice={"type": "function", "function": {"name": "get_weather"}}
)


print(completion)

""" output:
ChatCompletion(
  id='chatcmpl-946e4211-0c3e-9e50-91b3-f8c9cf210872', 
  choices=[
    Choice(
      finish_reason='tool_calls', 
      index=0, 
      logprobs=None, 
      message=ChatCompletionMessage(
        content='', 
        refusal=None, 
        role='assistant', 
        annotations=None, 
        audio=None, 
        function_call=None, 
        tool_calls=[
          ChatCompletionMessageToolCall(
            id='call_261205e6b567462fb6d1b1', 
            function=Function(
              arguments='{"location": "Beijing, China", "units": "celsius"}', 
              name='get_weather'
            ), 
            type='function', 
            index=0
          )
        ]
      )
    )
  ], 
  created=1744784573, 
  model='qwen-max', 
  object='chat.completion', 
  service_tier=None, 
  system_fingerprint=None, 
  usage=CompletionUsage(
    completion_tokens=21, 
    prompt_tokens=233, 
    total_tokens=254, 
    completion_tokens_details=None, 
    prompt_tokens_details=PromptTokensDetails(audio_tokens=None, cached_tokens=0)
  )
)
"""
