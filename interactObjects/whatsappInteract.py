import re

from responseComponents import audioResponse, buttonReply, text, location, sendLocation, product


class WhatsAppHandler:

    def __init__(self, phone_number_id, phone_number, message_id, access_token, business_id, output_type):
        self.phone_number_id = phone_number_id
        self.phone_number = phone_number
        self.message_id = message_id
        self.access_token = access_token
        self.business_id = business_id
        self.output_type = output_type

    async def message_wa(self, assistant_text, user_message):
        print(assistant_text)

        merge_pattern = r'^merged_content'
        
        if re.match(merge_pattern, assistant_text):
            # Split merged content into individual messages
            messages = assistant_text.replace('merged_content', '').split('?%67?')
            
            # Process each message
            output_types = []
            ai_outputs = []
            pattern = r'OUTPUT TYPE:\s*([a-zA-Z_]+)(?:\s*\||$)'
            
            for message in messages:
                match = re.search(pattern, str(message), re.IGNORECASE)
                if match:
                    output_type = match.group(1).strip().lower()
                    ai_output = re.sub(pattern, '', str(message), flags=re.IGNORECASE)
                    output_types.append(output_type)
                    ai_outputs.append(ai_output)

            # Map functions
            output_type_mapping = {
                "text": text.text,
                "audio": audioResponse.audioMessage, 
                "cta_button": buttonReply.buttonReply,
                "location": location.location,
                "request_location": sendLocation.sendLocation,
                "product": product.product
            }

            # Process each message in sequence
            for i, (output_type, ai_output) in enumerate(zip(output_types, ai_outputs)):
                post_function = output_type_mapping.get(output_type)
                
                if post_function:
                    args_mapping = {
                        "text": (output_type, ai_output, self.phone_number, self.phone_number_id),
                        "audio": (output_type, ai_output, self.phone_number, self.phone_number_id),
                        "cta_button": (output_type, assistant_text, ai_output, self.phone_number, self.phone_number_id),
                        "location": (output_type, assistant_text, ai_output, self.phone_number, self.phone_number_id),
                        "request_location": (output_type, ai_output, self.phone_number, self.phone_number_id),
                        "product": (output_type, ai_output, self.phone_number, self.phone_number_id, self.access_token, self.business_id)
                    }
                    
                    args = args_mapping.get(output_type)
                    if args:
                        await post_function(*args)
                        
            return {
                "output_type": output_types,
                "assistant_message": ai_outputs,
                "user_message": user_message,
                "double_message": True
            }
        # Define the regular expression pattern to find the end message
        pattern = r'OUTPUT TYPE:\s*([a-zA-Z_]+)(?:\s*\||$)'  # Match OUTPUT TYPE followed by word chars until | or end
        
        # Search for the pattern in the text
        match = re.search(pattern, str(assistant_text), re.IGNORECASE)
        print("Match/output type: ", match)
        print("Full text being searched:", assistant_text)

        # If a match is found, extract the output type and remove it from the text
        if match:
            output_type = match.group(1).lower().strip()  # Extract, lowercase and strip the output type
            ai_output = re.sub(pattern, '', str(assistant_text), flags=re.IGNORECASE).strip()  # Remove pattern and trim
            print("New reformatted text: ", ai_output)
            print("Extracted output type:", output_type)
            output_type_mapping = {
                "text": text.text,
                "audio": audioResponse.audioMessage,
                "cta_button": buttonReply.buttonReply,
                "location": location.location,
                "request_location": sendLocation.sendLocation,
                "product": product.product
            }

            # Get the corresponding function based on output_type
            post_function = output_type_mapping.get(str(output_type))

            args_mapping = {
                "text": (ai_output, self.phone_number, self.phone_number_id),
                "audio": (ai_output, self.phone_number, self.phone_number_id),
                "cta_button": (assistant_text, ai_output, self.phone_number, self.phone_number_id),
                "location": (assistant_text, ai_output, self.phone_number, self.phone_number_id),
                "request_location": (ai_output, self.phone_number, self.phone_number_id),
                "product": (ai_output, self.phone_number, self.phone_number_id, self.access_token, self.business_id)
            }

            args = args_mapping.get(str(output_type))

            if post_function:
                print(f"Trigerring function: {post_function.__name__}")
                await post_function(*args)
                return {"output_type": output_type, 
                        "assistant_message": ai_output,
                        "user_message": user_message,
                        "double_message": False}
            else:
                # Default action or error handling
                raise ValueError("Unable to trigger any post funtion")
                
        else:
            # Default action or error handling
            raise ValueError("No match. OUTPUT TYPE not found.")