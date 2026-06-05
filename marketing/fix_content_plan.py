#!/usr/bin/env python3
"""Fix the truncated content plan by appending the missing parts."""

import os

# Read existing file
with open('content_plan_june_2026.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Find cut point
cut_marker = 'После пилинга мы наносим крем'
idx = content.find(cut_marker)
if idx < 0:
    print('ERROR: cut marker not found')
    print('Last 200 chars:', content[-200:])
    exit(1)

# Keep only up to cut point
content = content[:idx + len(cut_marker)]

# Read the rest from a separate file
rest_file = 'content_plan_rest.md'
if not os.path.exists(rest_file):
    print(f'ERROR: {rest_file} not found')
    exit(1)

with open(rest_file, 'r', encoding='utf-8') as f:
    rest = f.read()

# Write the fixed file
with open('content_plan_june_2026.md', 'w', encoding='utf-8') as f:
    f.write(content + rest)

print(f'Done! File size: {os.path.getsize("content_plan_june_2026.md")} bytes')
