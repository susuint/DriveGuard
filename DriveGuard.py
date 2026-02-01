# -*- coding: utf-8 -*-
"""
================================================================================
    GOOGLE DRIVE BACKUP TOOL v1.9.1 - AUTO RESUME OPTIMIZED
    Optimized for Manual Resume - Stop runtime and restart the next day
================================================================================

VERSION: 1.9.1 FINAL
DATE: February 02, 2026

RECOMMENDED WORKFLOW:
1. Run backup normally
2. If rate limit occurs → STOP RUNTIME IMMEDIATELY (Runtime → Disconnect and delete runtime)
3. Wait 24 hours
4. Restart notebook → Program AUTO-RESUMES

NEW FEATURES v1.9.1:
✅ Auto-detect resume mode (no manual selection needed)
✅ Clear notifications when to stop runtime
✅ Checkpoint after each successful file
✅ Smart resume - automatic state detection
✅ Recommends STOPPING RUNTIME instead of waiting

================================================================================
"""

# ============================================================
# STEP 1: INSTALL LIBRARIES
# ============================================================

print("📦 Installing required libraries...")
import subprocess
import sys

packages = [
    'google-auth',
    'google-auth-oauthlib', 
    'google-auth-httplib2',
    'google-api-python-client',
    'tqdm',
    'requests',
    'psutil'
]

for package in packages:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-q', package])

print("✅ Library installation completed!\n")


# ============================================================
# STEP 2: IMPORT LIBRARIES
# ============================================================

import os
import json
import hashlib
import time
from datetime import datetime, timedelta
from pathlib import Path
import io
import logging
import gc
from threading import Lock
import concurrent.futures
import multiprocessing

# Google Drive API
from google.colab import auth
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from googleapiclient.errors import HttpError
from google.auth import default

# Progress bar
from tqdm.notebook import tqdm

# System monitoring
import psutil

# Disable warnings
logging.getLogger('google_auth_httplib2').setLevel(logging.ERROR)


# ============================================================
# ⚙️  STEP 3: MAIN CONFIGURATION - EDIT HERE
# ============================================================

# 📁 FOLDER IDs (REQUIRED TO CHANGE)
# Instructions: Right-click on folder → Share → Copy link
# Link format: https://drive.google.com/drive/folders/ABC123XYZ
# Use the ABC123XYZ part as FOLDER_ID

SOURCE_FOLDER_ID = '1ABCdefGHIjklMNOpqrSTUvwxYZ123456'  # ⚠️ CHANGE: Source folder to backup
BACKUP_PARENT_ID = '1XYZabcDEFghiJKLmnoPQRstUVWxyz789'  # ⚠️ CHANGE: Destination folder for backups

# 🏷️  Folder suffix
FOLDER_SUFFIX = '_BACKUP'

# 🚀 Parallel processing workers
MAX_WORKERS = None  # Auto-detect (recommended)

# 🛡️  Rate Limit Protection
MAX_CONSECUTIVE_RATE_LIMIT_ERRORS = 3   # Stop after 3 consecutive errors
RATE_LIMIT_COOLDOWN_HOURS = 24          # 24-hour cooldown

# 📝 Storage files
LOG_FILE = 'backup_log.json'
STATE_FILE = 'backup_state.json'

# 🎯 MANUAL RESUME MODE (Default)
# True = Recommend STOPPING RUNTIME when rate limit hits (RECOMMENDED)
# False = Auto retry (not recommended)
MANUAL_RESUME_MODE = True

print("="*80)
print("⚙️  SYSTEM CONFIGURATION:")
print("="*80)
print(f"📁 Source Folder: {SOURCE_FOLDER_ID}")
print(f"📁 Backup Parent: {BACKUP_PARENT_ID}")
print(f"🎯 Resume Mode: {'MANUAL (Recommended)' if MANUAL_RESUME_MODE else 'AUTO'}")
print("="*80 + "\n")


# ============================================================
# STEP 4: GOOGLE DRIVE AUTHENTICATION
# ============================================================

print("🔐 Authenticating with Google Drive...")
auth.authenticate_user()
creds, _ = default()
drive_service = build('drive', 'v3', credentials=creds)
print("✅ Authentication successful!\n")


# ============================================================
# STEP 5: CLASS DEFINITIONS
# ============================================================

class BackupState:
    """Manage backup state with optimized manual resume"""
    
    def __init__(self, state_file='backup_state.json'):
        self.state_file = state_file
        self.state = self.load_state()
    
    def load_state(self):
        """Load state from file"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                    print(f"📂 Loaded state from {self.state_file}")
                    return state
            except:
                print(f"⚠️  Cannot load state, creating new...")
        
        return {
            'status': 'new',
            'current_folder': None,
            'pending_files': [],
            'failed_files': [],
            'consecutive_rate_limit_errors': 0,
            'last_rate_limit_time': None,
            'backup_folder_id': None,
            'total_files_processed': 0,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
    
    def save_state(self):
        """Save state - Checkpoint after each change"""
        self.state['updated_at'] = datetime.now().isoformat()
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)
    
    def update(self, **kwargs):
        """Update and save immediately"""
        self.state.update(kwargs)
        self.save_state()
    
    def can_resume(self):
        """Check if resume is possible"""
        if self.state['last_rate_limit_time']:
            try:
                last_error = datetime.fromisoformat(self.state['last_rate_limit_time'])
                now = datetime.now()
                hours_passed = (now - last_error).total_seconds() / 3600
                
                if hours_passed < RATE_LIMIT_COOLDOWN_HOURS:
                    remaining = RATE_LIMIT_COOLDOWN_HOURS - hours_passed
                    next_time = last_error + timedelta(hours=RATE_LIMIT_COOLDOWN_HOURS)
                    
                    print(f"\n⏰ NEED TO WAIT {remaining:.1f} MORE HOURS")
                    print(f"🕐 Try again after: {next_time.strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"💡 Recommendation: Wait full time then restart notebook\n")
                    return False
            except:
                pass
        
        return True
    
    def reset_rate_limit_counter(self):
        """Reset rate limit counter"""
        self.state['consecutive_rate_limit_errors'] = 0
        self.save_state()
    
    def increment_rate_limit_error(self):
        """Increment rate limit error counter"""
        self.state['consecutive_rate_limit_errors'] += 1
        self.state['last_rate_limit_time'] = datetime.now().isoformat()
        self.save_state()
        return self.state['consecutive_rate_limit_errors']
    
    def should_auto_resume(self):
        """Check if auto-resume should occur"""
        # If status = paused and 24h has passed
        if self.state['status'] == 'paused':
            if self.can_resume():
                return True
        return False


class DriveBackupManager:
    """Backup Manager optimized for manual resume"""
    
    def __init__(self, service, log_file='backup_log.json', state_file='backup_state.json', 
                 max_workers=None, manual_mode=True):
        self.service = service
        self.log_file = log_file
        self.backup_log = self.load_log()
        self.backup_state = BackupState(state_file)
        self.local_temp_dir = '/content/temp_backup'
        os.makedirs(self.local_temp_dir, exist_ok=True)
        self.manual_mode = manual_mode
        
        if max_workers is None:
            self.max_workers = self._auto_detect_workers()
        else:
            self.max_workers = max_workers
        
        self.log_lock = Lock()
        self.state_lock = Lock()
        self.should_stop = False
        self.download_stats = {'success': 0, 'failed': 0, 'skipped': 0}
        self.upload_stats = {'success': 0, 'failed': 0}
    
    def _auto_detect_workers(self):
        """Auto-detect optimal worker count"""
        cpu_count = multiprocessing.cpu_count()
        available_memory_gb = psutil.virtual_memory().available / (1024**3)
        
        # Optimal formula: min(CPU cores, available_memory_GB / 2, 8)
        optimal_workers = min(cpu_count, int(available_memory_gb / 2), 8)
        optimal_workers = max(1, optimal_workers)  # Minimum 1 worker
        
        print(f"🔧 Auto-detected: {optimal_workers} workers (CPU: {cpu_count}, RAM: {available_memory_gb:.1f}GB)")
        return optimal_workers
    
    def load_log(self):
        """Load backup log"""
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    log = json.load(f)
                    print(f"📂 Loaded log from {self.log_file}")
                    return log
            except:
                print("⚠️  Cannot load log, creating new...")
        
        return {
            'backed_up_files': {},
            'last_run': None
        }
    
    def save_log(self):
        """Save backup log"""
        self.backup_log['last_run'] = datetime.now().isoformat()
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(self.backup_log, f, indent=2, ensure_ascii=False)
    
    def get_file_info(self, file_id):
        """Get file/folder information"""
        try:
            return self.service.files().get(
                fileId=file_id,
                fields='id, name, mimeType, size, parents'
            ).execute()
        except HttpError as e:
            print(f"❌ Error getting info: {e}")
            return None
    
    def list_files(self, folder_id, page_size=1000):
        """List all files in folder"""
        query = f"'{folder_id}' in parents and trashed=false"
        all_items = []
        page_token = None
        
        try:
            while True:
                response = self.service.files().list(
                    q=query,
                    pageSize=page_size,
                    fields='nextPageToken, files(id, name, mimeType, size, parents)',
                    pageToken=page_token
                ).execute()
                
                all_items.extend(response.get('files', []))
                page_token = response.get('nextPageToken')
                
                if not page_token:
                    break
            
            return all_items
        except HttpError as e:
            if e.resp.status == 429:
                print("\n⚠️  WARNING: API rate limit reached!")
                self._handle_rate_limit()
            else:
                print(f"❌ Error listing files: {e}")
            return []
    
    def create_folder(self, folder_name, parent_id):
        """Create new folder"""
        try:
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [parent_id]
            }
            
            folder = self.service.files().create(
                body=file_metadata,
                fields='id'
            ).execute()
            
            print(f"✅ Created folder: {folder_name}")
            return folder.get('id')
        except HttpError as e:
            if e.resp.status == 429:
                print("\n⚠️  WARNING: API rate limit reached!")
                self._handle_rate_limit()
            else:
                print(f"❌ Error creating folder: {e}")
            return None
    
    def _handle_rate_limit(self):
        """Handle rate limit errors"""
        error_count = self.backup_state.increment_rate_limit_error()
        
        print(f"\n{'='*80}")
        print(f"⚠️  RATE LIMIT - Occurrence {error_count}/{MAX_CONSECUTIVE_RATE_LIMIT_ERRORS}")
        print(f"{'='*80}")
        
        if error_count >= MAX_CONSECUTIVE_RATE_LIMIT_ERRORS:
            print("\n🛑 MAXIMUM LIMIT REACHED!")
            
            if self.manual_mode:
                print("\n💡 RECOMMENDATIONS:")
                print("="*80)
                print("1. ✅ State saved safely")
                print("2. ✅ STOP RUNTIME NOW (Runtime → Disconnect and delete runtime)")
                print("3. ✅ Wait 24 hours")
                print("4. ✅ Restart notebook → Auto-resume")
                print("="*80)
                
                # Save paused state
                pending_files = []
                with self.state_lock:
                    if hasattr(self, 'current_batch'):
                        pending_files = self.current_batch
                
                self.backup_state.update(
                    status='paused',
                    pending_files=pending_files,
                    current_folder=self.backup_state.state.get('current_folder')
                )
                
                self.should_stop = True
            else:
                print(f"\n⏰ Waiting {RATE_LIMIT_COOLDOWN_HOURS} hours then retry...")
                time.sleep(RATE_LIMIT_COOLDOWN_HOURS * 3600)
    
    def download_file(self, file_id, file_name, local_path):
        """Download file from Drive"""
        try:
            request = self.service.files().get_media(fileId=file_id)
            
            with open(local_path, 'wb') as f:
                downloader = MediaIoBaseDownload(f, request, chunksize=10*1024*1024)
                done = False
                
                while not done:
                    status, done = downloader.next_chunk()
            
            self.download_stats['success'] += 1
            return True
            
        except HttpError as e:
            if e.resp.status == 429:
                self._handle_rate_limit()
                self.download_stats['failed'] += 1
                return False
            else:
                print(f"❌ Error downloading {file_name}: {e}")
                self.download_stats['failed'] += 1
                return False
        except Exception as e:
            print(f"❌ Unknown error: {e}")
            self.download_stats['failed'] += 1
            return False
    
    def upload_file(self, local_path, file_name, parent_id):
        """Upload file to Drive"""
        try:
            file_metadata = {
                'name': file_name,
                'parents': [parent_id]
            }
            
            media = MediaFileUpload(
                local_path,
                resumable=True,
                chunksize=10*1024*1024
            )
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            self.upload_stats['success'] += 1
            return file.get('id')
            
        except HttpError as e:
            if e.resp.status == 429:
                self._handle_rate_limit()
                self.upload_stats['failed'] += 1
                return None
            else:
                print(f"❌ Error uploading {file_name}: {e}")
                self.upload_stats['failed'] += 1
                return None
        except Exception as e:
            print(f"❌ Unknown error: {e}")
            self.upload_stats['failed'] += 1
            return None
    
    def _process_single_file(self, file_item, backup_folder_id):
        """Process a single file"""
        if self.should_stop:
            return None
        
        file_id = file_item['id']
        file_name = file_item['name']
        
        # Check if already backed up
        if file_id in self.backup_log['backed_up_files']:
            self.download_stats['skipped'] += 1
            return None
        
        # Create temporary local path
        local_path = os.path.join(self.local_temp_dir, file_name)
        
        # Download file
        if not self.download_file(file_id, file_name, local_path):
            return {'id': file_id, 'name': file_name, 'status': 'failed'}
        
        # Upload to backup folder
        new_file_id = self.upload_file(local_path, file_name, backup_folder_id)
        
        # Delete local file
        try:
            os.remove(local_path)
        except:
            pass
        
        if new_file_id:
            # Save to log immediately
            with self.log_lock:
                self.backup_log['backed_up_files'][file_id] = {
                    'name': file_name,
                    'type': 'file',
                    'backup_id': new_file_id,
                    'backup_time': datetime.now().isoformat()
                }
                self.save_log()
            
            # Update state
            with self.state_lock:
                self.backup_state.state['total_files_processed'] += 1
                self.backup_state.save_state()
            
            return {'id': file_id, 'name': file_name, 'status': 'success'}
        else:
            return {'id': file_id, 'name': file_name, 'status': 'failed'}
    
    def _process_files_batch(self, files, backup_folder_id):
        """Process batch of files with multi-threading"""
        if not files or self.should_stop:
            return
        
        print(f"\n📥 Processing {len(files)} files...")
        
        # Save current batch
        self.current_batch = files
        
        failed_files = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            with tqdm(total=len(files), desc="Progress") as pbar:
                futures = {
                    executor.submit(self._process_single_file, f, backup_folder_id): f 
                    for f in files
                }
                
                for future in concurrent.futures.as_completed(futures):
                    if self.should_stop:
                        executor.shutdown(wait=False, cancel_futures=True)
                        break
                    
                    try:
                        result = future.result()
                        if result and result['status'] == 'failed':
                            failed_files.append(futures[future])
                    except Exception as e:
                        print(f"❌ Processing error: {e}")
                        failed_files.append(futures[future])
                    
                    pbar.update(1)
                    
                    # Memory cleanup
                    if pbar.n % 10 == 0:
                        gc.collect()
        
        # Save failed files to state
        if failed_files:
            with self.state_lock:
                current_failed = self.backup_state.state.get('failed_files', [])
                current_failed.extend(failed_files)
                self.backup_state.update(failed_files=current_failed)
    
    def _backup_folder_recursive(self, source_folder_id, backup_folder_id):
        """Recursively backup folder"""
        if self.should_stop:
            return
        
        # Get items list
        items = self.list_files(source_folder_id)
        
        if not items:
            return
        
        # Categorize
        folders = [i for i in items if i['mimeType'] == 'application/vnd.google-apps.folder']
        files = [i for i in items if i['mimeType'] != 'application/vnd.google-apps.folder']
        
        # Process folders first
        for folder_item in folders:
            if self.should_stop:
                break
            
            item_id = folder_item['id']
            item_name = folder_item['name']
            
            if item_id in self.backup_log['backed_up_files']:
                continue
            
            print(f"\n📁 Processing: {item_name}")
            new_folder_id = self.create_folder(item_name, backup_folder_id)
            
            if new_folder_id:
                self._backup_folder_recursive(item_id, new_folder_id)
                
                with self.log_lock:
                    self.backup_log['backed_up_files'][item_id] = {
                        'name': item_name,
                        'type': 'folder',
                        'backup_time': datetime.now().isoformat()
                    }
        
        # Process files
        if files and not self.should_stop:
            self._process_files_batch(files, backup_folder_id)
    
    def smart_backup(self):
        """
        SMART BACKUP - Auto-detect and resume
        No manual mode selection needed
        """
        
        # Check for paused state
        if self.backup_state.state['status'] == 'paused':
            if not self.backup_state.can_resume():
                print("\n⏰ Not enough time passed for resume (need 24h)")
                print("💡 Please come back later\n")
                return None
            
            # Auto resume
            print("\n" + "="*80)
            print("🔄 AUTO-RESUME - Detected paused backup")
            print("="*80)
            
            backup_folder_id = self.backup_state.state.get('backup_folder_id')
            
            if not backup_folder_id:
                print("❌ Backup folder ID not found")
                return None
            
            print(f"📁 Backup folder: {backup_folder_id}")
            
            pending = self.backup_state.state.get('pending_files', [])
            failed = self.backup_state.state.get('failed_files', [])
            
            print(f"📊 Pending: {len(pending)} | Failed: {len(failed)}")
            
            all_retry = pending + failed
            
            if all_retry:
                print(f"\n🔄 Retrying {len(all_retry)} files...")
                self._process_files_batch(all_retry, backup_folder_id)
                
                if not self.should_stop:
                    self.backup_state.update(
                        pending_files=[],
                        failed_files=[],
                        status='completed'
                    )
                    print("\n✅ Resume completed!")
            else:
                print("\n✅ No files need retry!")
                self.backup_state.update(status='completed')
            
            return backup_folder_id
        
        # New backup
        print("\n" + "="*80)
        print("🆕 NEW BACKUP")
        print("="*80)
        
        source_info = self.get_file_info(SOURCE_FOLDER_ID)
        if not source_info:
            print("❌ Cannot get source folder info")
            return None
        
        backup_folder_name = source_info['name'] + FOLDER_SUFFIX
        backup_folder_id = self.create_folder(backup_folder_name, BACKUP_PARENT_ID)
        
        if not backup_folder_id:
            return None
        
        self.backup_state.update(
            status='in_progress',
            backup_folder_id=backup_folder_id,
            current_folder=SOURCE_FOLDER_ID
        )
        
        self.download_stats = {'success': 0, 'failed': 0, 'skipped': 0}
        self.upload_stats = {'success': 0, 'failed': 0}
        
        self._backup_folder_recursive(SOURCE_FOLDER_ID, backup_folder_id)
        
        self.save_log()
        
        if self.should_stop:
            print(f"\n⏸️  BACKUP PAUSED")
        else:
            self.backup_state.update(status='completed')
            print(f"\n✅ BACKUP COMPLETED!")
        
        print(f"\n📊 Download: ✅ {self.download_stats['success']} | "
              f"❌ {self.download_stats['failed']} | ⏭️ {self.download_stats['skipped']}")
        print(f"📊 Upload: ✅ {self.upload_stats['success']} | ❌ {self.upload_stats['failed']}")
        
        return backup_folder_id
    
    def get_backup_stats(self):
        """Display backup statistics"""
        total = len(self.backup_log['backed_up_files'])
        files = sum(1 for i in self.backup_log['backed_up_files'].values() if i['type'] == 'file')
        folders = sum(1 for i in self.backup_log['backed_up_files'].values() if i['type'] == 'folder')
        
        print("\n" + "="*80)
        print("📊 BACKUP STATISTICS")
        print("="*80)
        print(f"Total: {total} | Files: {files} | Folders: {folders}")
        print(f"Last run: {self.backup_log.get('last_run', 'None')}")
        print(f"Status: {self.backup_state.state['status']}")
        
        if self.backup_state.state.get('pending_files'):
            print(f"Pending: {len(self.backup_state.state['pending_files'])}")
        if self.backup_state.state.get('failed_files'):
            print(f"Failed: {len(self.backup_state.state['failed_files'])}")
        
        print("="*80 + "\n")


# ============================================================
# STEP 6: INITIALIZE & RUN BACKUP
# ============================================================

print("🔧 Initializing Backup Manager...")
backup_manager = DriveBackupManager(
    drive_service,
    log_file=LOG_FILE,
    state_file=STATE_FILE,
    max_workers=MAX_WORKERS,
    manual_mode=MANUAL_RESUME_MODE
)

# Display current stats
backup_manager.get_backup_stats()

# ============================================================
# 🚀 RUN BACKUP - AUTO SMART
# ============================================================

print("\n" + "="*80)
print("🎯 RECOMMENDED WORKFLOW:")
print("="*80)
print("1. Run backup normally")
print("2. If rate limit occurs → STOP RUNTIME")
print("3. Wait 24 hours")
print("4. Restart notebook → AUTO-RESUME")
print("="*80 + "\n")

print("🚀 STARTING BACKUP...")
start_time = time.time()

# SMART BACKUP - Auto-detect resume or new backup
backup_folder_id = backup_manager.smart_backup()

end_time = time.time()

# ============================================================
# RESULTS
# ============================================================

if backup_folder_id:
    duration = end_time - start_time
    print(f"\n✅ SUCCESS!")
    print(f"⏱️  Duration: {duration:.2f}s ({duration/60:.2f} minutes)")
    print(f"📁 Backup Folder ID: {backup_folder_id}")
    print(f"🔗 Link: https://drive.google.com/drive/folders/{backup_folder_id}")
    
    backup_manager.get_backup_stats()
elif backup_manager.should_stop:
    print(f"\n💡 NEXT STEPS:")
    print("="*80)
    print("✅ State saved safely")
    print("✅ STOP RUNTIME NOW (Runtime → Disconnect)")
    print("✅ Wait 24 hours")
    print("✅ Reopen notebook → Run again → Auto-resume")
    print("="*80 + "\n")
else:
    print("\n❌ BACKUP FAILED!")

# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def view_state():
    """View backup state"""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            state = json.load(f)
            print("\n📊 BACKUP STATE:")
            print(json.dumps(state, indent=2, ensure_ascii=False))

def view_log():
    """View backup log"""
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as f:
            log = json.load(f)
            print(f"\n📊 BACKUP LOG:")
            print(f"Total backed up files: {len(log['backed_up_files'])}")

def download_files():
    """Download state and log files"""
    from google.colab import files
    for filename in [STATE_FILE, LOG_FILE]:
        if os.path.exists(filename):
            files.download(filename)
            print(f"✅ Downloaded: {filename}")

print("""
================================================================================
                        UTILITY FUNCTIONS
================================================================================

view_state()      # View detailed backup state
view_log()        # View backup log
download_files()  # Download state + log files to local machine

================================================================================
""")
