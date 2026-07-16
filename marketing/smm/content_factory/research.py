import os
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

from src.apify_client import ApifyClient
from src.tubelab_client import TubeLabClient
from src.gemini_client import GeminiClient
from src.engagement import calculate_engagement, identify_outliers
from src.report_generator import generate_report
from src.config_wizard import ensure_config

console = Console()

PLATFORMS = {
    'x': {'name': 'X/Twitter', 'scraper': 'apify'},
    'instagram': {'name': 'Instagram', 'scraper': 'apify'},
    'tiktok': {'name': 'TikTok', 'scraper': 'apify'},
    'youtube': {'name': 'YouTube', 'scraper': 'tubelab'}
}

def research_platform(platform, accounts, config):
    console.print(f"\n[bold blue]Researching {PLATFORMS[platform]['name']}...[/bold blue]")
    
    if platform == 'youtube':
        client = TubeLabClient(os.getenv('TUBELAB_API_KEY'))
        raw_data = client.fetch_outliers(
            channel_id=config['youtube_channel']['channel_id'],
            days=int(os.getenv('DAYS_TO_ANALYZE', 30))
        )
    else:
        client = ApifyClient(os.getenv('APIFY_TOKEN'))
        account_list = [acc['username'] for acc in accounts]
        raw_data = client.fetch_posts(
            platform=platform,
            accounts=account_list,
            max_posts=int(os.getenv('MAX_POSTS_PER_ACCOUNT', 50))
        )
    
    posts_with_engagement = calculate_engagement(raw_data, platform)
    outliers = identify_outliers(
        posts_with_engagement,
        threshold=float(os.getenv('OUTLIER_THRESHOLD', 2.0))
    )
    
    video_outliers = [o for o in outliers if o.get('is_video')]
    gemini = GeminiClient(os.getenv('GEMINI_API_KEY'))
    
    for outlier in video_outliers[:5]:
        if outlier.get('video_url'):
            try:
                console.print(f"  Analyzing video: {outlier.get('title', 'Untitled')}")
                analysis = gemini.analyze_video(outlier['video_url'])
                outlier['video_analysis'] = analysis
            except Exception as e:
                console.print(f"  [yellow]Warning: Could not analyze video: {e}[/yellow]")
    
    return {
        'raw': raw_data,
        'outliers': outliers,
        'video_analysis': [o for o in outliers if 'video_analysis' in o]
    }

def save_results(platform, results, output_dir):
    date_str = datetime.now().strftime('%Y-%m-%d')
    platform_dir = output_dir / platform / date_str
    platform_dir.mkdir(parents=True, exist_ok=True)
    
    with open(platform_dir / 'raw.json', 'w', encoding='utf-8') as f:
        json.dump(results['raw'], f, indent=2, ensure_ascii=False)
    
    with open(platform_dir / 'outliers.json', 'w', encoding='utf-8') as f:
        json.dump(results['outliers'], f, indent=2, ensure_ascii=False)
    
    if results['video_analysis']:
        with open(platform_dir / 'video-analysis.json', 'w', encoding='utf-8') as f:
            json.dump(results['video_analysis'], f, indent=2, ensure_ascii=False)
    
    report = generate_report(platform, results)
    with open(platform_dir / 'report.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    console.print(f"[green]✓ Results saved to {platform_dir}[/green]")

def main():
    parser = argparse.ArgumentParser(description='Research social media content')
    parser.add_argument('--platform', choices=['x', 'instagram', 'youtube', 'tiktok'],
                       help='Platform to research')
    parser.add_argument('--setup', action='store_true', help='Only run config wizard')
    args = parser.parse_args()

    if not ensure_config():
        return

    if args.setup:
        print('Конфигурация готова. Теперь запустите research.py с нужной платформой.')
        return

    if not args.platform:
        parser.error('--platform is required')
    
    with open('config/accounts.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    platform_config = {
        'x': config.get('x_accounts', []),
        'instagram': config.get('instagram_accounts', []),
        'tiktok': config.get('tiktok_accounts', []),
        'youtube': config.get('youtube_channel', {})
    }
    
    accounts = platform_config[args.platform]
    
    if not accounts:
        console.print(f"[red]Error: No accounts configured for {args.platform}[/red]")
        console.print("Edit config/accounts.json to add accounts")
        return
    
    output_dir = Path('output/research')
    
    try:
        results = research_platform(args.platform, accounts, config)
        save_results(args.platform, results, output_dir)
        
        console.print(Panel(
            f"[bold green]Research complete![/bold green]\n"
            f"Found {len(results['outliers'])} outliers\n"
            f"Analyzed {len(results['video_analysis'])} videos",
            title="Summary"
        ))
    except Exception as e:
        console.print(f"[red]Error during research: {e}[/red]")
        raise

if __name__ == '__main__':
    main()
