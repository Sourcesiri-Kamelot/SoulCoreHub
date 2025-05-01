# modules/secure_storage.py
"""
Secure Storage Module
-------------------
Provides encryption and secure storage for logs and backups.
"""

import logging
import os
import time
import json
import base64
import hashlib
import zipfile
import shutil
import threading
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logger = logging.getLogger("EvoVe.SecureStorage")

class SecureStorage:
    """Provides encryption and secure storage for logs and backups."""
    
    def __init__(self, evove):
        """Initialize the secure storage module."""
        self.evove = evove
        self.config = evove.config.get("secure_storage", {})
        self.encryption_key = self._get_encryption_key()
        self.backup_dir = self.config.get("backup_dir", "backups")
        self.log_dir = self.config.get("log_dir", "logs")
        self.max_log_size = self.config.get("max_log_size", 10 * 1024 * 1024)  # 10 MB
        self.max_log_age = self.config.get("max_log_age", 30)  # 30 days
        self.backup_schedule = self.config.get("backup_schedule", "daily")
        self.s3_bucket = self.config.get("s3_bucket")
        self.s3_prefix = self.config.get("s3_prefix", "evove-backups")
        self.running = False
        self.scheduler_thread = None
        
    def start(self):
        """Start the secure storage module."""
        if self.running:
            logger.warning("Secure storage is already running")
            return
            
        self.running = True
        logger.info("Starting secure storage")
        
        # Create directories if they don't exist
        os.makedirs(self.backup_dir, exist_ok=True)
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Start scheduler thread
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()
        
    def stop(self):
        """Stop the secure storage module."""
        if not self.running:
            logger.warning("Secure storage is not running")
            return
            
        self.running = False
        logger.info("Stopping secure storage")
        
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
    
    def _scheduler_loop(self):
        """Main scheduler loop."""
        last_daily = None
        last_weekly = None
        last_monthly = None
        last_rotation = None
        
        while self.running:
            try:
                now = datetime.now()
                
                # Check for log rotation
                if not last_rotation or (now - last_rotation).total_seconds() >= 3600:  # Every hour
                    self._rotate_logs()
                    last_rotation = now
                
                # Check for backups
                if self.backup_schedule == "daily" and (not last_daily or now.day != last_daily.day):
                    self._create_scheduled_backup("daily")
                    last_daily = now
                    
                elif self.backup_schedule == "weekly" and (not last_weekly or (now - last_weekly).days >= 7):
                    self._create_scheduled_backup("weekly")
                    last_weekly = now
                    
                elif self.backup_schedule == "monthly" and (not last_monthly or now.month != last_monthly.month):
                    self._create_scheduled_backup("monthly")
                    last_monthly = now
                
                # Sleep for a while
                time.sleep(60)
                
            except Exception as e:
                logger.error(f"Error in secure storage scheduler: {e}")
                time.sleep(300)  # Sleep for 5 minutes on error
    
    def _get_encryption_key(self):
        """Get or generate the encryption key."""
        key_file = self.config.get("key_file", "data/encryption.key")
        password = self.config.get("password", os.environ.get("EVOVE_ENCRYPTION_PASSWORD"))
        
        if not password:
            logger.warning("No encryption password provided, generating a random one")
            password = base64.urlsafe_b64encode(os.urandom(32)).decode()
        
        # Derive a key from the password
        salt = b'EvoVe_Salt_123'  # In production, use a secure, unique salt
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        
        # Save the key if configured
        if key_file:
            os.makedirs(os.path.dirname(key_file), exist_ok=True)
            if not os.path.exists(key_file):
                with open(key_file, 'wb') as f:
                    f.write(key)
                os.chmod(key_file, 0o600)  # Restrict permissions
        
        return key
    
    def encrypt_file(self, input_file, output_file=None):
        """Encrypt a file."""
        if not output_file:
            output_file = input_file + '.enc'
            
        try:
            cipher = Fernet(self.encryption_key)
            
            with open(input_file, 'rb') as f:
                data = f.read()
                
            encrypted_data = cipher.encrypt(data)
            
            with open(output_file, 'wb') as f:
                f.write(encrypted_data)
                
            logger.debug(f"Encrypted {input_file} to {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Failed to encrypt file {input_file}: {e}")
            return None
    
    def decrypt_file(self, input_file, output_file=None):
        """Decrypt a file."""
        if not output_file:
            output_file = input_file.replace('.enc', '') if input_file.endswith('.enc') else input_file + '.dec'
            
        try:
            cipher = Fernet(self.encryption_key)
            
            with open(input_file, 'rb') as f:
                encrypted_data = f.read()
                
            decrypted_data = cipher.decrypt(encrypted_data)
            
            with open(output_file, 'wb') as f:
                f.write(decrypted_data)
                
            logger.debug(f"Decrypted {input_file} to {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Failed to decrypt file {input_file}: {e}")
            return None
    
    def create_encrypted_backup(self, name=None):
        """Create an encrypted backup of the system."""
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        if not name:
            name = f"backup-{timestamp}"
            
        backup_file = os.path.join(self.backup_dir, f"{name}.zip")
        encrypted_file = backup_file + '.enc'
        
        try:
            logger.info(f"Creating encrypted backup: {name}")
            
            # Create a temporary directory for the backup
            temp_dir = os.path.join(self.backup_dir, "temp")
            os.makedirs(temp_dir, exist_ok=True)
            
            # Create the backup zip file
            with zipfile.ZipFile(backup_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add key files and directories
                dirs_to_backup = ['mcp', 'config', 'modules', 'scripts']
                files_to_backup = [
                    'evove_autonomous.py',
                    'mcp_main.py', 
                    'mcp_client_soul.py',
                    'anima_voice.py'
                ]
                
                # Add directories
                for dir_name in dirs_to_backup:
                    if os.path.exists(dir_name):
                        for root, _, files in os.walk(dir_name):
                            for file in files:
                                if not file.endswith('.pyc') and not file.endswith('.enc'):
                                    file_path = os.path.join(root, file)
                                    zipf.write(file_path)
                
                # Add individual files
                for file_name in files_to_backup:
                    if os.path.exists(file_name):
                        zipf.write(file_name)
                        
                # Add metadata
                metadata = {
                    "created_at": timestamp,
                    "created_by": "EvoVe",
                    "version": self.evove.config.get("version", "1.0.0"),
                    "description": f"Encrypted backup created on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                }
                
                with open(os.path.join(temp_dir, "metadata.json"), 'w') as f:
                    json.dump(metadata, f, indent=2)
                    
                zipf.write(os.path.join(temp_dir, "metadata.json"), "metadata.json")
            
            # Encrypt the backup
            self.encrypt_file(backup_file, encrypted_file)
            
            # Remove the unencrypted backup
            os.remove(backup_file)
            
            # Clean up
            shutil.rmtree(temp_dir, ignore_errors=True)
            
            logger.info(f"Encrypted backup created: {encrypted_file}")
            
            # Upload to S3 if configured
            if self.s3_bucket:
                self._upload_to_s3(encrypted_file)
                
            return encrypted_file
            
        except Exception as e:
            logger.error(f"Failed to create encrypted backup: {e}")
            return None
    
    def _create_scheduled_backup(self, schedule_type):
        """Create a scheduled backup."""
        name = f"{schedule_type}-{datetime.now().strftime('%Y%m%d')}"
        return self.create_encrypted_backup(name)
    
    def _rotate_logs(self):
        """Rotate and encrypt logs."""
        logger.debug("Rotating logs")
        
        try:
            # Check all log files
            for root, _, files in os.walk(self.log_dir):
                for file in files:
                    if file.endswith('.log') and not file.endswith('.enc'):
                        file_path = os.path.join(root, file)
                        
                        # Check file size
                        if os.path.getsize(file_path) > self.max_log_size:
                            self._archive_log(file_path)
                            
            # Check for old log archives
            now = datetime.now()
            for file in os.listdir(self.log_dir):
                if file.endswith('.log.enc'):
                    file_path = os.path.join(self.log_dir, file)
                    
                    # Extract timestamp from filename
                    try:
                        timestamp_str = file.split('-')[1].split('.')[0]
                        timestamp = datetime.strptime(timestamp_str, '%Y%m%d%H%M%S')
                        
                        # Check if the log is too old
                        if (now - timestamp).days > self.max_log_age:
                            logger.debug(f"Removing old log archive: {file}")
                            os.remove(file_path)
                    except (IndexError, ValueError):
                        continue
                        
        except Exception as e:
            logger.error(f"Error rotating logs: {e}")
    
    def _archive_log(self, log_file):
        """Archive and encrypt a log file."""
        try:
            # Create archive name
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            base_name = os.path.basename(log_file)
            archive_name = f"{base_name.split('.')[0]}-{timestamp}.log"
            archive_path = os.path.join(self.log_dir, archive_name)
            
            # Copy the log file
            shutil.copy2(log_file, archive_path)
            
            # Encrypt the archive
            encrypted_path = self.encrypt_file(archive_path)
            
            # Remove the unencrypted archive
            if encrypted_path:
                os.remove(archive_path)
            
            # Truncate the original log file
            with open(log_file, 'w') as f:
                f.write(f"Log rotated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                
            logger.debug(f"Archived log file: {log_file} -> {encrypted_path}")
            
        except Exception as e:
            logger.error(f"Failed to archive log file {log_file}: {e}")
    
    def _upload_to_s3(self, file_path):
        """Upload a file to S3."""
        if not self.s3_bucket:
            return False
            
        try:
            import boto3
            s3 = boto3.client('s3')
            
            file_name = os.path.basename(file_path)
            s3_key = f"{self.s3_prefix}/{file_name}"
            
            logger.info(f"Uploading {file_path} to S3 bucket {self.s3_bucket}")
            s3.upload_file(file_path, self.s3_bucket, s3_key)
            
            logger.info(f"Upload complete: s3://{self.s3_bucket}/{s3_key}")
            return True
            
        except ImportError:
            logger.error("boto3 not installed, cannot upload to S3")
            return False
        except Exception as e:
            logger.error(f"Failed to upload to S3: {e}")
            return False

