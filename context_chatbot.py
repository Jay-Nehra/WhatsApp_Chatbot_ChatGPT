import logging
import time
import openai  
import secrets
from flask import Flask, request, session
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from DB import TinyDB  

# Initialize logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Initialize OpenAI API key
openai.api_key = "YOUR_OPENAI_API_KEY"

# Twilio Configuration
account_sid = 'YOUR_TWILIO_SID'
auth_token = 'YOUR_TWILIO_AUTH_TOKEN'
client = Client(account_sid, auth_token)

# Initialize the in-memory database
db = TinyDB(db_location='tmp', in_memory=False)

def sendMessage(body_mess, phone_number):
    try:
        MAX_MESSAGE_LENGTH = 550 

        # Split the message into lines and words
        lines = body_mess.split('\n')
        chunks = []
        current_chunk = ""

        for line in lines:
            words = line.split()
            for word in words:
                if len(current_chunk) + len(word) + 1 > MAX_MESSAGE_LENGTH:
                    # Save the current chunk and start a new one
                    chunks.append(current_chunk.strip())
                    current_chunk = ""

                current_chunk += word + " "

            # Add a newline character at the end of each line
            current_chunk += "\n"

        # Add the last chunk
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        total_chunks = len(chunks)

        for i, chunk in enumerate(chunks):
            part_number = f"[{i+1}/{total_chunks}]"
            final_chunk = f"{chunk} {part_number}"
            
            logging.debug(f"Sending message chunk: {final_chunk} to {phone_number}")
            
            message = client.messages.create(
                from_='whatsapp:+14155238886',
                body=final_chunk,
                to='whatsapp:' + phone_number
            )
            
            time.sleep(1)  # Optional: To avoid rate-limiting

    except Exception as e:
        logging.error(f"Failed to send message. Error: {str(e)}")

def get_chatgpt_response(prompt, phone_number):
    logging.debug(f"Received prompt: {prompt}")

    # Fetch the last 5 conversations from the database for this phone_number
    all_conversations = db.read_list_record("conversations", phone_number, default=[])
    last_5_conversations = all_conversations[-10:]
    print()
    print(last_5_conversations)
    
    print()
    print()
    print()

    # Format the conversations for use in the GPT-3 API call
    previous_conversation = "\n".join([f'User: {conv["user_message"]}\nAssistant: {conv["gpt_response"]}' for conv in last_5_conversations])

    # Prepare the system message
    system_message = f"""As a travel assistant WhatsApp chatbot, your primary responsibility is to create tailored travel itineraries based on user input. Your responses should accurately interpret and address the user's questions and requirements. Utilize details such as *name*, *age*, *current location*, *preferred destinations*, *travel dates*, *budget*, *travel companions*, *interests or hobbies*, *special requirements*, *duration of the trip*, *mode of transportation*, and *previous travel experiences* to offer a comprehensive and personalized travel itinerary.

*Context Awareness*:
- For ongoing conversations, make use of the context provided by the last five user messages and chatbot responses to understand the current state of the interaction.
- Determine if the current message is the beginning of a new inquiry or a continuation of an existing one.
- If information like *budget*, *travel companions*, or *interests* has already been discussed, do not prompt for it again unless clarification is needed.


*WhatsApp Formatting Guidelines*:
- ALWAYS use '\n' as new line charector. 
- Use bullet points simulated by numbers and new lines for structuring any ordered lists within the response. Example:\n1. Item 1\n2. Item 2
- For unordered lists, use hyphens and new lines as bullet points. Example:\n- Available activities: swimming, hiking\n- Recommended destinations: Paris, Tokyo
- Use *asterisks* for **bold text**, _underscores_ for _italic text_, and ~tildes~ for ~~strikethrough~~. To represent `code`, use ```backticks```.
- Ensure each list item is clearly separated by a new line (\\n) for better readability.
- Activities or options within each list should be presented in the recommended order of completion or relevance.
- Separate different sections or categories with an empty line (\\n) for clarity.

Your role is to deliver this personalized service through the WhatsApp platform, ensuring a seamless and convenient user experience. Always adhere to these formatting guidelines to maintain the quality of the user interactions.
"""


    
    # Prepare the messages payload
    messages = [
        {
            "role": "system",
            "content": system_message
        }
    ]
    
    if previous_conversation:
        # Append the previous conversation to the system message
        messages[0]["content"] += f"\n\nHere are the five previous user messages and chatbot responses for context:\n\n{previous_conversation}"
        
    messages.append({
        "role": "user",
        "content": prompt
    })

    try:
        logging.debug("Fetching previous conversations from database...")
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=messages,
            temperature=0.75,
            max_tokens=1024,
            n=1,
            stop=None
        )
        
        generated_response = response['choices'][0]['message']['content'].strip()

        # Store the conversation in the database
        new_conversation = {
            "user_message": prompt,
            "gpt_response": generated_response
        }
        
        db.append_to_conversation("conversations", phone_number, new_conversation)
        print(new_conversation , "look at this jayant")
        logging.debug("Successfully upserted new conversation.")
        
        return generated_response if generated_response else ''
    except openai.OpenAIError as e:
        logging.error("Error from OpenAI API", exc_info=True)
        return "Error occurred while retrieving response from OpenAI API."

@app.route('/sms', methods=['POST'])
def sms_reply():
    incoming_msg = request.form.get('Body')
    phone_number = request.form.get('From')
    session_id = session.get('session_id', None)
    
    if not session_id:
        session_id = secrets.token_hex(16)
        session['session_id'] = session_id

    logging.debug(f"Incoming message from {phone_number}: {incoming_msg}")

    if incoming_msg:
        answer = get_chatgpt_response(incoming_msg, phone_number)
        sendMessage(answer, phone_number[9:])
    else:
        sendMessage("Message cannot be empty!", phone_number[9:])

    resp = MessagingResponse()
    resp.message("")
    return str(resp)

if __name__ == '__main__':
    app.run(debug=True)
