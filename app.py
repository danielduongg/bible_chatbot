from flask import Flask, render_template, request, jsonify, session
from bible_chatbot_logic import BibleChatbot
import os

app = Flask(__name__)
app.secret_key = os.urandom(24) # A secret key for session management

# Initialize the chatbot once when the application starts
# This avoids re-initializing the model for every request, which is efficient.
# However, for maintaining chat history per user, we need session management.
# For this basic example, we will re-initialize the chat *object* per request
# to demonstrate. For a truly persistent per-user chat, you'd store the
# `chat` object or its history in Flask's `session` or a database.

# Global instance (will re-initialize its internal `chat` for each request as per our current logic)
# OR, better: instantiate the chatbot per user session.

# Let's instantiate the chatbot logic here, but manage its `chat` history more carefully.
# A simple approach for multi-turn conversations in Flask is to store the history
# in the Flask session.

# Initialize the base chatbot logic (model setup)
initial_chatbot_logic = BibleChatbot() 


@app.route('/')
def index():
    # Clear existing chat history in session when visiting the main page
    session.pop('chat_history', None) 
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask_chatbot():
    user_message = request.json.get('message')
    if not user_message:
        return jsonify({"response": "Please enter a message."}), 400

    # Retrieve chat history from session or initialize it
    chat_history = session.get('chat_history', [])

    # Create a new chat session with the historical context for each request
    # This allows multi-turn conversations.
    # Ensure 'role' is alternating 'user' and 'model'
    # The initial prompt needs to be sent only once per *new* conversation.
    # We handle this by prepending it to the history if it's a fresh chat.

    # Prepare history for Gemini API
    gemini_history = []
    # Add the initial prompt as the first message from the model in the history
    # (This acts as the system instruction)
    gemini_history.append({"role": "user", "parts": [initial_chatbot_logic.initial_prompt]})
    gemini_history.append({"role": "model", "parts": ["Understood. What would you like to know about the ESV Bible?"]})

    for entry in chat_history:
        gemini_history.append({"role": entry['role'], "parts": [entry['text']]})

    # Instantiate a new chat with the compiled history
    # This creates a *new* chat object for each request but injects previous turns.
    temp_chat_session = initial_chatbot_logic.model.start_chat(history=gemini_history)

    try:
        # Guide the user query (optional, but good for focus)
        guided_query = f"Regarding the ESV Bible, {user_message}"
        response = temp_chat_session.send_message(guided_query)
        chatbot_response = response.text
    except Exception as e:
        chatbot_response = f"An error occurred: {e}"

    # Update chat history in session
    chat_history.append({"role": "user", "text": user_message})
    chat_history.append({"role": "model", "text": chatbot_response})
    session['chat_history'] = chat_history # Save updated history

    return jsonify({"response": chatbot_response})

if __name__ == '__main__':
    print("Starting Flask web server...")
    print("Open your browser and navigate to http://127.0.0.1:5000/")
    # Use debug=True for development (auto-reloads, shows errors)
    # Set threaded=True to handle multiple users concurrently (important for web apps)
    app.run(debug=True, threaded=True)