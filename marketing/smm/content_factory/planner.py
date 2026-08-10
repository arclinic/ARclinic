import os
import json
import argparse
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
from rich.console import Console
from rich.progress import Progress
from rich.panel import Panel

from research import research_platform, save_results
from src.ai_client import AIClient
from src.content_planner import generate_content_ideas, generate_playbooks
from src.config_wizard import ensure_config

console = Console()

def research_all_platforms():
    with open('config/accounts.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    platform_config = {
        'x': config.get('x_accounts', []),
        'instagram': config.get('instagram_accounts', []),
        'tiktok': config.get('tiktok_accounts', []),
        'youtube': config.get('youtube_channel', {})
    }
    
    output_dir = Path('output/research')
    all_results = {}
    
    with Progress() as progress:
        task = progress.add_task("Researching platforms...", total=4)
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {}
            
            for platform in ['x', 'instagram', 'youtube', 'tiktok']:
                accounts = platform_config[platform]
                if accounts:
                    future = executor.submit(research_platform, platform, accounts, config)
                    futures[future] = platform
            
            for future in as_completed(futures):
                platform = futures[future]
                try:
                    results = future.result()
                    all_results[platform] = results
                    save_results(platform, results, output_dir)
                    progress.advance(task)
                except Exception as e:
                    console.print(f"[red]Error researching {platform}: {e}[/red]")
                    progress.advance(task)
    
    return all_results

def generate_ai_content_plan(all_results, model='deepseek/deepseek-v4-pro'):
    console.print("\n[bold blue]Generating AI-powered content plan...[/bold blue]")
    
    kb_path = Path('knowledge_base.md')
    if not kb_path.exists():
        console.print("[yellow]Warning: knowledge_base.md not found. AI will generate generic content.[/yellow]")
        console.print("[yellow]Copy from Anna_business_26/мозг/ for personalized results.[/yellow]")
    else:
        console.print("[green]✓ Loaded knowledge_base.md[/green]")
    
    ai = AIClient(
        api_key=os.getenv('AI_API_KEY'),
        base_url=os.getenv('AI_API_BASE_URL'),
        model=model
    )
    
    outliers_by_platform = {}
    for platform, results in all_results.items():
        outliers_by_platform[platform] = results['outliers'][:10]
    
    content_ideas = generate_content_ideas(ai, outliers_by_platform)
    playbooks = generate_playbooks(ai, outliers_by_platform)
    
    return content_ideas, playbooks

def save_content_plan(content_ideas, playbooks):
    date_str = datetime.now().strftime('%Y-%m-%d')
    plan_dir = Path('output/content-plans') / date_str
    plan_dir.mkdir(parents=True, exist_ok=True)
    
    with open(plan_dir / 'content-ideas.md', 'w', encoding='utf-8') as f:
        f.write(content_ideas)
    
    for platform, playbook in playbooks.items():
        with open(plan_dir / f'{platform}-playbook.md', 'w', encoding='utf-8') as f:
            f.write(playbook)
    
    console.print(f"[green]✓ Content plan saved to {plan_dir}[/green]")
    return plan_dir

def main():
    parser = argparse.ArgumentParser(description='Generate comprehensive content plan')
    parser.add_argument('--with-ai', action='store_true', help='Use AI to generate content ideas')
    parser.add_argument('--model', choices=['deepseek', 'deepseek/deepseek-v4-pro', 'deepseek/deepseek-v4-flash'], default='deepseek/deepseek-v4-pro',
                       help='AI model to use')
    parser.add_argument('--setup', action='store_true', help='Only run config wizard')
    args = parser.parse_args()

    if not ensure_config():
        return

    if args.setup:
        print('Конфигурация готова. Теперь запустите planner.py без --setup.')
        return

    console.print(Panel(
        "[bold blue]Starting full content research...[/bold blue]\n"
        "This will research X/Twitter, Instagram, YouTube, and TikTok",
        title="Content Factory"
    ))
    
    try:
        all_results = research_all_platforms()
        
        if args.with_ai:
            content_ideas, playbooks = generate_ai_content_plan(all_results, args.model)
            plan_dir = save_content_plan(content_ideas, playbooks)
            
            console.print(Panel(
                f"[bold green]Content plan complete![/bold green]\n"
                f"Researched {len(all_results)} platforms\n"
                f"Plan saved to {plan_dir}",
                title="Summary"
            ))
        else:
            console.print("[yellow]Skipping AI content generation (use --with-ai to enable)[/yellow]")
            
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise

if __name__ == '__main__':
    main()
