from flask import Flask, request, jsonify
import base64
import logging
from google.cloud import bigquery
from datetime import datetime

app = Flask(__name__)

# Set up BigQuery client
client = bigquery.Client()

@app.route('/webhook', methods=['POST'])
def handleRequest(request):
    # Parse the request body
    req = request.get_json(silent=True, force=True)
    print(f"Request: {req}")
    
    # Get the intent name from the request
    intent = req['queryResult']['intent']['displayName'].strip()
    print(f"Received request for intent: {intent}")
    
    #if req['queryResult']['parameters']['emotions']:
        # Extract user ID
    #    user_id = get_user_id_from_request(req)

        # Insert data into BigQuery
    #    insert_bigquery_data(user_id, intent, req)  

    
    if intent == 'EmotionRecognition':
        response_text = handle_emotion_intent(req)
    elif intent == 'FollowUp':
        response_text = handle_follow_up_intent(req)
    elif intent == 'DurationRecognition':
        response_text = handle_duration_intent(req)
    elif intent == 'ResourceOffer':
        response_text = handle_resource_offer_intent(req)
    elif intent == 'Closure':
        response_text = handle_closure_intent(req)
    else:
        response_text = 'Default response'

    # Send the response back to Dialogflow
    response = {'fulfillmentText': response_text}
    return jsonify(response)

def get_user_id_from_request(req):
    source = req['originalDetectIntentRequest']['source']
    
    if source == 'telegram':
        user_id = req['originalDetectIntentRequest']['payload']['data']['from']['id']
    elif 'messenger' in req['session']:
        session = req['session']
        user_id = session.split('/')[-1]
    else:
        user_id = str(uuid.uuid4())
    
    return str(user_id)


def insert_bigquery_data(user_id, intent, req):
    dataset_id = 'GCPsycheBot_data'
    table_id = 'user_emotions'
    timestamp = datetime.utcnow()
    detected_emotion = req['queryResult']['parameters']['emotions']

    row = {
        'user_id': user_id,
        'timestamp': timestamp,
        'intent': intent,
        'parameters': str(req['queryResult']['parameters']),
        'emotion': detected_emotion
    }
    print(f"User ID: {user_id}")
    print(f"Intent: {intent}")
    print(f"Timestamp: {timestamp}")
    print(f"Detected Emotion: {detected_emotion}")

    table_ref = client.dataset(dataset_id).table(table_id)
    table = client.get_table(table_ref)
    errors = client.insert_rows_json(table, [row])

    if errors:
        print(f"Error inserting row into BigQuery: {errors}")
    else:
        print(f"Row inserted into BigQuery successfully.")

def handle_emotion_intent(req):
    # Extract relevant information from the request
    detected_emotion = req['queryResult']['parameters']['emotions']
    
    # Perform custom logic based on the detected emotion
    if detected_emotion == 'Lonely':
        response_text = "I'm sorry to hear that you're feeling lonely. It's okay to feel this way. Can you tell me more about what's going on?"
    elif detected_emotion == 'Sad':
        response_text = "I'm here for you. Feeling sad is a common experience. Why do you think you're feeling this way?"
    elif detected_emotion == 'Overwhelmed':
        response_text = "Feeling overwhelmed is tough. I'm here to listen. Can you share more about what's on your mind?"
    # Add more conditions for other emotions

    return response_text


def handle_follow_up_intent(req):
    # Extract relevant information from the request
    user_response = req['queryResult']['queryText']

    # Perform custom logic based on the user's response
    if 'been like this for a while' in user_response:
        response_text = 'I appreciate you sharing that. Feeling this way can be challenging. Can you share more about what you\'ve been going through recently?'
    elif 'trying to understand it myself' in user_response:
        response_text = 'It\'s okay not to have all the answers. Feeling this way can be challenging. Can you share more about what you\'ve been going through recently?'
    elif 'wish I had an answer' in user_response:
        response_text = 'It\'s okay not to have all the answers. Feeling this way can be challenging. Can you share more about what you\'ve been going through recently?'
    elif 'I don\'t know' in user_response:
        response_text = 'It\'s okay not to have all the answers. Feeling this way can be challenging. Can you share more about what you\'ve been going through recently?'
    
    return response_text


def handle_duration_intent(req):
    # Extract relevant information from the request
    duration_value = req['queryResult']['parameters']['EmotionDuration']

    # Perform custom logic based on the duration
    if duration_value == 'FewWeeks':
        response_text = 'Thank you for opening up. It\'s essential to acknowledge our emotions. In situations like this, reaching out to friends, family, or a mental health professional can provide valuable support. How has your experience been over the past few weeks?'
    elif duration_value == 'AboutAMonth':
        response_text = 'I appreciate your honesty. Feelings can ebb and flow. Can you share more about the circumstances around the start of these feelings about a month ago?'
    elif duration_value == 'CoupleOfMonths':
        response_text = "Understanding the duration helps us explore your experience better. How would you describe the intensity or changes in these feelings over the past couple of months?"
    elif duration_value == 'FewDays':
        response_text = "It's okay to reflect on when these feelings started. Can you recall any specific events or situations that may have triggered or influenced your emotions a few days ago?"
    elif duration_value == 'QuiteSomeTime':
        response_text = "I hear you. Experiencing these feelings for an extended period can be challenging. Have there been any noticeable patterns or changes during the on-and-off periods over the past few weeks?"
    

    return response_text


def handle_resource_offer_intent(req):
    # Extract relevant information from the request
    resource_need = req['queryResult']['parameters']['ResourceNeed']

    # Perform custom logic based on the user's resource need
    if resource_need == 'YesPlease':
        response_text = 'Great. First, consider talking to friends or family about your feelings. Additionally, engaging in activities you enjoy and joining social groups can help alleviate loneliness. If you ever need someone to talk to, I\'m here for you. Remember, seeking professional help is always an option. Would you like more information on coping strategies?'
    elif resource_need == 'OpenToSuggestions':
        response_text = 'Thank you for being open to resources. Connecting with others is crucial. Have you considered joining local social groups or participating in activities you enjoy? I can provide more information on coping strategies if you\'re interested.'
    # Add more conditions for other resource needs

    return response_text

def handle_closure_intent(req):
    # Extract relevant information from the request
    user_response = req['queryResult']['parameters']['ClosureIntent']

    # Perform custom logic based on the user's response
    if user_response == 'ThanksForListening':
        response_text = 'You\'re welcome. I\'m here whenever you need to talk. Take care of yourself, and don\'t hesitate to reach out again. Goodbye for now!'
    elif user_response == 'FeelBetter':
        response_text = 'I\'m glad our conversation was helpful. Remember, you\'re not alone, and I\'m here whenever you need support. Take care and goodbye for now.'
    # Add more conditions based on user responses

    return response_text

if __name__ == '__main__':
    app.run(port=8080, debug=True)
