### 🇺🇸 BẢN 2: ENGLISH
*Tên file gợi ý: `USER_GUIDE_ENGLISH.md`*

```markdown
# User Guide: Google Drive Backup Tool v1.9.1

**Version:** 1.9.1 FINAL (Manual Resume Optimized)  
**Release Date:** February 02, 2026

---

## 📖 Overview

The **Google Drive Backup Tool** is a robust, Python-based utility designed to run on Google Colab. It enables users to seamlessly clone or backup entire Google Drive folders to another location on the same drive.

The highlight of **v1.9.1** is its **Manual Resume Optimization**, specifically engineered to handle Google API Rate Limits intelligently without losing progress or requiring complex reconfiguration.

---

## ✨ Key Features

*   **🔄 Smart Resume:** Automatically detects interrupted backup sessions and resumes from the exact point of failure without manual intervention.
*   **🛡️ Intelligent Rate Limit Handling:** Instead of infinite retries that fail, the tool guides you to safely stop the Runtime and resume after the cooldown period.
*   **📁 Recursive Backup:** Automatically clones all subdirectories and nested files, preserving the original folder structure.
*   **🔐 Data Integrity Verification:** Verifies file sizes and MD5 checksums to ensure 100% data accuracy between source and destination.
*   **🚀 Performance Optimization:** Auto-detects optimal worker threads (processes) based on available Colab CPU and RAM resources.
*   **💾 Atomic Checkpointing:** Saves state after every successful file operation, preventing data loss during runtime disconnections.

---

## ⚙️ Configuration & Setup

### 1. Get Folder IDs
You need the IDs for two folders before starting:
1.  **Source Folder:** The folder you want to back up.
2.  **Destination Folder:** The location where the backup will be stored.

*   **How to get ID:** Open the folder in Google Drive -> Look at the URL. The long string between `/folders/` and `/` is the ID.
    *   *Example:* `https://drive.google.com/drive/folders/1A2B3C4D5E...` -> ID is `1A2B3C4D5E...`

### 2. Edit the Code
Locate **STEP 3: MAIN CONFIGURATION** in the script and update the following values:

```python
# 📁 FOLDER IDs (REQUIRED - REPLACE WITH YOUR IDs)
SOURCE_FOLDER_ID = 'PASTE_YOUR_SOURCE_FOLDER_ID_HERE'
BACKUP_PARENT_ID = 'PASTE_YOUR_DESTINATION_FOLDER_ID_HERE'

# 🏷️  Folder Suffix
FOLDER_SUFFIX = '_BACKUP' # The backup folder will be named "OriginalName_BACKUP"
```

---

## 🚀 Usage Guide

### Standard Workflow (Recommended)
1.  **Run All Cells:** Click `Runtime` -> `Run all`.
2.  **Authenticate:** Grant Google Drive access permissions when prompted.
3.  **Monitor:** Watch the progress bars and logs in the output console.

### 🛑 Handling Rate Limits (Crucial)
This tool is built to manage `403: userRateLimitExceeded` errors effectively.

1.  Upon hitting the rate limit **3 times consecutively**, the tool will pause and display a warning.
2.  **Follow the on-screen instructions:**
    *   **STOP THE RUNTIME NOW:** Go to `Runtime` -> `Disconnect and delete runtime`.
    *   **CLOSE TAB:** You can safely close your browser window.
3.  **Wait 24 Hours:** Google resets usage quotas approximately every 24 hours.
4.  **Resuming:**
    *   Re-open the Colab notebook.
    *   Click `Run All` again.
    *   The tool will **AUTOMATICALLY DETECT** the previous session, skip completed files, and continue processing the rest.

---

## ⚡ Advanced Features

### 1. Manual Resume Mode
Enabled by default (`True`). This is the safest mode for large backups.
*   **True:** When limits are reached, the tool advises stopping the runtime to protect your account from temporary bans.
*   **False:** The tool will attempt to auto-retry (Not recommended as it may prolong the ban duration).

### 2. Worker Management
The script automatically calculates the optimal number of workers based on available RAM. To override this:
```python
MAX_WORKERS = None # None = Auto-detect, or set a specific number (e.g., 4)
```

### 3. Logs & State Management
The system generates two critical files in the Colab environment:
*   `backup_state.json`: Contains the current snapshot (pending files, failed files, timestamps). **Do not delete this** if you intend to resume later.
*   `backup_log.json`: Contains the history of successfully backed up files.

---

## 🛠️ Utilities & Debugging

After execution or for troubleshooting, use these commands in the final code cell:

*   `view_state()`: View detailed backup status (pending files, failed files, timestamps).
*   `view_log()`: View the total count of successfully backed up files.
*   `download_files()`: Download `state.json` and `log.json` to your local machine for external record-keeping.

---

## ❓ Frequently Asked Questions (Q&A)

**Q1: Can I close my browser while the backup is running?**
A: Yes, but ensure the Colab tab remains open and the computer does not sleep. However, the safest method for long-term backups is to let it run until you hit a Rate Limit, then perform the "Stop Runtime" procedure and return after 24h.

**Q2: Why should I stop the Runtime instead of just letting it retry?**
A: When Google blocks access (Rate Limit), continuous retrying often results in longer lockout periods or flags your IP as suspicious. Stopping the Runtime and waiting 24h acts as a "manual reset" adhering to Google's best practices for bulk operations.

**Q3: How do I know which files failed?**
A: Run `view_state()`. Failed files are listed in the `failed_files` array. The system will automatically attempt to re-upload these files during the Resume process.

**Q4: Can I change the destination folder halfway through?**
A: No, not recommended. Changing the destination ID will break the Resume logic because the program won't find the previously backed-up files in the new location. If you must change, delete `backup_state.json` to start a fresh backup.

**Q5: Does this support Google Docs/Sheets?**
A: Currently, the tool focuses on binary files (Video, Images, Zip, PDF, etc.). While it attempts to process all items, Google Docs/Sheets behave differently as exports. It is best used for storing media and standard files.
```
