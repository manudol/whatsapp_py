from openai_client.client import client


class Structo:
    def __init__(self, ai_output: str, Model: object):
        self.ai_output = ai_output
        self.Model = Model

    def get_structo(self):
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-2024-02-15",
            messages=[{"role": "system", 
                       "content": f"You are a helpful assistant that can help with structuring data. \
                       Structure your output using the informaitons found in the whatsapp bot's ai message: {self.ai_output}. \
                       For context you are outputing data that will be parsed ot send messages to users interacting with a company on whatsapp through a whatsapp bot. \
                       Usually the bot's message is already well labeled and structured.\
                       The data is: {self.ai_output}"}],
            response_format=self.Model
            )
        return completion.choices[0].message.parsed