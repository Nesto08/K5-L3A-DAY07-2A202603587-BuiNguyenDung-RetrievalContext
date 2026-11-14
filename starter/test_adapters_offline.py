"""No API calls: smoke-test adapter contracts and grounded citation flow."""
import json
from types import SimpleNamespace as NS

from adapters import HybridRetriever, OpenAIController
from agentic import run_agent

class Embeddings:
    def create(self, **kwargs):
        assert kwargs['input'] == 'What is print?'
        return NS(data=[NS(embedding=[0.0]*1536)], usage=NS(total_tokens=5))

class Chats:
    def __init__(self): self.calls=0
    def create(self, **kwargs):
        self.calls+=1
        assert kwargs['tools'][0]['function']['name']=='search_documents'
        if self.calls==1:
            assert kwargs['tool_choice']=='required'
            msg=NS(tool_calls=[NS(function=NS(arguments=json.dumps({'query':'What is print?'})))],content=None)
        else:
            assert kwargs['tool_choice']=='auto'
            msg=NS(tool_calls=[], content='It prints text. [c1]')
        return NS(choices=[NS(message=msg)], usage=NS(prompt_tokens=10, completion_tokens=5))

class FakeClient:
    def __init__(self):
        self.embeddings=Embeddings()
        self.chat=NS(completions=Chats())

class FakeCollection:
    def count(self): return 1
    def get(self, **kwargs): return {'ids':['c1']}
    def query(self, **kwargs):
        assert 'gold' not in str(kwargs)
        return {'ids': [['c1']], 'distances': [[0.25]]}

chunk = {'id':'c1','source_id':'test','source':'test.pdf','page':1,
         'text':'The print() function prints text to the user.','metadata':{'chapter':'1'}}
client=FakeClient()
r=HybridRetriever([chunk],FakeCollection(),client)
c=OpenAIController(client)
result=run_agent('What is print?',c,r,budget=1600, top_k=3)
assert result['status']=='answered',result
assert result['citations']==['c1']
assert result['events'][0]['event']=='search'
assert client.chat.completions.calls==2
print('PASS: hybrid adapter + real tool-call contract + citation loop (offline fake clients)')
