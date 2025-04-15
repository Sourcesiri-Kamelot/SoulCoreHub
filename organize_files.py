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

    # Move shell scripts and plist
    for f in os.listdir('.'):
        if f.endswith('.sh') or f == 'soulcore.plist':
            try:
                shutil.move(f, os.path.join('scripts', f))
                print(f'Moved {f} to scripts/')
            except Exception as e:
                print(f'Error moving {f}: {e}')

    # Move AWS files
    aws_files = ['AWSCLIV2.pkg', 'awscliv2.zip', 'heloawscli']
    for f in aws_files:
        if os.path.exists(f):
            try:
                shutil.move(f, os.path.join('aws_tools', f))
                print(f'Moved {f} to aws_tools/')
            except Exception as e:
                print(f'Error moving {f}: {e}')

if __name__ == '__main__':
    create_dirs()
    move_files()
    print('\nOrganization complete!')