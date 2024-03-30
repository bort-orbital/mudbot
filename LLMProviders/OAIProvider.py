from LLMProviders.BaseLLMProvider import BaseLLMProvider
import openai


class OAIProvider(BaseLLMProvider):

    def login(self):
        self.include_system = True
        self.client  = openai.OpenAI(
            api_key=self.api_key,
        )


    def send(self):
        messages = self.get_messages()
        response = self.client.chat.completions.create(
                max_tokens=1024,
                messages=messages,
                model=self.model,
        )
        return response.choices[0].message.content

    def __init__(self, model, api_key):
        super().__init__(model, api_key)



