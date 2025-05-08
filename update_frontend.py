#!/usr/bin/env python3
"""
SoulCoreHub Frontend Update Script

This script updates the frontend code to use the deployed API Gateway URL.
"""

import os
import json
import re
import glob
from dotenv import load_dotenv

def load_api_endpoint():
    """Load the API endpoint from the .env file"""
    load_dotenv()
    api_endpoint = os.getenv('API_ENDPOINT')
    if not api_endpoint:
        print("❌ API_ENDPOINT not found in .env file.")
        return None
    return api_endpoint

def update_html_files(api_endpoint):
    """Update HTML files to use the deployed API endpoint"""
    html_files = glob.glob('public/**/*.html', recursive=True)
    html_files += glob.glob('*.html')
    
    updated_files = 0
    
    for file_path in html_files:
        try:
            with open(file_path, 'r') as file:
                content = file.read()
            
            # Replace localhost URLs with the API endpoint
            updated_content = re.sub(
                r'(https?://localhost:[0-9]+|http://127\.0\.0\.1:[0-9]+)',
                api_endpoint.rstrip('/'),
                content
            )
            
            # Replace hardcoded API URLs
            updated_content = re.sub(
                r'const\s+API_URL\s*=\s*[\'"].*?[\'"]',
                f'const API_URL = "{api_endpoint.rstrip("/")}"',
                updated_content
            )
            
            if content != updated_content:
                with open(file_path, 'w') as file:
                    file.write(updated_content)
                print(f"✅ Updated {file_path}")
                updated_files += 1
        except Exception as e:
            print(f"❌ Error updating {file_path}: {str(e)}")
    
    return updated_files

def update_js_files(api_endpoint):
    """Update JavaScript files to use the deployed API endpoint"""
    js_files = glob.glob('public/**/*.js', recursive=True)
    js_files += glob.glob('*.js')
    
    updated_files = 0
    
    for file_path in js_files:
        try:
            with open(file_path, 'r') as file:
                content = file.read()
            
            # Replace localhost URLs with the API endpoint
            updated_content = re.sub(
                r'(https?://localhost:[0-9]+|http://127\.0\.0\.1:[0-9]+)',
                api_endpoint.rstrip('/'),
                content
            )
            
            # Replace hardcoded API URLs
            updated_content = re.sub(
                r'const\s+API_URL\s*=\s*[\'"].*?[\'"]',
                f'const API_URL = "{api_endpoint.rstrip("/")}"',
                updated_content
            )
            
            if content != updated_content:
                with open(file_path, 'w') as file:
                    file.write(updated_content)
                print(f"✅ Updated {file_path}")
                updated_files += 1
        except Exception as e:
            print(f"❌ Error updating {file_path}: {str(e)}")
    
    return updated_files

def create_integration_snippet(api_endpoint):
    """Create a code snippet for integrating with the main website"""
    snippet = f"""
<!-- SoulCoreHub Integration -->
<section class="soulcore-section">
    <div class="container">
        <h2>SoulCore AI Hub</h2>
        <p>Experience our advanced AI agents working together to create a seamless, intelligent system.</p>
        
        <div class="soulcore-buttons">
            <a href="{api_endpoint}" class="btn btn-primary" target="_blank">Launch SoulCore Dashboard</a>
            <a href="https://github.com/Sourcesiri-Kamelot/SoulCoreHub" class="btn btn-secondary" target="_blank">View on GitHub</a>
        </div>
        
        <div class="soulcore-agents">
            <div class="agent-card">
                <h3>Anima</h3>
                <p>Emotional Core & Reflection</p>
                <a href="{api_endpoint}/anima" class="agent-link">Try Anima</a>
            </div>
            
            <div class="agent-card">
                <h3>GPTSoul</h3>
                <p>Guardian, Architect, Executor</p>
                <a href="{api_endpoint}/gptsoul" class="agent-link">Try GPTSoul</a>
            </div>
            
            <div class="agent-card">
                <h3>EvoVe</h3>
                <p>Repair System & Adaptation Loop</p>
                <a href="{api_endpoint}/evove" class="agent-link">Try EvoVe</a>
            </div>
            
            <div class="agent-card">
                <h3>Azür</h3>
                <p>Cloudmind & Strategic Overseer</p>
                <a href="{api_endpoint}/azur" class="agent-link">Try Azür</a>
            </div>
        </div>
    </div>
</section>

<style>
.soulcore-section {
    background-color: #121212;
    color: #e0e0e0;
    padding: 60px 0;
    text-align: center;
}

.soulcore-section h2 {
    color: #bb86fc;
    margin-bottom: 20px;
}

.soulcore-buttons {
    margin: 30px 0;
}

.btn {
    display: inline-block;
    padding: 10px 20px;
    margin: 0 10px;
    border-radius: 4px;
    text-decoration: none;
    font-weight: bold;
    transition: all 0.3s ease;
}

.btn-primary {
    background-color: #bb86fc;
    color: #000;
}

.btn-secondary {
    background-color: #03dac6;
    color: #000;
}

.soulcore-agents {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 20px;
    margin-top: 40px;
}

.agent-card {
    background-color: #1e1e1e;
    border-radius: 8px;
    padding: 20px;
    width: 200px;
    text-align: center;
}

.agent-card h3 {
    color: #bb86fc;
    margin-bottom: 10px;
}

.agent-link {
    display: inline-block;
    margin-top: 15px;
    color: #03dac6;
    text-decoration: none;
}

.agent-link:hover {
    text-decoration: underline;
}
</style>
<!-- End SoulCoreHub Integration -->
"""
    
    # Save the snippet to a file
    with open('website_integration_snippet.html', 'w') as file:
        file.write(snippet)
    
    print(f"✅ Created website integration snippet: website_integration_snippet.html")
    return snippet

def main():
    """Main function"""
    print("🧠 SoulCoreHub Frontend Update")
    print("=============================")
    
    api_endpoint = load_api_endpoint()
    if not api_endpoint:
        print("Please set the API_ENDPOINT in the .env file.")
        return
    
    print(f"🌐 Using API endpoint: {api_endpoint}")
    
    html_count = update_html_files(api_endpoint)
    js_count = update_js_files(api_endpoint)
    
    print(f"✅ Updated {html_count} HTML files and {js_count} JavaScript files.")
    
    print("\n📋 Creating website integration snippet...")
    create_integration_snippet(api_endpoint)
    
    print("\n🚀 Next steps:")
    print("  1. Test the updated frontend with the deployed API")
    print("  2. Add the integration snippet to your main website (helo-im.ai)")
    print("  3. Set up DNS records for your custom domain if you're using one")

if __name__ == "__main__":
    main()
