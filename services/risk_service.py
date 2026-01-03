"""
Risk Analysis Service - Deep document risk analysis with scoring
"""
import json
import config
from services import key_manager

# client = Groq(api_key=config.GROQ_API_KEY)


def analyze_document_risks(text, document_type, target_language='English'):
    """
    Perform deep risk analysis on document
    Returns risk scores, risky clauses, and category breakdown
    """
    prompt = f"""You are a legal and financial risk analyst. Analyze this {document_type} document for risks.

DOCUMENT:
{text[:15000]}

Analyze for:
1. Risky clauses that may harm the user
2. Liability issues
3. Financial risks
4. Hidden terms or obligations
5. Termination clauses
6. Penalty clauses

Respond in {target_language} using this EXACT JSON format:
{{
    "overall_risk_score": 75,
    "risk_breakdown": {{
        "high_risk": 5,
        "medium_risk": 10,
        "low_risk": 3
    }},
    "total_clauses_analyzed": 18,
    "clauses_by_category": {{
        "Liability": 8,
        "Financial": 5,
        "Dispute": 2,
        "Termination": 3
    }},
    "risky_clauses": [
        {{
            "clause_text": "The exact text from document",
            "category": "Liability",
            "risk_level": "HIGH",
            "risk_score": 95,
            "explanation": "Why this is risky"
        }}
    ],
    "summary": "Brief overall risk summary",
    "recommendations": ["Action item 1", "Action item 2"]
}}

Identify at least 5-10 risky clauses. Score 0-100 (higher = more risky).
Respond with ONLY valid JSON:"""

    try:
        client = key_manager.get_groq_client()
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": f"You are an expert legal risk analyst. Identify risky clauses and score them. Respond in {target_language}. Return valid JSON only."
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
        
        # Ensure required fields exist
        if 'overall_risk_score' not in data:
            data['overall_risk_score'] = 50
        if 'risk_breakdown' not in data:
            data['risk_breakdown'] = {'high_risk': 0, 'medium_risk': 0, 'low_risk': 0}
        if 'risky_clauses' not in data:
            data['risky_clauses'] = []
        if 'clauses_by_category' not in data:
            data['clauses_by_category'] = {}
            
        return data
    
    except Exception as e:
        print(f"Error in risk analysis: {e}")
        return {
            "overall_risk_score": 0,
            "risk_breakdown": {"high_risk": 0, "medium_risk": 0, "low_risk": 0},
            "total_clauses_analyzed": 0,
            "clauses_by_category": {},
            "risky_clauses": [],
            "summary": "Error analyzing document risks",
            "recommendations": ["Please try again"]
        }


def get_risk_color(score):
    """Get color based on risk score"""
    if score >= 80:
        return "#ef4444"  # Red - High risk
    elif score >= 50:
        return "#f59e0b"  # Orange - Medium risk
    else:
        return "#22c55e"  # Green - Low risk


def get_risk_label(score):
    """Get risk label based on score"""
    if score >= 80:
        return "HIGH"
    elif score >= 50:
        return "MEDIUM"
    else:
        return "LOW"
