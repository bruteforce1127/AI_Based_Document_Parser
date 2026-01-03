"""
YouTube Service - Search for educational videos with improved accuracy
"""
import requests
import config


def build_search_query(term, category=None, context=None):
    """Build an optimized search query for better video results"""
    # Base query with the term
    query_parts = [term]
    
    # Add category-specific keywords for better relevance
    category_keywords = {
        'Legal': ['law explained', 'legal meaning', 'legal term'],
        'Financial': ['finance explained', 'financial term', 'money'],
        'Medical': ['medical term', 'health', 'medicine explained'],
        'Technical': ['technical explained', 'how it works', 'technology'],
        'Insurance': ['insurance explained', 'policy meaning'],
        'Real Estate': ['real estate', 'property', 'housing'],
        'Banking': ['banking', 'bank term', 'finance'],
        'Tax': ['tax explained', 'taxation', 'IRS']
    }
    
    # Add category-specific keyword if available
    if category and category in category_keywords:
        query_parts.append(category_keywords[category][0])
    else:
        query_parts.append('explained simply')
    
    # Add context clues
    if context:
        query_parts.append(context)
    
    return ' '.join(query_parts)


def search_videos(term, category=None, max_results=2):
    """Search YouTube for videos related to a term with improved query"""
    try:
        # Build optimized query
        query = build_search_query(term, category)
        
        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            'part': 'snippet',
            'q': query,
            'type': 'video',
            'maxResults': max_results,
            'key': config.YOUTUBE_API_KEY,
            'relevanceLanguage': 'en',
            'safeSearch': 'strict',
            'videoDuration': 'medium',  # Prefer medium length videos (4-20 min)
            'order': 'relevance'
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        videos = []
        if 'items' in data:
            for item in data['items']:
                videos.append({
                    'video_id': item['id']['videoId'],
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'][:150] + '...' if len(item['snippet']['description']) > 150 else item['snippet']['description'],
                    'thumbnail': item['snippet']['thumbnails']['medium']['url'],
                    'channel': item['snippet']['channelTitle'],
                    'url': f"https://www.youtube.com/watch?v={item['id']['videoId']}"
                })
        
        return videos
    
    except Exception as e:
        print(f"Error searching YouTube: {e}")
        return []


def search_videos_for_terms(terms_with_categories, max_per_term=2):
    """
    Search videos for multiple terms with their categories
    terms_with_categories: list of dicts with 'term' and 'category' keys
    """
    results = {}
    
    for item in terms_with_categories:
        term = item.get('term', item) if isinstance(item, dict) else item
        category = item.get('category', None) if isinstance(item, dict) else None
        
        # Try with category first
        videos = search_videos(term, category, max_per_term)
        
        # If no videos found, try with just the term
        if not videos:
            videos = search_videos(term, None, max_per_term)
        
        # Ensure at least trying a broader search if still no results
        if not videos:
            broader_query = f"{term} meaning for beginners"
            try:
                url = "https://www.googleapis.com/youtube/v3/search"
                params = {
                    'part': 'snippet',
                    'q': broader_query,
                    'type': 'video',
                    'maxResults': 1,
                    'key': config.YOUTUBE_API_KEY,
                    'safeSearch': 'strict'
                }
                response = requests.get(url, params=params)
                data = response.json()
                if 'items' in data and data['items']:
                    item = data['items'][0]
                    videos = [{
                        'video_id': item['id']['videoId'],
                        'title': item['snippet']['title'],
                        'description': item['snippet']['description'][:150] + '...',
                        'thumbnail': item['snippet']['thumbnails']['medium']['url'],
                        'channel': item['snippet']['channelTitle'],
                        'url': f"https://www.youtube.com/watch?v={item['id']['videoId']}"
                    }]
            except:
                pass
        
        if videos:
            # Ensure at least 1, at most 2 videos
            results[term] = videos[:2]
    
    return results
