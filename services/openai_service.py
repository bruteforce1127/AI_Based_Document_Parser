"""
OpenAI Service - Handles all AI operations
"""
import config
from services import key_manager


def classify_document(text):
    """Use OpenAI to classify the document type"""
    if not text or len(text.strip()) < 10:
        return "Unreadable Document"
    
    prompt = f"""Analyze the following document text and classify it into a document type.
Your response must be ONLY the document type in 1-3 words maximum.

Examples of valid responses:
- Home Loan
- Mortgage Agreement
- Rent Agreement
- Employment Contract
- Medical Report
- Insurance Policy
- Tax Return
- Bank Statement
- Invoice
- Birth Certificate
- Passport
- Utility Bill
- Credit Card Statement
- Loan Agreement
- Property Deed

Document text:
{text[:5000]}

Document type (1-3 words only):"""

    try:
        client = key_manager.get_openai_client()
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a document classification expert. Respond with ONLY the document type in 1-3 words. No explanations, no punctuation, just the classification."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model=config.OPENAI_MODEL,
            temperature=0.1,
            max_tokens=20
        )
        
        result = chat_completion.choices[0].message.content.strip()
        result = result.replace('.', '').replace(',', '').strip()
        words = result.split()[:3]
        return ' '.join(words)
    
    except Exception as e:
        print(f"Error classifying document: {e}")
        return "Classification Error"


def translate_text(text, target_language):
    """Use OpenAI to translate text to target language"""
    if not text or len(text.strip()) < 1:
        return "No text to translate"
    
    prompt = f"""Translate the following text to {target_language}.
Provide ONLY the translation without any explanations or notes.

Text to translate:
{text}

Translation:"""

    try:
        client = key_manager.get_openai_client()
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": f"You are a professional translator. Translate the given text to {target_language} accurately. Provide only the translation without any additional explanations or notes."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model=config.OPENAI_MODEL,
            temperature=0.3,
            max_tokens=4000
        )
        
        return chat_completion.choices[0].message.content.strip()
    
    except Exception as e:
        print(f"Error translating text: {e}")
        return f"Translation Error: {str(e)}"


def translate_full_document(pages, target_language):
    """Translate entire document page by page"""
    if not pages:
        return []
    
    translated_pages = []
    
    for page in pages:
        if page['content'].strip():
            translated_content = translate_text(page['content'], target_language)
        else:
            translated_content = "(Empty page)"
        
    translated_pages.append({
            'page_number': page['page_number'],
            'original': page['content'],
            'translated': translated_content
        })
    
    return translated_pages


def analyze_difficult_terms(text, target_language='English'):
    """Identify difficult terms/jargon in document and explain them"""
    if not text or len(text.strip()) < 50:
        return []
    
    prompt = f"""Analyze the following document text and identify difficult or technical terms, legal jargon, 
complex phrases, or specialized vocabulary that a regular person might not understand.

For each term, provide:
1. The exact term or phrase from the document
2. A simple, clear explanation in {target_language}
3. The category (Legal, Financial, Technical, Medical, etc.)

Return EXACTLY in this JSON format (valid JSON array):
[
  {{"term": "example term", "explanation": "simple explanation here", "category": "Category"}},
  {{"term": "another term", "explanation": "explanation", "category": "Category"}}
]

Find 5-10 of the most important difficult terms. If the document is simple, find fewer terms.

Document text:
{text[:8000]}

Respond with ONLY the JSON array, no other text:"""

    try:
        client = key_manager.get_openai_client()
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": f"You are an expert at identifying difficult vocabulary and explaining complex terms in simple language. Always respond in valid JSON format. Explain terms in {target_language}."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model=config.OPENAI_MODEL,
            temperature=0.3,
            max_tokens=2000
        )
        
        result = chat_completion.choices[0].message.content.strip()
        
        # Clean up the response to extract JSON
        if result.startswith('```'):
            result = result.split('```')[1]
            if result.startswith('json'):
                result = result[4:]
        result = result.strip()
        
        import json
        terms = json.loads(result)
        return terms
    
    except Exception as e:
        print(f"Error analyzing terms: {e}")
        return []


def analyze_consequences(text, target_language='English'):
    """Analyze document for rules, obligations, and consequences of non-compliance"""
    if not text or len(text.strip()) < 100:
        return {'rules': [], 'consequences': [], 'summary': ''}
    
    prompt = f"""Analyze this legal/official document and identify:

1. RULES & OBLIGATIONS: What must the person do or follow according to this document?
2. CONSEQUENCES: What happens if the person fails to follow these rules or breaks the agreement?
3. PENALTIES: Any fines, legal actions, or negative outcomes mentioned

For each item provide:
- The rule/obligation or consequence
- A clear explanation in simple {target_language}
- Severity level (Low, Medium, High, Critical)

Return EXACTLY in this JSON format:
{{
    "document_type": "type of document",
    "rules": [
        {{"rule": "exact rule text", "explanation": "simple explanation", "severity": "Medium"}}
    ],
    "consequences": [
        {{"consequence": "what happens if broken", "explanation": "simple explanation", "severity": "High", "triggered_by": "which rule if violated"}}
    ],
    "summary": "Brief overall summary of the key obligations and risks in {target_language}"
}}

Document text:
{text[:10000]}

Respond with ONLY valid JSON:"""

    try:
        client = key_manager.get_openai_client()
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": f"You are a legal document analyst expert. Identify all rules, obligations, and consequences in documents. Explain everything clearly in {target_language}. Always respond in valid JSON format."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model=config.OPENAI_MODEL,
            temperature=0.2,
            max_tokens=3000
        )
        
        result = chat_completion.choices[0].message.content.strip()
        
        # Clean up JSON response
        if result.startswith('```'):
            result = result.split('```')[1]
            if result.startswith('json'):
                result = result[4:]
        result = result.strip()
        
        import json
        data = json.loads(result)
        return data
    
    except Exception as e:
        print(f"Error analyzing consequences: {e}")
        return {'rules': [], 'consequences': [], 'summary': 'Error analyzing document'}
