from .bdi2_questions import BDI2_QUESTIONS
from .bdi2_scoring import bdi2_scorer
from .bdi2_triggers import bdi2_trigger

class BDI2Manager:
    def __init__(self):
        self.user_sessions = {}  # Store user BDI-II progress
        
    def initialize_user_session(self, user_id):
        """Start new BDI-II session for user"""
        self.user_sessions[user_id] = {
            'completed_questions': set(),
            'user_responses': {},
            'in_progress': True,
            'current_question': None
        }
    
    def process_user_response(self, user_id, user_message):
        """Process user's response to BDI-II question"""
        if user_id not in self.user_sessions:
            return {"error": "No active BDI-II session"}
                
        session = self.user_sessions[user_id]
        current_q = session['current_question']
        
        #INPUT VALIDATION: Check if response is valid (0, 1, 2, 3)
        user_message_clean = user_message.strip()
        
        if user_message_clean.isdigit():
            numeric_value = int(user_message_clean)
            if numeric_value not in [0, 1, 2, 3]:
                #INVALID INPUT: Don't proceed, ask for valid input
                return {
                    "type": "bdi2_validation_error",
                    "message": "x--x Please enter only 0, 1, 2, or 3\n\n0 = Not at all\n1 = Sometimes\n2 = Often\n3 = Always",
                    "current_question": BDI2_QUESTIONS[current_q]['question'],
                    "progress": f"{len(session['completed_questions'])}/21"
                }
        
        if current_q:
            # Score the response (only if valid)
            question_data = BDI2_QUESTIONS[current_q]
            
            # Use enhanced scoring with question context
            keyword_score = bdi2_scorer.keyword_matching_score(
                user_message, question_data['keywords'], current_q
            )
            
            # Only use semantic scoring for non-numeric inputs
            if user_message.strip().isdigit():
                # For numeric inputs, trust the keyword score only
                final_score = keyword_score
            else:
                # For text inputs, use both methods
                semantic_score = bdi2_scorer.semantic_similarity_score(
                    user_message, question_data['options']
                )
                # Take the higher score (more conservative approach)
                final_score = max(keyword_score, semantic_score)
            
            # Store the response
            session['user_responses'][current_q] = final_score
            session['completed_questions'].add(current_q)
        
        # Get next question or finalize
        next_q_id, next_q_data = bdi2_trigger.get_next_question(
            session['completed_questions']
        )
        
        if next_q_id:
            session['current_question'] = next_q_id
            progress = len(session['completed_questions'])
            total = len(BDI2_QUESTIONS)
            
            return {
                "type": "bdi2_question",
                "question_id": next_q_id,
                "question": next_q_data['question'],
                "progress": f"{progress}/{total}",
                "progress_percent": int((progress / total) * 100)
            }
        else:
            # All questions completed - calculate final score
            final_result = bdi2_scorer.calculate_final_score(
                session['user_responses']
            )
            session['in_progress'] = False
            
            return {
                "type": "bdi2_completed",
                "result": final_result,
                "total_score": final_result['total_score'],
                "severity": final_result['severity'],
                "interpretation": final_result['interpretation']
            }
    
    def start_bdi2_assessment(self, user_id, conversation_history, nlp_scores):
        """Start BDI-II assessment if triggers are met"""
        if bdi2_trigger.should_trigger_bdi2(conversation_history, nlp_scores):
            self.initialize_user_session(user_id)
            next_q_id, next_q_data = bdi2_trigger.get_next_question(set())
            
            if next_q_id:
                self.user_sessions[user_id]['current_question'] = next_q_id
                
                return {
                    "should_start": True,
                    "question": next_q_data['question'],
                    "question_id": next_q_id,
                    "message": "I want to understand how you've been feeling recently. This will help me support you better."
                }
        
        return {"should_start": False}
    
    def get_user_progress(self, user_id):
        """Get current progress for a user"""
        if user_id in self.user_sessions:
            return self.user_sessions[user_id]
        return None

# Global instance
bdi2_manager = BDI2Manager()