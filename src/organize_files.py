import os
import shutil

def create_dirs():
    dirs = ['src', 'config', 'scripts', 'aws_tools']
    for d in dirs:
        os.makedirs(d, exist_ok=True)

def move_files():
    # Move Python files
    for f in os.listdir('.'):
        if f.endswith('.py') and f != 'organize_files.py':
            try:
                shutil.move(f, os.path.join('src', f))
                print(f'Moved {f} to src/')
            except Exception as e:
                print(f'Error moving {f}: {e}')

    # Move JSON files
    for f in os.listdir('.'):
        if f.endswith('.json'):
            try:
                shutil.move(f, os.path.join('config', f))
                print(f'Moved {f} to config/')
            except Exception as e:
                print(f'Error moving {f}: {e}')

