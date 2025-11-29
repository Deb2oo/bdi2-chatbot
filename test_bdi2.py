from bdi2 import bdi2_manager

def test_bdi2_system():
    print("🧪 Testing BDI-II System...")
    
    user_id = "test_user_123"
    
    # Test 1: Check if BDI-II triggers with depressive conversation
    print("\n1. Testing BDI-II Trigger...")
    test_conversation = [
        "I've been feeling really sad lately",
        "Everything seems hopeless",
        "I don't see the point anymore"
    ]
    
    test_nlp_scores = {
        'depression': 0.8,
        'sentiment': -0.7,
        'emotions': {'sadness': 0.9, 'fear': 0.2, 'anger': 0.1}
    }
    
    # Check if should trigger BDI-II
    result = bdi2_manager.start_bdi2_assessment(
        user_id, test_conversation, test_nlp_scores
    )
    
    if result['should_start']:
        print("✅ BDI-II triggered successfully!")
        print(f"First question: {result['question']}")
        
        # Test 2: Process user responses
        print("\n2. Testing Response Processing...")
        test_responses = [
            "I feel sad all the time",  # Should score high for sadness
            "I'm worried about my future",  # Medium score
            "I feel like a complete failure"  # High score
        ]
        
        for i, response in enumerate(test_responses):
            print(f"\nResponse {i+1}: '{response}'")
            bdi2_result = bdi2_manager.process_user_response(user_id, response)
            
            if bdi2_result['type'] == 'bdi2_question':
                print(f"Next question: {bdi2_result['question']}")
                print(f"Progress: {bdi2_result['progress']}")
            elif bdi2_result['type'] == 'bdi2_completed':
                print("🎉 BDI-II Assessment Completed!")
                print(f"Final score: {bdi2_result['total_score']}/63")
                print(f"Severity: {bdi2_result['severity']}")
                print(f"Interpretation: {bdi2_result['interpretation']}")
                break
    else:
        print("❌ BDI-II didn't trigger (this might be expected for normal conversation)")
    
    # Test 3: Check user progress
    print("\n3. Testing User Progress...")
    progress = bdi2_manager.get_user_progress(user_id)
    if progress:
        print(f"User session: {progress}")
    else:
        print("No active user session")

if __name__ == "__main__":
    test_bdi2_system()