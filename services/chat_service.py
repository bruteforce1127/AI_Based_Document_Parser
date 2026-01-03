"""
Chat Service - Q&A with document context and conversation history
"""
import json
import config
from services import key_manager

# client = Groq(api_key=config.GROQ_API_KEY)

# In-memory store for conversation history (per document)
# In production, this should be stored in database
conversation_store = {}


def get_conversation_key(user_id, doc_id):
    """Generate unique key for user+document conversation"""
    return f"{user_id}_{doc_id}"


def get_conversation_history(user_id, doc_id):
    """Get conversation history for a specific document"""
    key = get_conversation_key(user_id, doc_id)
    return conversation_store.get(key, [])


def add_to_conversation(user_id, doc_id, role, content):
    """Add a message to conversation history"""
    key = get_conversation_key(user_id, doc_id)
    if key not in conversation_store:
        conversation_store[key] = []
    
    conversation_store[key].append({
        "role": role,
        "content": content
    })
    
    # Keep only last 20 messages to avoid token limits
    if len(conversation_store[key]) > 20:
        conversation_store[key] = conversation_store[key][-20:]


def clear_conversation(user_id, doc_id):
    """Clear conversation history for a document"""
    key = get_conversation_key(user_id, doc_id)
    if key in conversation_store:
        del conversation_store[key]


def ask_question(user_id, doc_id, document_content, document_type, question, language='English'):
    """
    Ask a question about the document with conversation context
    """
    # Get conversation history
    history = get_conversation_history(user_id, doc_id)
    
    # Build system prompt with document context
    system_prompt = f"""You are a helpful document assistant for ClarityVault. You are analyzing a {document_type} document.

DOCUMENT CONTENT:
{document_content[:15000]}

---

Your role:
1. Answer questions about this specific document accurately
2. Reference specific parts of the document when relevant
3. Provide clear, helpful explanations in {language}
4. If the user asks something not covered in the document, say so politely
5. Remember the conversation context to provide coherent follow-up answers
6. Be conversational and helpful

Always base your answers on the actual document content provided above."""

    # Build messages with conversation history
    messages = [{"role": "system", "content": system_prompt}]
    
    # Add conversation history (limit to avoid token overflow)
    for msg in history[-10:]:  # Last 10 messages
        messages.append(msg)
    
    # Add current question
    messages.append({"role": "user", "content": question})
    
    try:
        client = key_manager.get_groq_client()
        chat_completion = client.chat.completions.create(
            messages=messages,
            model=config.GROQ_MODEL,
            temperature=0.5,
            max_tokens=1500
        )
        
        answer = chat_completion.choices[0].message.content.strip()
        
        # Save to conversation history
        add_to_conversation(user_id, doc_id, "user", question)
        add_to_conversation(user_id, doc_id, "assistant", answer)
        
        return {
            "success": True,
            "answer": answer,
            "question": question
        }
    
    except Exception as e:
        print(f"Error in chat: {e}")
        return {
            "success": False,
            "error": str(e),
            "answer": "Sorry, I couldn't process your question. Please try again."
        }


def get_suggested_questions(document_type):
    """Get suggested questions based on document type"""
    suggestions = {
        "Home Loan": [
            "What is the interest rate?",
            "What are the EMI payment terms?",
            "Are there any prepayment penalties?",
            "What is the loan tenure?",
            "What happens if I miss a payment?"
        ],
        "Rent Agreement": [
            "What is the monthly rent?",
            "What is the security deposit?",
            "When does the lease end?",
            "Can I sublet this property?",
            "What are my maintenance responsibilities?"
        ],
        "Employment Contract": [
            "What is the salary mentioned?",
            "What are the working hours?",
            "What is the notice period?",
            "What benefits are included?",
            "Is there a non-compete clause?"
        ],
        "Insurance Policy": [
            "What is covered under this policy?",
            "What is the premium amount?",
            "What are the exclusions?",
            "How do I file a claim?",
            "What is the deductible?"
        ]
    }
    
    return suggestions.get(document_type, [
        "What is this document about?",
        "What are the key terms?",
        "What are my obligations?",
        "Are there any penalties mentioned?",
        "When does this expire?"
    ])
