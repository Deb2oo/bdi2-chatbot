from flask import Flask, render_template, request, jsonify, session
from bdi2 import bdi2_manager
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'bdi2-test-secret-key'

# Store conversations in memory (for testing)
conversations = {}

def get_nlp_scores(message):
    """Mock NLP analysis - replace with your teammate's real NLP"""
    message_lower = message.lower()
    
    depression_keywords = ['sad', 'depressed', 'hopeless', 'worthless', 'tired', 'can\'t sleep', 'no energy']
    sentiment = -0.8 if any(word in message_lower for word in depression_keywords) else 0.1
    
    return {
        'sentiment': sentiment,
        'depression': 0.9 if any(word in message_lower for word in depression_keywords) else 0.1,
        'emotions': {
            'sadness': 0.8 if any(word in message_lower for word in ['sad', 'depressed']) else 0.1,
            'fear': 0.1,
            'anger': 0.1
        }
    }

@app.route('/')
def home():
    return render_template('chat.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_id = data.get('user_id', 'test_user')
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({"error": "No message provided"}), 400
        
        # Initialize user conversation if not exists
        if user_id not in conversations:
            conversations[user_id] = []
        
        # Add user message to conversation
        conversations[user_id].append({
            'role': 'user',
            'message': user_message,
            'timestamp': datetime.now().isoformat()
        })
        
        # Get NLP scores (mock)
        nlp_scores = get_nlp_scores(user_message)
        
        # Get conversation history
        conversation_history = [msg['message'] for msg in conversations[user_id] if msg['role'] == 'user']
        
        response_data = {
            "response": "",
            "bdi2_in_progress": False,
            "bdi2_completed": False,
            "progress": None
        }
        
        # Check for ongoing BDI-II session FIRST
        if (user_id in bdi2_manager.user_sessions and 
            bdi2_manager.user_sessions[user_id]['in_progress']):
            
            bdi2_result = bdi2_manager.process_user_response(user_id, user_message)
            
            if bdi2_result['type'] == 'bdi2_question':
                response_data["response"] = bdi2_result['question']
                response_data["bdi2_in_progress"] = True
                response_data["progress"] = bdi2_result['progress']
                response_data["progress_percent"] = bdi2_result.get('progress_percent', 0)
                
            elif bdi2_result['type'] == 'bdi2_validation_error':
                #Handle validation errors
                response_data["response"] = f"❌ {bdi2_result['message']}\n\n{bdi2_result['current_question']}"
                response_data["bdi2_in_progress"] = True
                response_data["progress"] = bdi2_result['progress']
                
            elif bdi2_result['type'] == 'bdi2_completed':
                response_data["response"] = (
                    f"🎉 **Assessment Complete!**\n\n"
                    f"**BDI-II Score:** {bdi2_result['total_score']}/63\n"
                    f"**Severity:** {bdi2_result['severity']}\n"
                    f"**Interpretation:** {bdi2_result['interpretation']}\n\n"
                    f"Thank you for completing the assessment. I'm here to support you."
                )
                response_data["bdi2_completed"] = True
                response_data["bdi2_score"] = bdi2_result['total_score']
                response_data["severity"] = bdi2_result['severity']
        
        # Check if we should start NEW BDI-II (only if no active session)
        else:
            bdi2_check = bdi2_manager.start_bdi2_assessment(user_id, conversation_history, nlp_scores)
            
            if bdi2_check['should_start']:
                response_data["response"] = f" {bdi2_check['message']}\n\n{bdi2_check['question']}"
                response_data["bdi2_in_progress"] = True
                response_data["progress"] = "0/21"
                response_data["progress_percent"] = 0
        
        # Normal chatbot response (if no BDI-II activity)
        if not response_data["response"]:
            if any(word in user_message.lower() for word in ['hello', 'hi', 'hey']):
                response_data["response"] = "Hello! I'm here to listen and support you. How are you feeling today?"
            elif any(word in user_message.lower() for word in ['help', 'support']):
                response_data["response"] = "I'm here to help you. You can share your feelings with me, and I'll listen without judgment."
            else:
                response_data["response"] = "Thank you for sharing. I'm listening and here to support you."
        
        # Add bot response to conversation
        conversations[user_id].append({
            'role': 'bot',
            'message': response_data["response"],
            'timestamp': datetime.now().isoformat(),
            'bdi2_in_progress': response_data.get('bdi2_in_progress', False)
        })
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/reset', methods=['POST'])
def reset():
    """Reset conversation and BDI-II session"""
    data = request.json
    user_id = data.get('user_id', 'test_user')
    
    if user_id in conversations:
        del conversations[user_id]
    if user_id in bdi2_manager.user_sessions:
        del bdi2_manager.user_sessions[user_id]
    
    return jsonify({"message": "Conversation reset successfully"})

@app.route('/status')
def status():
    """Get server status"""
    return jsonify({
        "status": "running",
        "active_users": len(conversations),
        "bdi2_sessions": len(bdi2_manager.user_sessions)
    })

# For production deployment
import os
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)