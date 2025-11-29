class BDI2Trigger:
    def __init__(self):
        self.trigger_keywords = [
            "sad", "depressed", "hopeless", "worthless", "empty",
            "can't go on", "tired", "sleep", "appetite", "guilty",
            "failure", "cry", "irritable", "suicidal", "lonely"
        ]
        
        self.trigger_threshold = 0.3  # 30% of messages contain trigger words
        
    def should_trigger_bdi2(self, conversation_history, current_nlp_scores):
        """
        Decide when to trigger BDI-II questions
        """
        if not conversation_history:
            return False
            
        # Check NLP scores
        depression_score = current_nlp_scores.get('depression', 0)
        sentiment_score = current_nlp_scores.get('sentiment', 0)
        
        # High depression score from NLP
        if depression_score > 0.7:
            return True
            
        # Very negative sentiment
        if sentiment_score < -0.5:
            return True
        
        # Check conversation for trigger words
        recent_messages = conversation_history[-5:]  # Last 5 messages
        if len(recent_messages) == 0:
            return False
            
        trigger_word_count = 0
        
        for message in recent_messages:
            if any(keyword in message.lower() for keyword in self.trigger_keywords):
                trigger_word_count += 1
                
        trigger_ratio = trigger_word_count / len(recent_messages)
        
        # Trigger if enough messages contain depression-related keywords
        if trigger_ratio > self.trigger_threshold:
            return True
            
        return False
    
    def get_next_question(self, completed_questions):
        """
        Get the next BDI-II question to ask
        """
        from .bdi2_questions import BDI2_QUESTIONS
        
        for question_id in range(1, 22):  # 21 questions
            if question_id not in completed_questions:
                return question_id, BDI2_QUESTIONS[question_id]
                
        return None, None  # All questions completed

# Instantiate trigger system
bdi2_trigger = BDI2Trigger()