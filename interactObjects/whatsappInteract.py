import re

from load_env import load_vars
from responseComponents import audioResponse, buttonReply, text, emojiReaction

load_vars()


class WhatsAppHandler:

    def __init__(self, phone_number_id, phone_number, message_id):
        self.phone_number_id = phone_number_id
        self.phone_number = phone_number
        self.message_id = message_id


  
    async def message_wa(self, assistant_text, user_message):
        print(assistant_text)
        # Define the regular expression pattern to find the end message
        pattern = r'\s*OUTPUT TYPE:\s*\'([^\']+)\'$'
        
        # Search for the pattern in the text
        match = re.search(pattern, str(assistant_text), re.IGNORECASE)
        print("Match/output type: ", match)

        # If a match is found, extract the output type and remove it from the text
        if match:
            output_type = match.group(1).lower()  # Extract and lowercase the output type
            ai_output = re.sub(pattern, '', str(assistant_text), flags=re.IGNORECASE)  # Remove the pattern from the text
            print("New reformatted text: ", ai_output)
            print(output_type)
            output_type_mapping = {
                "text": text.text,
                "audio": audioResponse.audioMessage,
                "button_reply": buttonReply.buttonReply,
                "emoji_react": emojiReaction.emojiReaction
            }

            # Get the corresponding function based on output_type
            post_function = output_type_mapping.get(str(output_type))

            args_mapping = {
                "text": (ai_output, self.phone_number, self.phone_number_id),
                "audio": (ai_output, self.phone_number, self.phone_number_id),
                "button_reply": (ai_output, self.phone_number, self.phone_number_id, user_message, output_type),
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


