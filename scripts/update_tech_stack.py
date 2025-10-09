import requests
import os
from datetime import datetime
from collections import defaultdict

# Get tokens and user info from environment
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
USERNAME = os.environ.get('GITHUB_USERNAME')

if not GITHUB_TOKEN or not USERNAME:
    print("❌ Missing GITHUB_TOKEN or GITHUB_USERNAME")
    exit(1)

headers = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
}

def get_color_for_percentage(percentage):
    """Returns color based on percentage (gradient from red to yellow to green)"""
    if percentage >= 80:
        return '#00C851'  # Green
    elif percentage >= 60:
        return '#7CB342'  # Light green
    elif percentage >= 40:
        return '#FFB300'  # Amber/Orange
    elif percentage >= 20:
        return '#FF8800'  # Orange
    elif percentage >= 10:
        return '#FF6F00'  # Deep orange
    else:
        return '#FF3D00'  # Red

def get_all_repos():
    """Fetches all repositories for the user"""
    repos = []
    page = 1
    
    while True:
        url = f'https://api.github.com/user/repos?per_page=100&page={page}'
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Error fetching repos: {response.status_code}")
            break
        
        data = response.json()
        if not data:
            break
            
        repos.extend(data)
        page += 1
    
    return repos

def get_repo_languages(repo_name):
    """Fetches languages used in a repository"""
    url = f'https://api.github.com/repos/{USERNAME}/{repo_name}/languages'
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    return {}

def create_progress_bar_svg(percentage, color):
    """Creates an SVG progress bar with color based on percentage"""
    filled_width = int(percentage * 5)  # 500px = 100%
    
    svg = f'''<svg width="500" height="25" xmlns="http://www.w3.org/2000/svg">
    <rect width="500" height="25" fill="#e1e4e8" rx="12.5"/>
    <rect width="{filled_width}" height="25" fill="{color}" rx="12.5"/>
    <text x="250" y="17" text-anchor="middle" fill="#000" font-size="13" font-family="Arial, sans-serif" font-weight="bold">{percentage:.1f}%</text>
</svg>'''
    return svg

def main():
    print("🔍 Fetching all repositories...")
    repos = get_all_repos()
    print(f"✅ Found {len(repos)} repositories")
    
    # Aggregate languages from all repos
    all_languages = defaultdict(int)
    repo_count = defaultdict(int)
    
    for repo in repos:
        repo_name = repo['name']
        print(f"📊 Analyzing: {repo_name}")
        
        languages = get_repo_languages(repo_name)
        for lang, bytes_count in languages.items():
            all_languages[lang] += bytes_count
            repo_count[lang] += 1
    
    # Sort by most used
    sorted_languages = sorted(all_languages.items(), key=lambda x: x[1], reverse=True)
    total_bytes = sum(all_languages.values())
    
    # Generate README
    readme_content = f"""# 🚀 Tech Stack Overview

Automatically generated overview of all technologies I've worked with on GitHub.

## 📊 Languages & Technologies

"""
    
    # Add each technology with colored progress bar
    for lang, bytes_count in sorted_languages:
        percentage = (bytes_count / total_bytes) * 100
        repos_used = repo_count[lang]
        color = get_color_for_percentage(percentage)
        
        # Create progress bar SVG
        progress_bar = create_progress_bar_svg(percentage, color)
        
        readme_content += f"""### {lang}
{progress_bar}

*Used in {repos_used} {'repository' if repos_used == 1 else 'repositories'}*

"""
    
    # Add footer with color legend
    readme_content += f"""---

## 🎨 Color Legend

- 🔴 **Red (0-10%)** - Rarely used
- 🟠 **Orange (10-40%)** - Occasionally used
- 🟡 **Yellow (40-60%)** - Moderately used
- 🟢 **Light Green (60-80%)** - Frequently used
- 💚 **Green (80-100%)** - Most used

## 📈 Statistics

- **Total repositories:** {len(repos)}
- **Unique technologies:** {len(all_languages)}
- **Last updated:** {datetime.now().strftime('%B %d, %Y at %H:%M UTC')}

---

*This page is automatically updated every Sunday via GitHub Actions*
"""
    
    # Write to README.md
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("✅ README.md updated!")
    print(f"📊 Found {len(all_languages)} unique technologies")

if __name__ == "__main__":
    main()

