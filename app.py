from flask import Flask, jsonify, request
from openai import OpenAI
from dotenv import load_dotenv
import os, json
from slack_sdk import WebClient
from flask_ngrok import run_with_ngrok

app = Flask(__name__)
run_with_ngrok(app)  # Use ngrok for local testing

slack_client = WebClient(token='xoxb-6409820116198-6402567529575-WkBMRy0D6XF7GX4HAxANaJaa')
SLACK_VERIFICATION_TOKEN = 'gnj9eh0DGTywu2u2YonDPCwu'

load_dotenv()
client = OpenAI()
client.api_key = os.getenv("OPENAI_API_KEY")

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'png', 'jpg', 'json'}

@app.route('/slack/events', methods=['POST'])
def slack_events():
    if 'challenge' in request.json:
        return jsonify({'challenge': request.json['challenge']})
    else:
        data = request.get_json()
        if data['token'] != SLACK_VERIFICATION_TOKEN:
            return jsonify({'error': 'Invalid token'}), 403

        if 'event' in data:
            event = data['event']
            event_type = event['type']
            if event_type == 'message' and 'bot_id' not in event:
                message = data.get('event', {}).get('text', '')
                channel_id = data['event']['channel']
                response = process_message(message)
                slack_client.chat_postMessage(channel=channel_id, text=response)

    return jsonify({'Message': 'Hello from World!'})

def process_message(message):
    assistant_id = "asst_JTCSfhHOOtm0DgMEZTTWxsX8"

    # Create thread, message, and run the assistant
    thread = client.beta.threads.create()
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=message
    )
    
    run = client.beta.threads.runs.create(
        thread_id=thread.id, 
        assistant_id=assistant_id
        )
    # Wait for the assistant to complete
    while run.status != 'completed':
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id, 
            run_id=run.id
    )
    # Get the assistant's response
    messages = client.beta.threads.messages.list(
        thread_id=thread.id
    )
    
    for message in messages:
        if message.role == "assistant":
            myresponse = message.content[0].text.value
            break
    print("I am after message creation")
    return myresponse

if __name__ == '__main__':
    app.run()
