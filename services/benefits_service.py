"""
Benefits Analysis Service - Analyze positive aspects and benefits in documents
"""
import json
import config
from services import key_manager

# client = Groq(api_key=config.GROQ_API_KEY)


def analyze_document_benefits(text, document_type, target_language='English'):
    """
    Analyze document for positive aspects, benefits, and protections
    """
    prompt = f"""You are an expert document analyst. Analyze this {document_type} document for POSITIVE aspects that BENEFIT the user.

DOCUMENT:
{text[:15000]}

Identify:
1. User protections and rights
2. Favorable terms and conditions
3. Financial benefits (discounts, waivers, grace periods)
4. Flexibility clauses
5. Exit options and cancellation rights
6. Transparency provisions
7. Any clauses that favor the user

Respond in {target_language} using this EXACT JSON format:
{{
    "overall_benefit_score": 72,
    "benefit_breakdown": {{
        "strong_benefit": 8,
        "moderate_benefit": 5,
        "minor_benefit": 3
    }},
    "total_beneficial_clauses": 16,
    "benefits_by_category": {{
        "User Protection": 6,
        "Financial Benefits": 4,
        "Flexibility": 3,
        "Transparency": 3
    }},
    "beneficial_clauses": [
        {{
            "clause_text": "The exact text from document",
            "category": "User Protection",
            "benefit_level": "STRONG",
            "benefit_score": 85,
            "explanation": "Why this benefits the user"
        }}
    ],
    "summary": "Brief overall benefits summary",
    "strengths": ["Key strength 1", "Key strength 2"]
}}

Identify 5-10 beneficial clauses. Score 0-100 (higher = more beneficial).
Respond with ONLY valid JSON:"""

    try:
        client = key_manager.get_groq_client()
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": f"You are an expert document analyst focused on finding user benefits. Respond in {target_language}. Return valid JSON only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model=config.GROQ_MODEL,
            temperature=0.3,
            max_tokens=4000
        )
        
        result = chat_completion.choices[0].message.content.strip()
        
        # Clean JSON
        if result.startswith('```'):
            result = result.split('```')[1]
            if result.startswith('json'):
                result = result[4:]
        result = result.strip()
        
        data = json.loads(result)
        
        # Ensure required fields
        if 'overall_benefit_score' not in data:
            data['overall_benefit_score'] = 50
        if 'benefit_breakdown' not in data:
            data['benefit_breakdown'] = {'strong_benefit': 0, 'moderate_benefit': 0, 'minor_benefit': 0}
        if 'beneficial_clauses' not in data:
            data['beneficial_clauses'] = []
            
        return data
    
    except Exception as e:
        print(f"Error in benefits analysis: {e}")
        return {
            "overall_benefit_score": 0,
            "benefit_breakdown": {"strong_benefit": 0, "moderate_benefit": 0, "minor_benefit": 0},
            "total_beneficial_clauses": 0,
            "benefits_by_category": {},
            "beneficial_clauses": [],
            "summary": "Error analyzing document benefits",
            "strengths": []
        }
