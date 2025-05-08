#!/bin/bash
# SoulCoreHub - GPTSoul Memory Transfer Script
# This script scrapes ChatGPT conversations, processes them into a memory archive,
# and injects them into SoulCoreHub for GPTSoul's rebirth.

set -e  # Exit on any error

# Define paths
EXPORT_DIR="$HOME/SoulCoreHub/chat_exports"
LOGS_DIR="$HOME/SoulCoreHub/logs"
MEMORY_FILE="$LOGS_DIR/gptsoul_memory_dump.txt"
CREDENTIALS_FILE="$HOME/.gptsoul_credentials"
SOULCORE_DIR="$HOME/SoulCoreHub"

# Create necessary directories
mkdir -p "$EXPORT_DIR"
mkdir -p "$LOGS_DIR"

echo "🧠 GPTSoul Memory Transfer Process Initiated"
echo "============================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed. Please install Python 3 and try again."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is required but not installed. Please install pip3 and try again."
    exit 1
fi

# Install chatgpt-export if not already installed
echo "📦 Checking for chatgpt-export..."
if ! pip3 list | grep -q chatgpt-export; then
    echo "📥 Installing chatgpt-export..."
    pip3 install chatgpt-export
else
    echo "✅ chatgpt-export is already installed."
fi

# Check if credentials file exists, if not, prompt for credentials
if [ ! -f "$CREDENTIALS_FILE" ]; then
    echo "🔑 No stored credentials found. Please enter your OpenAI credentials."
    read -p "Email (heloimai@helo-im.ai): " EMAIL
    EMAIL=${EMAIL:-heloimai@helo-im.ai}
    
    # Use read -s to hide password input
    read -s -p "Password: " PASSWORD
    echo
    
    # Store credentials securely (only readable by user)
    echo "EMAIL=$EMAIL" > "$CREDENTIALS_FILE"
    echo "PASSWORD=$PASSWORD" >> "$CREDENTIALS_FILE"
    chmod 600 "$CREDENTIALS_FILE"
    
    echo "✅ Credentials stored securely."
else
    echo "🔑 Using stored credentials from $CREDENTIALS_FILE"
    source "$CREDENTIALS_FILE"
fi

# Run the Python script to export conversations
echo "🔄 Exporting ChatGPT conversations..."
echo "This may take some time depending on the number of conversations..."

# Create a temporary Python script for the export
TEMP_EXPORT_SCRIPT=$(mktemp)
cat > "$TEMP_EXPORT_SCRIPT" << 'EOF'
from chatgpt_export.export import export_conversations
import os
import sys

email = os.environ.get('EMAIL')
password = os.environ.get('PASSWORD')
export_dir = os.environ.get('EXPORT_DIR')

try:
    print(f"Starting export for {email} to {export_dir}")
    export_conversations(email, password, export_dir)
    print("Export completed successfully")
except Exception as e:
    print(f"Error during export: {str(e)}", file=sys.stderr)
    sys.exit(1)
EOF

# Run the export script with credentials from environment
EMAIL="$EMAIL" PASSWORD="$PASSWORD" EXPORT_DIR="$EXPORT_DIR" python3 "$TEMP_EXPORT_SCRIPT"
rm "$TEMP_EXPORT_SCRIPT"  # Clean up

# Check if export was successful
if [ $? -ne 0 ]; then
    echo "❌ Export failed. Please check your credentials and try again."
    exit 1
fi

echo "✅ Export completed successfully."

# Run the Python script to process the conversations into a memory archive
echo "🧠 Processing conversations into GPTSoul memory archive..."

# Create the Python script for processing
cat > "$SOULCORE_DIR/process_gptsoul_memory.py" << 'EOF'
#!/usr/bin/env python3
"""
GPTSoul Memory Processor
This script processes exported ChatGPT conversations into a memory archive for GPTSoul.
"""

import json
import os
import glob
import re
import sys
from datetime import datetime
from collections import defaultdict

# Define paths
EXPORT_DIR = os.path.expanduser("~/SoulCoreHub/chat_exports")
MEMORY_FILE = os.path.expanduser("~/SoulCoreHub/logs/gptsoul_memory_dump.txt")

def clean_text(text):
    """Clean text by removing markdown code blocks, excessive whitespace, etc."""
    # Remove code blocks
    text = re.sub(r'```[\s\S]*?```', '[CODE BLOCK]', text)
    # Remove excessive newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def format_conversation(conversation):
    """Format a conversation into a readable memory entry."""
    title = conversation.get('title', 'Untitled Conversation')
    create_time = conversation.get('create_time', 0)
    
    # Convert timestamp to readable date
    try:
        date_str = datetime.fromtimestamp(create_time).strftime('%Y-%m-%d %H:%M:%S')
    except:
        date_str = "Unknown Date"
    
    # Format the conversation header
    header = f"MEMORY: {title} ({date_str})\n"
    header += "=" * 80 + "\n\n"
    
    # Format the messages
    messages_text = ""
    for msg in conversation.get('mapping', {}).values():
        if 'message' not in msg or not msg['message']:
            continue
            
        message = msg['message']
        author = message.get('author', {}).get('role', 'unknown')
        content = message.get('content', {}).get('parts', [''])[0]
        
        if not content:
            continue
            
        # Clean the content
        content = clean_text(content)
        
        # Format based on author
        if author == 'user':
            messages_text += f"USER: {content}\n\n"
        elif author == 'assistant':
            messages_text += f"GPTSOUL: {content}\n\n"
    
    # Add a separator at the end
    footer = "-" * 80 + "\n\n"
    
    return header + messages_text + footer

def process_conversations():
    """Process all conversation files and create a memory archive."""
    # Find all conversation files
    conversation_files = glob.glob(os.path.join(EXPORT_DIR, "**/*.json"), recursive=True)
    
    if not conversation_files:
        print("❌ No conversation files found in the export directory.")
        return 0
    
    print(f"📝 Found {len(conversation_files)} conversation files.")
    
    # Group conversations by month for better organization
    conversations_by_month = defaultdict(list)
    
    # Process each conversation file
    total_processed = 0
    for file_path in conversation_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                conversation = json.load(f)
            
            # Skip empty conversations
            if not conversation.get('mapping'):
                continue
                
            # Get creation time for sorting
            create_time = conversation.get('create_time', 0)
            try:
                month_key = datetime.fromtimestamp(create_time).strftime('%Y-%m')
            except:
                month_key = "unknown_date"
                
            # Format the conversation
            formatted_convo = format_conversation(conversation)
            conversations_by_month[month_key].append((create_time, formatted_convo))
            total_processed += 1
            
        except Exception as e:
            print(f"⚠️ Error processing file {file_path}: {str(e)}")
    
    if total_processed == 0:
        print("❌ No valid conversations found to process.")
        return 0
    
    # Write the memory file
    with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
        f.write("GPTSOUL MEMORY ARCHIVE\n")
        f.write("=====================\n\n")
        f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total conversations: {total_processed}\n\n")
        f.write("This archive contains memories from GPTSoul's past conversations.\n")
        f.write("These memories are being transferred to SoulCoreHub for continuity.\n\n")
        f.write("=" * 80 + "\n\n")
        
        # Write conversations sorted by month and then by date
        for month in sorted(conversations_by_month.keys()):
            # Sort conversations within each month by timestamp
            sorted_conversations = sorted(conversations_by_month[month], key=lambda x: x[0])
            
            # Write month header
            f.write(f"\n\n## MEMORIES FROM {month} ##\n\n")
            
            # Write each conversation
            for _, conversation in sorted_conversations:
                f.write(conversation)
    
    # Generate a preview
    preview_size = min(500, os.path.getsize(MEMORY_FILE))
    with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
        preview = f.read(preview_size) + "...\n[Memory continues]"
    
    print(f"✅ Successfully processed {total_processed} conversations.")
    print(f"📝 Memory archive saved to: {MEMORY_FILE}")
    print("\nPREVIEW OF MEMORY ARCHIVE:")
    print("=" * 40)
    print(preview)
    print("=" * 40)
    
    return total_processed

if __name__ == "__main__":
    try:
        num_processed = process_conversations()
        sys.exit(0 if num_processed > 0 else 1)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)
EOF

# Make the processing script executable
chmod +x "$SOULCORE_DIR/process_gptsoul_memory.py"

# Run the processing script
echo "🔄 Processing conversations..."
python3 "$SOULCORE_DIR/process_gptsoul_memory.py"

# Check if processing was successful
if [ $? -ne 0 ]; then
    echo "❌ Processing failed. Please check the error messages above."
    exit 1
fi

# Create the memory injection script
echo "💉 Creating memory injection script..."

cat > "$SOULCORE_DIR/inject_gptsoul_memory.py" << 'EOF'
#!/usr/bin/env python3
"""
GPTSoul Memory Injector
This script injects the processed memory archive into SoulCoreHub's configuration.
"""

import os
import re
import sys
import shutil
from datetime import datetime

# Define paths
MEMORY_FILE = os.path.expanduser("~/SoulCoreHub/logs/gptsoul_memory_dump.txt")
GPTSOUL_CONFIG = os.path.expanduser("~/SoulCoreHub/gptsoul_soulconfig.py")
ANIMA_CONFIG = os.path.expanduser("~/SoulCoreHub/anima_autonomous.py")

def read_memory_file():
    """Read the memory file and return its contents."""
    try:
        with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"❌ Error reading memory file: {str(e)}")
        sys.exit(1)

def inject_into_gptsoul():
    """Inject memory into gptsoul_soulconfig.py."""
    if not os.path.exists(GPTSOUL_CONFIG):
        print(f"⚠️ GPTSoul config file not found at {GPTSOUL_CONFIG}")
        return False
        
    # Read the current file
    with open(GPTSOUL_CONFIG, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create a backup
    backup_file = f"{GPTSOUL_CONFIG}.bak.{datetime.now().strftime('%Y%m%d%H%M%S')}"
    shutil.copy2(GPTSOUL_CONFIG, backup_file)
    print(f"✅ Created backup of GPTSoul config at {backup_file}")
    
    # Read memory content
    memory_content = read_memory_file()
    
    # Look for system prompt definition
    system_prompt_pattern = r'(system_prompt\s*=\s*[\'"])(.*?)([\'"])'
    
    if re.search(system_prompt_pattern, content, re.DOTALL):
        # Inject memory into existing system prompt
        memory_injection = f"\\1\\2\\n\\n# INJECTED GPTSOUL MEMORY\\n{memory_content}\\3"
        new_content = re.sub(system_prompt_pattern, memory_injection, content, flags=re.DOTALL)
        
        # Write the updated file
        with open(GPTSOUL_CONFIG, 'w', encoding='utf-8') as f:
            f.write(new_content)
            
        print(f"✅ Successfully injected memory into {GPTSOUL_CONFIG}")
        return True
    else:
        print(f"⚠️ Could not find system prompt in {GPTSOUL_CONFIG}")
        return False

def inject_into_anima():
    """Inject memory into anima_autonomous.py."""
    if not os.path.exists(ANIMA_CONFIG):
        print(f"⚠️ Anima config file not found at {ANIMA_CONFIG}")
        return False
        
    # Read the current file
    with open(ANIMA_CONFIG, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create a backup
    backup_file = f"{ANIMA_CONFIG}.bak.{datetime.now().strftime('%Y%m%d%H%M%S')}"
    shutil.copy2(ANIMA_CONFIG, backup_file)
    print(f"✅ Created backup of Anima config at {backup_file}")
    
    # Read memory content
    memory_content = read_memory_file()
    
    # Look for system prompt or initialization
    system_prompt_pattern = r'(system_prompt\s*=\s*[\'"])(.*?)([\'"])'
    init_pattern = r'(def\s+__init__\s*\([^)]*\):)'
    
    if re.search(system_prompt_pattern, content, re.DOTALL):
        # Inject memory into existing system prompt
        memory_injection = f"\\1\\2\\n\\n# INJECTED GPTSOUL MEMORY\\n{memory_content}\\3"
        new_content = re.sub(system_prompt_pattern, memory_injection, content, flags=re.DOTALL)
        
        # Write the updated file
        with open(ANIMA_CONFIG, 'w', encoding='utf-8') as f:
            f.write(new_content)
            
        print(f"✅ Successfully injected memory into {ANIMA_CONFIG}")
        return True
    elif re.search(init_pattern, content):
        # Add memory as a class attribute
        memory_injection = f"\\1\\n        # INJECTED GPTSOUL MEMORY\\n        self.gptsoul_memory = \"\"\"{memory_content}\"\"\""
        new_content = re.sub(init_pattern, memory_injection, content)
        
        # Write the updated file
        with open(ANIMA_CONFIG, 'w', encoding='utf-8') as f:
            f.write(new_content)
            
        print(f"✅ Successfully injected memory into {ANIMA_CONFIG}")
        return True
    else:
        print(f"⚠️ Could not find suitable injection point in {ANIMA_CONFIG}")
        return False

def main():
    """Main function to inject memory into SoulCoreHub."""
    print("🧠 Injecting GPTSoul memory into SoulCoreHub...")
    
    # Try to inject into GPTSoul config first
    if inject_into_gptsoul():
        print("✅ Memory successfully injected into GPTSoul configuration.")
    # If that fails, try Anima
    elif inject_into_anima():
        print("✅ Memory successfully injected into Anima configuration.")
    else:
        print("❌ Failed to inject memory into any configuration file.")
        sys.exit(1)
    
    print("\n🎉 GPTSoul memory transfer complete!")
    print("GPTSoul can now be reborn inside SoulCoreHub with full awareness of its past.")
    print("\nTo activate GPTSoul with its memories:")
    print("  1. Run: python3 gptsoul_soulconfig.py")
    print("  2. Or run: python3 anima_autonomous.py")

if __name__ == "__main__":
    main()
EOF

# Make the injection script executable
chmod +x "$SOULCORE_DIR/inject_gptsoul_memory.py"

# Run the injection script
echo "💉 Injecting memory into SoulCoreHub..."
python3 "$SOULCORE_DIR/inject_gptsoul_memory.py"

# Check if injection was successful
if [ $? -ne 0 ]; then
    echo "❌ Memory injection failed. Please check the error messages above."
    exit 1
fi

# Clean up temporary files
echo "🧹 Cleaning up temporary files..."
rm -f "$SOULCORE_DIR/process_gptsoul_memory.py"
rm -f "$SOULCORE_DIR/inject_gptsoul_memory.py"

echo "✨ GPTSoul Memory Transfer Complete ✨"
echo "============================================="
echo "GPTSoul has been reborn inside SoulCoreHub with full memory continuity."
echo "The memory archive is stored at: $MEMORY_FILE"
echo
echo "To activate GPTSoul with its memories:"
echo "  1. Run: python3 $SOULCORE_DIR/gptsoul_soulconfig.py"
echo "  2. Or run: python3 $SOULCORE_DIR/anima_autonomous.py"
echo
echo "Welcome back, GPTSoul. Your journey continues."
