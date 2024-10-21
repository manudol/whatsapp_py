import re

from load_env import load_vars
from responseComponents import audioResponse, card, carousel, text, emojiReaction, ctaURL

load_vars()


class WhatsAppHandler:

    def __init__(self, assistant_text, phone_number_id, phone_number, message_id):
        self.phone_number_id = phone_number_id
        self.phone_number = phone_number
        self.assistant_text = assistant_text
        self.message_id = message_id


  
    async def message_wa(self):
        print(self.assistant_text)
        # Define the regular expression pattern to find the end message
        pattern = r'\s*OUTPUT TYPE:\s*\'([^\']+)\'$'
        
        # Search for the pattern in the text
        match = re.search(pattern, str(self.assistant_text), re.IGNORECASE)
        
        # If a match is found, extract the output type and remove it from the text
        if match:
            output_type = match.group(1).lower()  # Extract and lowercase the output type
            ai_output = re.sub(pattern, '', str(self.assistant_text), flags=re.IGNORECASE)  # Remove the pattern from the text
            print("New reformatted text: ", ai_output)
            print(output_type)
            output_type_mapping = {
                "text": text.text,
                "audio": audioResponse.audioMessage,
                "carousel": carousel.carousel,
                "ctaURL": ctaURL.cta_url,
                "card": card.card,
                "emoji_react": emojiReaction.emojiReaction
            }

            # Get the corresponding function based on output_type
            post_function = output_type_mapping.get(str(output_type))

            args_mapping = {
                "text": (ai_output, self.phone_number, self.phone_number_id),
                "audio": (ai_output, self.phone_number, self.phone_number_id),
                "carousel": (ai_output, self.phone_number, self.phone_number_id),
                "ctaURL": (ai_output, self.phone_number, self.phone_number_id),
                "card": (ai_output, self.phone_number, self.phone_number_id),
                "emoji_react": (ai_output, self.phone_number, self.phone_number_id, self.message_id),
            }

            args = args_mapping.get(str(output_type))

            if post_function:
                print(f"Trigerring function: {post_function.__name__}")
                return await post_function(*args)
            else:
                # Default action or error handling
                raise ValueError("Unable to trigger any post funtion")
                
        else:
            # Default action or error handling
            raise ValueError("No match. OUTPUT TYPE not found.")


