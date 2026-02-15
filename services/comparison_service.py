"""
Comparison Service - Market analysis and alternatives comparison using AI
"""
from services import openai_service
import config
from services import key_manager


def analyze_document_for_comparison(text, document_type, target_language='English'):
    """
    Analyze document and find market alternatives based on document type
    """
    prompt = f"""You are a market research expert. Analyze this {document_type} document and provide:

1. KEY TERMS EXTRACTED: Extract the main terms/conditions from this document (rates, prices, conditions)
2. MARKET COMPARISON: Compare with current market standards and alternatives
3. BETTER OPTIONS: Suggest potentially better alternatives available in the market
4. RECOMMENDATIONS: Provide actionable advice

Document Type: {document_type}
Document Content:
{text[:10000]}

Respond in {target_language} using this EXACT JSON format:
{{
    "document_summary": "Brief summary of what this document offers",
    "key_terms": [
        {{"term": "Interest Rate", "value": "8.5%", "category": "Financial"}}
    ],
    "market_comparison": {{
        "current_market_average": "Description of market average for this type",
        "your_document_status": "Better/Worse/Average compared to market",
        "analysis": "Detailed comparison analysis"
    }},
    "alternatives": [
        {{
            "name": "Alternative Option Name",
            "description": "What this alternative offers",
            "potential_benefit": "Why this might be better",
            "type": "Loan/Rental/Job/Insurance/etc"
        }}
    ],
    "recommendations": [
        "Actionable recommendation 1",
        "Actionable recommendation 2"
    ],
    "risk_assessment": "Low/Medium/High",
    "overall_verdict": "Your overall assessment of this document"
}}

Respond with ONLY valid JSON:"""

    try:
        client = key_manager.get_openai_client()
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": f"You are a market research and document analysis expert. Provide helpful comparisons and alternatives in {target_language}. Always respond in valid JSON format."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model=config.OPENAI_MODEL,
            temperature=0.4,
            max_tokens=3000
        )
        
        result = chat_completion.choices[0].message.content.strip()
        
        # Clean up JSON
        if result.startswith('```'):
            result = result.split('```')[1]
            if result.startswith('json'):
                result = result[4:]
        result = result.strip()
        
        import json
        data = json.loads(result)
        return data
    
    except Exception as e:
        print(f"Error in comparison analysis: {e}")
        return {
            "document_summary": "Error analyzing document",
            "key_terms": [],
            "market_comparison": {"analysis": "Could not complete analysis"},
            "alternatives": [],
            "recommendations": ["Please try again"],
            "risk_assessment": "Unknown",
            "overall_verdict": "Analysis failed"
        }


def get_search_suggestions(document_type, key_terms):
    """
    Generate search suggestions for finding alternatives
    """
    search_queries = {
        "Home Loan": [
            "best home loan rates {year}",
            "compare mortgage rates",
            "low interest home loans"
        ],
        "Rent Agreement": [
            "apartments for rent near me",
            "rental properties comparison",
            "best rental deals"
        ],
        "Employment Contract": [
            "job opportunities {industry}",
            "salary comparison {role}",
            "better job offers"
        ],
        "Insurance Policy": [
            "compare insurance rates",
            "best insurance deals {year}",
            "insurance comparison"
        ],
        "Loan Agreement": [
            "best personal loan rates",
            "compare loan offers",
            "low interest loans"
        ]
    }
    
    # Get relevant searches or default
    suggestions = search_queries.get(document_type, [
        f"compare {document_type.lower()} offers",
        f"best {document_type.lower()} deals",
        f"alternatives to {document_type.lower()}"
    ])
    
    return suggestions
