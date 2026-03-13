
import os
import re
import datetime
import shutil

# Paths
SOURCE_BASE = "/tmp/agency-agents"
TARGET_BASE = r"c:\Users\ABhati\Documents\yantrax-rl\.agent\skills\skills"
CATEGORIES = [
    "engineering", "marketing", "sales", "design", "product", 
    "project-management", "testing", "support", "spatial-computing", 
    "specialized", "strategy", "game-development", "paid-media"
]

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    text = text.strip('-')
    return f"agency-{text}"

def get_frontmatter_field(content, field):
    # Match field: value or field: "value" or field: 'value'
    pattern = rf"^{field}:\s*['\"]?(.*?)['\"]?\s*$"
    match = re.search(pattern, content, re.MULTILINE | re.IGNORECASE)
    if match:
        return match.group(1)
    return None

def process_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by --- to get frontmatter and body
    parts = content.split('---')
    if len(parts) < 3:
        return # Not a valid agent file
    
    frontmatter = parts[1]
    body = '---'.join(parts[2:]).strip()
    
    name = get_frontmatter_field(frontmatter, 'name')
    description = get_frontmatter_field(frontmatter, 'description')
    
    if not name or not description:
        return
    
    slug = slugify(name)
    target_dir = os.path.join(TARGET_BASE, slug)
    
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    
    date_str = datetime.date.today().isoformat()
    
    skill_content = f"""---
name: {slug}
description: {description}
risk: low
source: community
date_added: '{date_str}'
---

{body}
"""
    
    with open(os.path.join(target_dir, "SKILL.md"), 'w', encoding='utf-8') as f:
        f.write(skill_content)
    
    print(f"Installed: {slug}")

def main():
    count = 0
    for cat in CATEGORIES:
        cat_path = os.path.join(SOURCE_BASE, cat)
        if not os.path.exists(cat_path):
            continue
            
        for filename in os.listdir(cat_path):
            if filename.endswith(".md"):
                process_file(os.path.join(cat_path, filename))
                count += 1
    
    print(f"\nSuccessfully installed {count} agency skills.")

if __name__ == "__main__":
    main()
