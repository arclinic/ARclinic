from datetime import datetime
from typing import Dict

PLATFORM_NAMES = {
    'x': 'X/Twitter',
    'instagram': 'Instagram',
    'youtube': 'YouTube',
    'tiktok': 'TikTok'
}

def generate_report(platform: str, results: Dict) -> str:
    report = []
    report.append(f"# {PLATFORM_NAMES[platform]} Research Report\n")
    report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    report.append(f"\n## Summary\n")
    report.append(f"- **Total posts analyzed:** {len(results['raw'])}\n")
    report.append(f"- **Outliers found:** {len(results['outliers'])}\n")
    report.append(f"- **Videos analyzed:** {len(results['video_analysis'])}\n")
    
    if results['outliers']:
        report.append(f"\n## Top 10 Outliers\n\n")
        for i, outlier in enumerate(results['outliers'][:10], 1):
            report.append(f"### {i}. {outlier.get('title', outlier.get('text', 'Untitled'))[:80]}\n\n")
            report.append(f"**Engagement Score:** {outlier['engagement_score']:,.0f}\n\n")
            
            if platform == 'x':
                report.append(f"- Likes: {outlier.get('likes', 0):,}\n")
                report.append(f"- Retweets: {outlier.get('retweets', 0):,}\n")
                report.append(f"- Replies: {outlier.get('replies', 0):,}\n")
                report.append(f"- Bookmarks: {outlier.get('bookmarks', 0):,}\n")
            elif platform == 'instagram':
                report.append(f"- Likes: {outlier.get('likes', 0):,}\n")
                report.append(f"- Comments: {outlier.get('comments', 0):,}\n")
                report.append(f"- Views: {outlier.get('views', 0):,}\n")
            elif platform == 'tiktok':
                report.append(f"- Likes: {outlier.get('likes', 0):,}\n")
                report.append(f"- Comments: {outlier.get('comments', 0):,}\n")
                report.append(f"- Shares: {outlier.get('shares', 0):,}\n")
                report.append(f"- Views: {outlier.get('views', 0):,}\n")
            elif platform == 'youtube':
                report.append(f"- Views: {outlier.get('views', 0):,}\n")
                report.append(f"- Likes: {outlier.get('likes', 0):,}\n")
                report.append(f"- Comments: {outlier.get('comments', 0):,}\n")
            
            if outlier.get('url'):
                report.append(f"- **URL:** {outlier['url']}\n")
            
            report.append("\n")
    
    if results['video_analysis']:
        report.append(f"\n## Video Analysis\n\n")
        for i, video in enumerate(results['video_analysis'][:5], 1):
            report.append(f"### {i}. {video.get('title', 'Untitled')}\n\n")
            
            analysis = video.get('video_analysis', {})
            if analysis.get('hook'):
                report.append(f"**Hook:** {analysis['hook']}\n\n")
            if analysis.get('patterns'):
                report.append(f"**Patterns:** {analysis['patterns']}\n\n")
            if analysis.get('replicable_elements'):
                report.append(f"**Replicable Elements:** {analysis['replicable_elements']}\n\n")
            
            report.append("\n")
    
    return ''.join(report)
