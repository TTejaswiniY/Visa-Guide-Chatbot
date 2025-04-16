from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/chat', methods=['POST'])
def chat():
    # Get the message sent from React frontend
    data = request.get_json()
    user_message = data.get('message', '')

    # Here, you can put your logic for generating a bot response based on the user message.
    # For now, we're just going to send back a mock response.
    bot_response = "You said: " + user_message  # This is just an example

    # Return the bot response as a JSON object
    return jsonify({"reply": bot_response})

if __name__ == "__main__":
    app.run(debug=True)
