import shelve


class ConversationDataManager :
    def __init__(self, chat_type):
        self.chat_type = chat_type
        pass

    def store_carousel(self):
        pass

    def store_card(self):
        pass

    def store_text_res(self):
        pass

    def store_audio_res(self):
        pass

    def store_emoji_react(self):
        pass


    def get_chat_type(self):
        print("Chat Type: ", self.chat_type)

        chat_types = {
            "carousel": None,
            "card": None,
            "text_response":None,
            "emoji_response":None,
            "audio_response":None,
            "audio_message":None,
            "text_response":None
        }

        chat_action = chat_types.get(str(self.chat_type))

        chat_types_args = {
            "carousel":None,
            "card":None,
            "text_response":None,
            "emoji_response":None,
            "audio_response":None,
            "audio_message":None,
            "text_response":None
        }

        args = chat_types_args.get(str(self.chat_type))
        
        if chat_action:
            return chat_action(*args)
        pass