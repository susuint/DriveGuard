# 📚 USER GUIDE - GOOGLE DRIVE BACKUP TOOL v1.9.1

## 📋 TABLE OF CONTENTS

1. [Introduction](#introduction)
2. [Key Features](#key-features)
3. [System Requirements](#system-requirements)
4. [Installation & Configuration](#installation--configuration)
5. [User Guide](#user-guide)
6. [Advanced Features](#advanced-features)
7. [Troubleshooting](#troubleshooting)
8. [FAQ](#faq)
9. [Best Practices](#best-practices)

---

## 🎯 INTRODUCTION

### Overview

**Google Drive Backup Tool v1.9.1** is an automated backup solution specifically designed to handle Google Drive API rate limits. This tool is optimized for **manual resume** - allowing you to stop the backup process and continue the next day automatically.

### Problem Solved

- ✅ **API Limits**: Google Drive API has limits of 20,000 requests/100 seconds/user
- ✅ **Large Data Backup**: Backup thousands of files without interruption worries
- ✅ **Auto-Continue**: No manual intervention needed when restarting
- ✅ **Data Safety**: Checkpoint after each file, no progress loss

### Highlights

- 🚀 **Smart Resume**: Auto-detect and continue from pause point
- 💾 **Checkpoint System**: Save state after each successful file
- 🛡️ **Rate Limit Protection**: Intelligent handling of API limits
- ⚡ **Multi-threading**: Optimized speed with parallel processing
- 📊 **Real-time Statistics**: Detailed progress tracking
- 🔄 **Retry Mechanism**: Automatic retry of failed files

---

## ✨ KEY FEATURES

### 1. Automatic & Recursive Backup

```
Source Folder/
├── Subfolder 1/
│   ├── File 1.pdf
│   └── File 2.docx
├── Subfolder 2/
│   └── File 3.xlsx
└── File 4.txt

→ Automatically backs up entire folder structure
```

**Characteristics:**
- ✅ Recursive backup of all subfolders
- ✅ Preserves folder structure
- ✅ Supports all file types (Office, PDF, images, videos, etc.)
- ✅ Automatically skips already backed up files

### 2. Smart Resume - Auto-Continue

**Usage Scenario:**

```
Run 1 (Day 1):
[==============40%==============          ] 2000/5000 files
⚠️ RATE LIMIT! → STOP RUNTIME

Run 2 (Day 2 - After 24h):
[                              ===========] 3000/5000 files
✅ AUTO-RESUME from file 2001!
```

**How it Works:**
1. Detect `backup_state.json` file
2. Check elapsed time (must be ≥ 24h)
3. Auto-load pending/failed files list
4. Continue backup without configuration

### 3. Rate Limit Protection - Smart Protection

**3-Tier System:**

```
Error 1: ⚠️ Warning - Continue
Error 2: ⚠️⚠️ Severe warning - Continue  
Error 3: 🛑 STOP - Save state - Recommend stopping runtime
```

**Automatic Actions:**
- Save current state
- Save pending files list
- Set timestamp for error
- Clear notification to stop runtime

### 4. Checkpoint System - No Progress Loss

**Save after each action:**
- ✅ After each successful file download
- ✅ After each successful file upload  
- ✅ After each successful folder creation
- ✅ After each rate limit error

**Storage Files:**
- `backup_state.json`: Current state (pending, failed, completed)
- `backup_log.json`: History of all backed up files

### 5. Multi-threading - Speed Optimization

**Auto-detection:**
```python
Workers = min(CPU cores, RAM_GB/2, 8)

Examples:
- CPU: 4 cores, RAM: 12GB → 4 workers
- CPU: 8 cores, RAM: 8GB → 4 workers  
- CPU: 16 cores, RAM: 32GB → 8 workers (max)
```

**Benefits:**
- ⚡ 3-5x faster than single-thread
- 💾 Auto-adjust based on resources
- 🛡️ No system overload

### 6. Real-time Statistics

**Display:**
```
📊 Progress:
[====================75%=====] 3750/5000 files

📥 Download: ✅ 3700 | ❌ 30 | ⏭️ 20
📤 Upload:   ✅ 3680 | ❌ 50

⏱️ Duration: 45:32 minutes
🚀 Speed: ~83 files/minute
```

### 7. Retry Mechanism - Smart Retry

**Strategy:**
1. **Immediate retry**: No immediate retry (avoid rate limit)
2. **Batch retry**: Retry all failed files on resume
3. **Smart skip**: Skip successfully backed up files

**Failed Files Management:**
```json
{
  "failed_files": [
    {"id": "file123", "name": "document.pdf", "reason": "rate_limit"},
    {"id": "file456", "name": "image.jpg", "reason": "timeout"}
  ]
}
```

---

## 💻 SYSTEM REQUIREMENTS

### Environment

| Requirement | Description |
|-------------|-------------|
| **Platform** | Google Colab (recommended) or Jupyter Notebook |
| **Python** | 3.7+ |
| **RAM** | Minimum 2GB, recommended 4GB+ |
| **Google Account** | Account with Drive access permissions |

### Dependencies

```python
google-auth>=2.0.0
google-auth-oauthlib>=0.5.0
google-auth-httplib2>=0.1.0
google-api-python-client>=2.0.0
tqdm>=4.60.0
requests>=2.25.0
psutil>=5.8.0
```

### Google Drive Permissions

- ✅ Read source files/folders
- ✅ Create new folders
- ✅ Upload files
- ✅ List files/folders

---

## ⚙️ INSTALLATION & CONFIGURATION

### Step 1: Get Folder ID

**How to get Folder ID from Google Drive:**

1. Open Google Drive in browser
2. Right-click on folder → **Share** → **Copy link**
3. Link format: `https://drive.google.com/drive/folders/1ABC...XYZ`
4. Take the `1ABC...XYZ` part (after `/folders/`)

**Example:**
```
Link: https://drive.google.com/drive/folders/1ABCdefGHIjklMNOpqrSTUvwxYZ123456
ID:   1ABCdefGHIjklMNOpqrSTUvwxYZ123456
```

### Step 2: Configure in Code

**Open Python file and edit:**

```python
# ⚠️ CHANGE THESE 2 LINES
SOURCE_FOLDER_ID = '1ABC...'  # Folder to backup
BACKUP_PARENT_ID = '1XYZ...'  # Folder to store backups
```

**Advanced Options:**

```python
# Backup folder suffix
FOLDER_SUFFIX = '_BACKUP'  # Result: "MyFolder_BACKUP"

# Processing workers
MAX_WORKERS = None  # None = auto-detect, or set specific number (1-8)

# Rate limit protection
MAX_CONSECUTIVE_RATE_LIMIT_ERRORS = 3  # Stop after 3 consecutive errors
RATE_LIMIT_COOLDOWN_HOURS = 24  # Cooldown time (hours)

# Resume mode
MANUAL_RESUME_MODE = True  # True = recommend stopping runtime
                           # False = auto-wait (not recommended)
```

### Step 3: Upload to Google Colab

1. Go to [Google Colab](https://colab.research.google.com/)
2. **File** → **Upload notebook**
3. Select `.py` file or create new notebook and copy code

---

## 🚀 USER GUIDE

### Basic Workflow

#### **First Run**

```
1. Open Google Colab
2. Upload Python file
3. Edit SOURCE_FOLDER_ID and BACKUP_PARENT_ID
4. Runtime → Run all
5. Allow Google Drive access permissions
6. Wait for process to complete
```

**Sample Output:**
```
🔐 Authenticating with Google Drive...
✅ Authentication successful!

🔧 Auto-detected: 4 workers (CPU: 4, RAM: 12.7GB)

⚙️  CONFIGURATION:
📁 Source: 1ABCdefGHIjklMNOpqrSTUvwxYZ123456
📁 Backup Parent: 1XYZabcDEFghiJKLmnoPQRstUVWxyz789
🎯 Resume Mode: MANUAL (Recommended)

🆕 NEW BACKUP
✅ Created folder: MyDocuments_BACKUP

📥 Processing 2458 files...
[====================75%=====] 1844/2458

⚠️  WARNING: API rate limit reached!
⚠️  RATE LIMIT - Occurrence 3/3
🛑 MAXIMUM LIMIT REACHED!

💡 RECOMMENDATIONS:
================================================================================
1. ✅ State saved safely
2. ✅ STOP RUNTIME NOW (Runtime → Disconnect and delete runtime)
3. ✅ Wait 24 hours
4. ✅ Restart notebook → Auto-resume
================================================================================
```

**Action:**
```
1. Runtime → Disconnect and delete runtime
2. Close browser
3. Wait 24 hours
```

#### **Second Run (Resume)**

```
1. Reopen Google Colab
2. Open same notebook
3. Runtime → Run all
4. Program AUTO-RESUMES!
```

**Sample Output:**
```
🔐 Authenticating with Google Drive...
✅ Authentication successful!

📂 Loaded state from backup_state.json

🔄 AUTO-RESUME - Detected paused backup
📁 Backup folder: 1BackupFolderID
📊 Pending: 614 | Failed: 0

🔄 Retrying 614 files...
[====================100%====] 614/614

✅ Resume completed!

📊 Download: ✅ 2458 | ❌ 0 | ⏭️ 0
📊 Upload: ✅ 2458 | ❌ 0

⏱️ Duration: 18:45 minutes
```

### Complete Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                      FIRST RUN                               │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
                  ┌────────────────┐
                  │ Configure code │
                  │ (Folder IDs)   │
                  └────────┬───────┘
                           │
                           ▼
                  ┌────────────────┐
                  │ Run notebook   │
                  └────────┬───────┘
                           │
                           ▼
                  ┌────────────────┐
                  │ Auth Drive     │
                  └────────┬───────┘
                           │
                           ▼
              ┌────────────┴──────────────┐
              │                           │
              ▼                           ▼
    ┌─────────────────┐         ┌──────────────────┐
    │ Complete OK     │         │ Rate Limit Hit   │
    │ ✅ Success!     │         │ ⚠️ Need to stop  │
    └─────────────────┘         └────────┬─────────┘
                                         │
                                         ▼
                                ┌────────────────┐
                                │ Save state     │
                                │ Stop runtime   │
                                └────────┬───────┘
                                         │
                                         ▼
                                ┌────────────────┐
                                │ Wait 24 hours  │
                                └────────┬───────┘
                                         │
┌────────────────────────────────────────┴───────────────────┐
│                    SECOND RUN (RESUME)                      │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
                  ┌────────────────┐
                  │ Run notebook   │
                  └────────┬───────┘
                           │
                           ▼
                  ┌────────────────┐
                  │ Load state     │
                  │ Auto resume    │
                  └────────┬───────┘
                           │
                           ▼
              ┌────────────┴──────────────┐
              │                           │
              ▼                           ▼
    ┌─────────────────┐         ┌──────────────────┐
    │ Complete OK     │         │ Still rate limit │
    │ ✅ Success!     │         │ ⚠️ Repeat        │
    └─────────────────┘         └──────────────────┘
                                         │
                                         ▼
                              (Back to wait 24h step)
```

---

## 🔧 ADVANCED FEATURES

### 1. Utility Functions

**View detailed state:**
```python
view_state()
```

**Output:**
```json
{
  "status": "paused",
  "current_folder": "1ABC...",
  "pending_files": [
    {"id": "file1", "name": "doc.pdf"},
    {"id": "file2", "name": "img.jpg"}
  ],
  "failed_files": [],
  "consecutive_rate_limit_errors": 3,
  "last_rate_limit_time": "2026-02-01T15:30:00",
  "backup_folder_id": "1XYZ...",
  "total_files_processed": 1844,
  "created_at": "2026-02-01T10:00:00",
  "updated_at": "2026-02-01T15:30:15"
}
```

**View backup log:**
```python
view_log()
```

**Output:**
```
📊 BACKUP LOG:
Total backed up files: 1844
```

**Download files:**
```python
download_files()
```
- Downloads `backup_state.json` and `backup_log.json` to local machine
- Useful for backup or debugging

### 2. Manual Control

**Force resume:**
```python
# If you need to force resume before 24h
# (Not recommended - may hit rate limit again)

# 1. Edit state file
import json
with open('backup_state.json', 'r+') as f:
    state = json.load(f)
    state['last_rate_limit_time'] = None  # Reset time
    f.seek(0)
    json.dump(state, f, indent=2)
    f.truncate()

# 2. Run notebook again
```

**Complete reset:**
```python
# Delete all state and log to start fresh
import os

if os.path.exists('backup_state.json'):
    os.remove('backup_state.json')
    
if os.path.exists('backup_log.json'):
    os.remove('backup_log.json')

print("✅ Reset complete! Run again to start new backup.")
```

### 3. Custom Configuration

**Backup multiple folders:**
```python
# Create list of folders to backup
folders_to_backup = [
    ('1ABC...', '1XYZ...'),  # (Source, Destination)
    ('1DEF...', '1UVW...'),
    ('1GHI...', '1RST...')
]

# Loop through each folder
for source, dest in folders_to_backup:
    SOURCE_FOLDER_ID = source
    BACKUP_PARENT_ID = dest
    
    # Create new manager for each folder
    backup_manager = DriveBackupManager(
        drive_service,
        log_file=f'backup_log_{source[:8]}.json',
        state_file=f'backup_state_{source[:8]}.json',
        max_workers=MAX_WORKERS,
        manual_mode=MANUAL_RESUME_MODE
    )
    
    backup_manager.smart_backup()
```

**Custom naming:**
```python
# Custom folder suffix with timestamp
from datetime import datetime

FOLDER_SUFFIX = f'_BACKUP_{datetime.now().strftime("%Y%m%d")}'
# Result: "MyFolder_BACKUP_20260201"
```

**Custom workers:**
```python
# Reduce workers if low RAM
MAX_WORKERS = 2

# Increase workers if high RAM
MAX_WORKERS = 6

# Disable multi-threading
MAX_WORKERS = 1
```

### 4. Monitoring & Logging

**Custom logging:**
```python
import logging

# Enable detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('detailed_backup.log'),
        logging.StreamHandler()
    ]
)
```

**Real-time monitoring:**
```python
# Add to _process_files_batch
def _process_files_batch(self, files, backup_folder_id):
    start_time = time.time()
    
    # ... existing code ...
    
    # Calculate speed
    elapsed = time.time() - start_time
    rate = len(files) / elapsed if elapsed > 0 else 0
    
    print(f"\n⚡ Speed: {rate:.1f} files/second")
    print(f"📊 Total time: {elapsed/60:.1f} minutes")
```

---

## 🔍 TROUBLESHOOTING

### Common Issues

#### 1. "Authentication failed"

**Causes:**
- Permissions not granted
- Session expired

**Solutions:**
```python
# 1. Re-run authentication cell
auth.authenticate_user()

# 2. Clear output and run entire notebook
# Runtime → Restart and run all
```

#### 2. "Folder ID not found"

**Causes:**
- Wrong Folder ID
- No access permissions to folder

**Solutions:**
```python
# Check if folder exists
file_info = drive_service.files().get(fileId=SOURCE_FOLDER_ID).execute()
print(file_info['name'])

# If error → Wrong Folder ID or no permissions
```

#### 3. "Rate limit even after 24h"

**Causes:**
- Not exactly 24h yet
- Different time zones

**Solutions:**
```python
# Check exact time
from datetime import datetime

with open('backup_state.json', 'r') as f:
    state = json.load(f)
    last_time = datetime.fromisoformat(state['last_rate_limit_time'])
    now = datetime.now()
    hours = (now - last_time).total_seconds() / 3600
    
    print(f"Elapsed: {hours:.1f} hours")
    print(f"Remaining: {24 - hours:.1f} hours")
```

#### 4. "Out of memory"

**Causes:**
- Too many workers
- Files too large

**Solutions:**
```python
# Reduce workers
MAX_WORKERS = 2

# Or increase Colab RAM
# Runtime → Change runtime type → High-RAM
```

#### 5. "Upload failed - timeout"

**Causes:**
- Files too large
- Unstable connection

**Solutions:**
```python
# Increase timeout in upload_file
media = MediaFileUpload(
    local_path,
    resumable=True,
    chunksize=10*1024*1024  # 10MB chunks
)

# Retry with exponential backoff
```

#### 6. "Backup incomplete but status = completed"

**Causes:**
- Files in failed_files

**Solutions:**
```python
view_state()  # Check failed_files

# Manually retry failed files
failed = backup_state.state.get('failed_files', [])
if failed:
    print(f"{len(failed)} files failed")
    # Run again to retry
```

### Debug Mode

**Enable debug for details:**
```python
import logging

logging.basicConfig(level=logging.DEBUG)

# View all API calls
logging.getLogger('googleapiclient.discovery').setLevel(logging.DEBUG)
```

### Error Recovery

**Recover from critical errors:**
```python
# 1. Backup state files
download_files()

# 2. Check state
view_state()
view_log()

# 3. If needed, manually edit state file
import json

with open('backup_state.json', 'r+') as f:
    state = json.load(f)
    
    # Fix status
    state['status'] = 'paused'
    
    # Reset error counter
    state['consecutive_rate_limit_errors'] = 0
    
    # Save
    f.seek(0)
    json.dump(state, f, indent=2)
    f.truncate()
```

---

## ❓ FAQ

### Q1: How long to backup 10,000 files?

**A:** Depends on:
- File size (average 1-5MB/file)
- Workers count (4 workers = ~80-100 files/minute)
- Rate limits (may need 2-3 runs)

**Estimate:**
```
10,000 files × 1MB = ~10GB
Speed: ~80 files/minute × 60 = ~4,800 files/hour
→ Need ~2-3 hours (without rate limit)
→ Reality: 2-3 days (with rate limits)
```

### Q2: Is there a cost?

**A:** 
- ✅ Google Colab: FREE
- ✅ Google Drive API: FREE (within limits)
- ⚠️ Colab Pro: $10/month (more RAM, fewer limits)

### Q3: Can backup Google Workspace files (Docs, Sheets)?

**A:** YES, but need export:
```python
# Export Google Docs to .docx
def export_gdoc(file_id):
    request = drive_service.files().export_media(
        fileId=file_id,
        mimeType='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )
    # ... download and upload ...
```

### Q4: Can it be scheduled automatically?

**A:** NOT directly on Colab, but possible with:
- Google Cloud Functions + Scheduler
- Local script + cron job
- Apps Script (more limited)

### Q5: How are duplicates handled?

**A:** 
- Check by File ID (not name)
- Each file backed up only once
- Update if source file changes (needs customization)

### Q6: Can resume from different machine?

**A:** YES, if you have state files:
```
1. Download backup_state.json and backup_log.json
2. Upload to new Colab
3. Run notebook → Auto-resume
```

### Q7: Does deleting backup folder affect anything?

**A:**
- Doesn't affect source folder
- State file still references deleted folder
- Should reset state if wanting to backup again

### Q8: Google Drive API limits?

**A:**
```
- 20,000 requests per 100 seconds per user
- 1 billion requests per day (default)
- 10 requests per second per user
```

### Q9: Can backup shared drives?

**A:** YES, needs additional parameters:
```python
# In list_files
response = drive_service.files().list(
    q=query,
    pageSize=page_size,
    fields='nextPageToken, files(id, name, mimeType, size, parents)',
    pageToken=page_token,
    supportsAllDrives=True,  # Add this line
    includeItemsFromAllDrives=True  # And this line
).execute()
```

### Q10: Is Colab RAM sufficient?

**A:**
- Colab Free: 12-13GB RAM (enough for most cases)
- Colab Pro: 25GB RAM
- Colab Pro+: 50GB RAM

This tool is RAM-optimized, usually uses <2GB.

---

## 💡 BEST PRACTICES

### 1. Before Running

```
✅ Check Drive storage (ensure enough space)
✅ Test with small folder first
✅ Read output messages carefully
✅ Backup state files periodically
✅ Use clear folder names
```

### 2. During Execution

```
✅ Don't close browser
✅ Don't turn off computer
✅ Monitor output regularly
✅ Be ready to stop when rate limit warning appears
```

### 3. When Rate Limit Hits

```
✅ STOP RUNTIME IMMEDIATELY (don't wait)
✅ Verify state file is saved
✅ Set reminder for 24h later
✅ Don't run any Drive API for 24h
```

### 4. Performance Optimization

```python
# 1. Increase chunk size for large files
chunksize=50*1024*1024  # 50MB

# 2. Reduce workers for many small files
MAX_WORKERS = 2

# 3. Batch processing
# Process 100 files at a time instead of all

# 4. Use Colab Pro if needed
# Fewer rate limits, more RAM
```

### 5. Security

```
⚠️ DON'T share state files (contain folder IDs)
⚠️ DON'T commit state files to Git
⚠️ Revoke access after completion
⚠️ Use service account for production
```

### 6. Backup Strategy

```
Day 1: Full backup
Day 7: Incremental backup (new/changed files only)
Day 30: New full backup + delete old backup
```

### 7. Monitoring

```python
# Add notifications
def send_notification(message):
    # Discord webhook
    import requests
    webhook_url = "YOUR_DISCORD_WEBHOOK"
    requests.post(webhook_url, json={"content": message})

# Call when complete or error
send_notification("✅ Backup completed!")
```

---

## 📞 SUPPORT & CONTRIBUTION

### Report Issues

If you encounter problems:
1. Check [Troubleshooting](#troubleshooting) section
2. See [FAQ](#faq)
3. Create issue with information:
   - Complete output
   - State file (remove sensitive info)
   - Steps taken

### Contribute

Contributions welcome!
- Report bugs
- Suggest features
- Improve documentation
- Submit pull requests

### License

MIT License - Free to use for personal and commercial purposes.

---

## 📝 CHANGELOG

### v1.9.1 (2026-02-02)
- ✅ Auto-detect resume mode
- ✅ Improved rate limit handling
- ✅ Better checkpoint system
- ✅ Enhanced logging

### v1.9.0 (2026-01-15)
- ✅ Smart resume feature
- ✅ Multi-threading support
- ✅ State management

### v1.8.0 (2025-12-01)
- ✅ Initial release

---

**Happy backing up! 🎉**

*Last updated: 02/02/2026*
