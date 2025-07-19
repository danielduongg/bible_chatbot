import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure the Gemini API with your API key
try:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
except KeyError:
    print("Error: GEMINI_API_KEY not found in environment variables.")
    print("Please make sure you have a .env file with GEMINI_API_KEY=YOUR_API_KEY")
    exit()

def find_generative_model():
    # print("Checking available Gemini models...") # Commented out for cleaner web app logs

    target_models = ["gemini-1.5-flash", "gemini-1.0-pro", "gemini-pro"] 

    for model_preference in target_models:
        for m in genai.list_models():
            if m.name == f"models/{model_preference}" and "generateContent" in m.supported_generation_methods:
                if m.input_token_limit > 0:
                    # print(f"Found suitable model: {m.name}") # Commented out for cleaner web app logs
                    return m.name

    print("No suitable generative text model found with 'generateContent' support.")
    print("Please check your API key, region, or Google AI Studio for available models.")
    return None

class BibleChatbot:
    def __init__(self):
        model_name = find_generative_model()
        if not model_name:
            exit("Exiting: No suitable Gemini model found.")

        self.model = genai.GenerativeModel(model_name)

        # We need to ensure the chat history is tied to a *session* for a web app.
        # For this basic example, we'll start a fresh chat with each request.
        # For persistent chat, you'd store history in a session or database.
        self.chat = self.model.start_chat(history=[])
        self.initial_prompt = (
            "You are a helpful AI assistant specialized in the English Standard Version (ESV) Bible. "
            "Your goal is to provide accurate and contextually relevant answers to questions about "
            "Bible verses, stories, characters, and theological concepts, specifically from the ESV translation. "
            "If a user asks for a specific verse, try to provide it as accurately as possible. "
            "If you don't have enough information to answer a specific question about the ESV Bible, "
            "kindly state that you cannot provide a definitive answer based on the provided context. "
            "Always maintain a respectful and informative tone."
        )
        # Send the initial system instruction
        self.chat.send_message(self.initial_prompt)

    def get_bible_response(self, user_query):
        try:
            # We'll send the initial prompt with every *new* chat instantiation for simplicity.
            # In a more advanced Flask app, you'd manage session history.
            # For now, let's keep the initial prompt logic within __init__ and assume
            # a new chat is started per request for simplicity if not handling sessions.
            # However, to actually maintain chat history with Gemini, the `self.chat` object
            # needs to persist across requests for a user. For a truly stateful chatbot,
            # you'd need Flask's `session` object or a backend database.

            # For now, let's ensure the initial prompt is sent once per chat session.
            # This current setup in __init__ sends it only when the object is created.
            # If we instantiate BibleChatbot per request, the history will be short-lived.
            # For this basic Flask example, we will let the `start_chat` manage it.

            # The `guided_query` logic will now be handled in the Flask app.
            response = self.chat.send_message(user_query)
            return response.text
        except Exception as e:
            return f"An error occurred while communicating with the Gemini API: {e}"