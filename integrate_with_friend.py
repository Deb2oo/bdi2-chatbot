from bdi2 import bdi2_manager

# In their chatbot code:
def handle_user_message(user_id, user_message, conversation_history, nlp_scores):
    # Check if we should start BDI-II
    bdi2_result = bdi2_manager.start_bdi2_assessment(user_id, conversation_history, nlp_scores)
    
    if bdi2_result['should_start']:
        return {
            "response": bdi2_result['question'],
            "bdi2_in_progress": True
        }
    
    # Check if BDI-II is in progress
    if user_id in bdi2_manager.user_sessions and bdi2_manager.user_sessions[user_id]['in_progress']:
        bdi2_response = bdi2_manager.process_user_response(user_id, user_message)
        
        if bdi2_response['type'] == 'bdi2_question':
            return {
                "response": bdi2_response['question'],
                "bdi2_in_progress": True,
                "progress": bdi2_response['progress']
            }
        else:  # bdi2_completed
            return {
                "response": f"Assessment complete! Score: {bdi2_response['total_score']} - {bdi2_response['severity']}",
                "bdi2_completed": True,
                "bdi2_score": bdi2_response['total_score']
            }
    
    # Normal chatbot response
    return {"response": "Normal chatbot reply"}