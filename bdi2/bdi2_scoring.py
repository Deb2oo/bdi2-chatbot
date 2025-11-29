import numpy as np
from sentence_transformers import SentenceTransformer
from .bdi2_questions import get_depression_level
import re

class BDI2Scorer:
    def __init__(self):
        # Load model for semantic similarity
        self.similarity_model = SentenceTransformer('all-MiniLM-L6-v2')
        
    def keyword_matching_score(self, user_response, question_keywords, current_question_id=None):
        """
        Enhanced keyword matching with numeric input and question context
        """
        user_response_lower = user_response.lower().strip()
        
        # Handle "0" input properly
        if user_response_lower == "0":
            return 0
        
        # Handle direct numeric inputs (1, 2, 3)
        if user_response_lower.isdigit():
            numeric_score = int(user_response_lower)
            if 1 <= numeric_score <= 3:  # Changed from 0-3 to 1-3
                return numeric_score
            else:
                return 0  # Any other number gets score 0
        
        # Handle simple yes/no/scale responses
        simple_responses = {
            'not at all': 0, 'none': 0, 'never': 0, 'no': 0, 'zero': 0,
            'a little': 1, 'somewhat': 1, 'sometimes': 1, 'slightly': 1, 'mild': 1,
            'quite a bit': 2, 'often': 2, 'frequently': 2, 'much': 2, 'moderate': 2,
            'extremely': 3, 'always': 3, 'constantly': 3, 'very much': 3, 'severe': 3
        }
        
        for response_pattern, score in simple_responses.items():
            if response_pattern in user_response_lower:
                return score
        
        # Original keyword matching
        best_score = 0
        best_match = 0
        
        for score, keywords in question_keywords.items():
            match_count = 0
            for keyword in keywords:
                # Use word boundaries for exact matching
                if re.search(r'\b' + re.escape(keyword) + r'\b', user_response_lower):
                    match_count += 1
            
            if match_count > best_score:
                best_score = match_count
                best_match = score
        
        # If no good match found, try to infer from sentiment
        if best_score == 0:
            return self.infer_score_from_sentiment(user_response_lower)
                
        return best_match
    
    def infer_score_from_sentiment(self, user_response):
        """
        Infer score from general sentiment when no specific keywords match
        """
        positive_words = ['good', 'fine', 'ok', 'okay', 'alright', 'not bad', 'better', 'positive']
        negative_words = ['bad', 'terrible', 'awful', 'horrible', 'worst', 'not good', 'negative']
        intense_words = ['extremely', 'very', 'really', 'so', 'too', 'completely']
        
        response_lower = user_response.lower()
        
        # Check for intense negative
        if any(intense_word in response_lower for intense_word in intense_words) and \
           any(negative_word in response_lower for negative_word in negative_words):
            return 3
        
        # Check for moderate negative
        if any(negative_word in response_lower for negative_word in negative_words):
            return 2
        
        # Check for mild negative
        if len(response_lower) < 5 and not any(positive_word in response_lower for positive_word in positive_words):
            return 1
        
        # Default to minimal
        return 0
    
    def semantic_similarity_score(self, user_response, question_options):
        """
        Advanced scoring using semantic similarity
        """
        try:
            user_embedding = self.similarity_model.encode([user_response])
            best_score = -1
            best_option = 0
            
            for option_score, option_text in question_options.items():
                option_embedding = self.similarity_model.encode([option_text])
                similarity = np.dot(user_embedding, option_embedding.T)[0][0]
                
                if similarity > best_score:
                    best_score = similarity
                    best_option = option_score
            
            return best_option
        except Exception:
            # Fallback to keyword matching if semantic fails
            return 0
    
    def calculate_final_score(self, user_responses):
        """
        Calculate total BDI-II score from all responses
        """
        total_score = sum(user_responses.values())
        
        # Get depression level interpretation
        depression_level = get_depression_level(total_score)
        
        return {
            "total_score": total_score,
            "severity": depression_level,
            "responses": user_responses,
            "interpretation": f"BDI-II Score: {total_score}/63 - {depression_level}"
        }

# Instantiate the scorer
bdi2_scorer = BDI2Scorer()