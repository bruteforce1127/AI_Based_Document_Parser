"""
Podcast Service - Generates podcast-style audio summaries of documents
"""
from services import key_manager
import config


def generate_podcast_summary(text, target_language='English'):
    """Generate a podcast-style conversational summary of a document"""
    if not text or len(text.strip()) < 50:
        return "This document doesn't contain enough text to generate a podcast summary."

    prompt = f"""You are a friendly and engaging podcast host summarizing a legal/official document for your listeners.

Create a podcast-style summary of this document in {target_language}. Write it as if you're speaking directly to the listener, explaining the document in a conversational, easy-to-understand way.

Guidelines:
- Start with a brief introduction like "Hey everyone! Today we're breaking down an interesting document..."
- Explain the key points in simple language
- Highlight important obligations, deadlines, or risks
- Use a warm, conversational tone throughout
- End with a brief wrap-up and key takeaways
- Keep it concise but comprehensive (aim for 2-3 minutes of speaking time, roughly 400-600 words)
- Write entirely in {target_language}

Document text:
{text[:12000]}

Podcast summary in {target_language}:"""

    try:
        client = key_manager.get_openai_client()
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": f"You are an engaging podcast host who explains complex documents in simple, conversational language. Always respond in {target_language}. Be friendly, clear, and informative."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model=config.OPENAI_MODEL,
            temperature=0.7,
            max_tokens=2000
        )

        return chat_completion.choices[0].message.content.strip()

    except Exception as e:
        print(f"Error generating podcast summary: {e}")
        return f"Sorry, I couldn't generate a podcast summary right now. Error: {str(e)}"
