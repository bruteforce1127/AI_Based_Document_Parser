"""
Counter-Offer Service - Generates professional negotiation letters for risky clauses
"""
import json
import config
from services import key_manager


def generate_counter_offer(clause_text, category, risk_level, explanation, document_type, target_language='English'):
    """
    Generate a professional counter-offer letter for a risky clause.
    Returns subject line, letter body, and suggested alternative clause.
    """
    # Determine the likely recipient based on document type
    recipient_map = {
        'Rental Agreement': 'Landlord/Property Manager',
        'Lease Agreement': 'Landlord/Property Manager',
        'Employment Contract': 'Employer/HR Department',
        'Loan Agreement': 'Bank/Lending Institution',
        'Insurance Policy': 'Insurance Provider',
        'Service Agreement': 'Service Provider',
        'NDA': 'Other Party',
        'Terms of Service': 'Company/Service Provider',
        'Partnership Agreement': 'Partner/Co-founder',
    }
    recipient = recipient_map.get(document_type, 'Other Party')

    prompt = f"""You are a professional legal negotiation expert. Generate a formal, polite, and professional counter-offer letter for the following risky clause found in a {document_type}.

RISKY CLAUSE: "{clause_text}"
CATEGORY: {category}
RISK LEVEL: {risk_level}
WHY IT'S RISKY: {explanation}
RECIPIENT TYPE: {recipient}

Write the response in {target_language}.

Generate a professional negotiation letter in this EXACT JSON format:
{{
    "subject": "Request for Amendment – [Category] Clause in {document_type}",
    "recipient": "{recipient}",
    "letter_body": "Dear [Recipient],\\n\\nI am writing regarding the {document_type} currently under review...\\n\\n[Professional body explaining the concern, proposed change, and reasoning]\\n\\nI look forward to your response.\\n\\nSincerely,\\n[Your Name]",  
    "suggested_alternative": "A rewritten version of the clause that is fairer and more balanced",
    "key_points": ["Point 1 about why this change is reasonable", "Point 2", "Point 3"]
}}

Rules:
- Be professional, respectful, and non-confrontational
- Reference specific legal principles or industry standards where applicable
- Propose a fair compromise, not an extreme position
- The letter should be ready to send with minimal editing
- Include placeholder [Your Name] and [Recipient] for the user to fill in
- Respond with ONLY valid JSON"""

    try:
        client = key_manager.get_openai_client()
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": f"You are an expert legal negotiation consultant. Generate professional, legally-informed counter-offer letters. Respond in {target_language}. Return valid JSON only."
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

        # Clean JSON
        if result.startswith('```'):
            result = result.split('```')[1]
            if result.startswith('json'):
                result = result[4:]
        result = result.strip()

        data = json.loads(result)

        # Ensure required fields
        if 'subject' not in data:
            data['subject'] = f'Request for Amendment – {category} Clause'
        if 'letter_body' not in data:
            data['letter_body'] = 'Error generating letter body.'
        if 'suggested_alternative' not in data:
            data['suggested_alternative'] = ''
        if 'key_points' not in data:
            data['key_points'] = []

        return data

    except Exception as e:
        print(f"Error generating counter-offer: {e}")
        return {
            "subject": f"Request for Amendment – {category} Clause",
            "letter_body": "We were unable to generate the letter at this time. Please try again.",
            "suggested_alternative": "",
            "key_points": [],
            "error": str(e)
        }
