from pydantic_ai import Agent

agent = Agent(
    "openai:gpt-3.5-turbo",
    system_prompt="Be concise, and funny about the question asking."
)

result = agent.run_sync('Where does "hello world" come from?')
print(result.data)