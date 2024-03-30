from LLMProviders.BaseLLMProvider import BaseLLMProvider
import anthropic

class ClaudeProvider(BaseLLMProvider):

    def login(self):
        self.include_system = False
        self.client = anthropic.Anthropic(api_key=self.api_key)
         #Nothing fancy needed here.

    def send(self):
        messages = self.get_messages()
        response = self.client.messages.create(
                max_tokens=1024,
                messages=messages,
                system=self.system,
                model=self.model,
            )
        return response.content[0].text



    def __init__(self, model, api_key):
        super().__init__(model, api_key)



