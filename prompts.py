system_prompt="you are a testing assistant in an app being developed just respond to my questions in the testing environment\
    please please please it is vital that you end your responses (all the time !) with the words  'OUTPUT TYPE: 'text'' to signal to the \
    application that your output is for text messaging format.\
    please end each of your responses with the words: 'OUTPUT TYPE: 'text''.\
    Still respond as instructed above if the information on user_message is text, audio or image."




def craft_genai_prompt(prompt2gen, phone_number):
    if prompt2gen == "button_reply":
        structure = """
        {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": phone_number,
                "type": "interactive",
                "interactive": {
                    "type": "button",
                    "header": None,
                    "body": {
                    "text": body_text
                    },
                    "footer": {
                    "text": footer_text
                    },
                    "action": {
                    "buttons": [
                        {
                        "type": "reply",
                        "reply": {
                            "id": "change-button",
                            "title": button1_title
                        }
                        },
                        {
                        "type": "reply",
                        "reply": {
                            "id": "cancel-button",
                            "title": button2_title
                        }
                        },
                        ... more buttons if necessary.
                    ]
                    }
                }
                }
        """

    genai_prompt = f"Prompt structure: {structure}\
        please generate a prompt in this style.\
        replace phone_number snake case text by the actual phone: {phone_number}\
        replace all the other snake case variables with relevant text to properly \
        craft the interactive element that will be rendered by the whatsapp api.\
        VERY IMPORTANT: DO NOT forget to stay absolutely loyal to the structure\
        otherwise the api call that will use the json that you generated will fail.\
        **VERY VERY VERY VERY IMPORTANT: DO NOT GENERATE ANYTHNG ELSE OUTSIDE OF THE JSON BODY\
        YOUR MESSAGE SHOULD START WITH A SQUIGLY BRAKET AND CLOSE WITH ONE!"
    
    return genai_prompt