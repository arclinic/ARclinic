import numpy as np
from typing import List, Dict

def calculate_engagement(posts: List[Dict], platform: str) -> List[Dict]:
    for post in posts:
        if platform == 'x':
            post['engagement_score'] = (
                post.get('bookmarks', 0) * 4 +
                post.get('replies', 0) * 3 +
                post.get('retweets', 0) * 2 +
                post.get('quotes', 0) * 2 +
                post.get('likes', 0) * 1
            )
        elif platform == 'instagram':
            post['engagement_score'] = (
                post.get('likes', 0) +
                post.get('comments', 0) * 3 +
                post.get('views', 0) * 0.1
            )
        elif platform == 'tiktok':
            post['engagement_score'] = (
                post.get('likes', 0) +
                post.get('comments', 0) * 3 +
                post.get('shares', 0) * 2 +
                post.get('saves', 0) * 2 +
                post.get('views', 0) * 0.05
            )
        elif platform == 'youtube':
            post['engagement_score'] = post.get('score', 0)
    
    return posts

def identify_outliers(posts: List[Dict], threshold: float = 2.0) -> List[Dict]:
    if not posts:
        return []
    
    scores = [p['engagement_score'] for p in posts]
    mean = np.mean(scores)
    std = np.std(scores)
    
    cutoff = mean + (threshold * std)
    
    outliers = [p for p in posts if p['engagement_score'] > cutoff]
    outliers.sort(key=lambda x: x['engagement_score'], reverse=True)
    
    return outliers
