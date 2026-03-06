with open('tests/test_strategy_debate_api.py', 'r') as f:
    content = f.read()

content = content.replace("def conduct_debate(self, ticker, **kwargs):", "async def conduct_debate(self, ticker, context=None, **kwargs):")

with open('tests/test_strategy_debate_api.py', 'w') as f:
    f.write(content)
