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

# GitHub's official language colors
LANGUAGE_COLORS = {
    'Python': '🟦',
    'JavaScript': '🟨',
    'TypeScript': '🟦',
    'Java': '🟧',
    'C++': '🟪',
    'C': '⬜',
    'C#': '🟩',
    'Go': '🟦',
    'Rust': '🟧',
    'Ruby': '🟥',
    'PHP': '🟪',
    'Swift': '🟧',
    'Kotlin': '🟪',
    'Dart': '🟦',
    'R': '🟦',
    'Shell': '🟩',
    'HTML': '🟧',
    'CSS': '🟪',
    'SCSS': '🟪',
    'Vue': '🟩',
    'Jupyter Notebook': '🟧',
    'Lua': '🟦',
    'Perl': '🟦',
    'Scala': '🟥',
    'Haskell': '🟪',
    'Elixir': '🟪',
    'Clojure': '🟥',
    'Objective-C': '🟦',
    'Dockerfile': '🟦',
    'YAML': '🟥',
    'Markdown': '🟦',
    'JSON': '⬜',
}

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

def create_progress_bar(percentage):
    """Creates a text-based progress bar"""
    filled = int(percentage / 2)  # 50 chars = 100%
    empty = 50 - filled
    return '█' * filled + '░' * empty

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
    
    # Add each technology as a card
    for lang, bytes_count in sorted_languages:
        percentage = (bytes_count / total_bytes) * 100
        repos_used = repo_count[lang]
        emoji = LANGUAGE_COLORS.get(lang, '⚪')
        progress_bar = create_progress_bar(percentage)
        
        readme_content += f"""
<div align="center">

### {emoji} {lang}

```text
{progress_bar} {percentage:.1f}%
```

**Used in {repos_used} {'repository' if repos_used == 1 else 'repositories'}**

</div>

---

"""
    
    # Add footer
    readme_content += f"""
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
