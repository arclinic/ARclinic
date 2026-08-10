# Content Factory - SMM Agent

AI-powered social media content research and planning agent, compatible with DeepSeek V4 Pro (via Promptra) and Qwen 3.7 Max.

Based on [head-of-content](https://github.com/bradautomates/head-of-content) logic, but model-agnostic.

## Features

- Research high-performing content across X/Twitter, Instagram, YouTube, TikTok
- Identify viral content using engagement scoring algorithms
- Analyze videos with AI to extract hooks and patterns
- Generate cross-platform content plans
- Create platform-specific playbooks

## Requirements

- Python 3.8+
- Apify API token (for X/Instagram/TikTok scraping)
- TubeLab API key (for YouTube outlier detection)
- Google Gemini API key (for video analysis)
- DeepSeek V4 Pro API access (via Promptra — регистрация на promptra.ru)

## Setup

1. Clone and install dependencies:
```bash
pip install -r requirements.txt
```

2. Copy environment template:
```bash
cp .env.example .env
```

3. Edit `.env` with your API keys

4. Configure target accounts in `config/accounts.json`

## Usage

```bash
# Run individual platform research
python research.py --platform x
python research.py --platform instagram
python research.py --platform youtube
python research.py --platform tiktok

# Run full content planning (all platforms)
python planner.py

# Generate content plan with AI (DeepSeek V4 Pro via Promptra)
python planner.py --with-ai --model deepseek
```

## Output Structure

```
output/
├── research/
│   ├── x/2024-01-15/
│   │   ├── raw.json
│   │   ├── outliers.json
│   │   └── report.md
│   ├── instagram/...
│   ├── youtube/...
│   └── tiktok/...
└── content-plans/
    └── 2024-01-15/
        ├── content-ideas.md
        ├── x-playbook.md
        ├── instagram-playbook.md
        ├── youtube-playbook.md
        └── tiktok-playbook.md
```

## Engagement Scoring

### X/Twitter
- Bookmarks: 4x
- Replies: 3x
- Retweets: 2x
- Quotes: 2x
- Likes: 1x

### Instagram
`engagement = likes + (3 × comments) + (0.1 × views)`

### TikTok
`engagement = likes + (3 × comments) + (2 × shares) + (2 × saves) + (0.05 × views)`

### YouTube
`score = zScore × recency_boost (5% daily decay)`

**Outlier threshold:** Content scoring above `mean + (2.0 × std_dev)`

## License

MIT
