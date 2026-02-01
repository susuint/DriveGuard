# 🚀 DriveGuard - Smart Google Drive Backup Tool

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Google Drive API](https://img.shields.io/badge/Google%20Drive-API%20v3-yellow.svg)](https://developers.google.com/drive)
[![Maintenance](https://img.shields.io/badge/Maintained-Yes-brightgreen.svg)](https://github.com/yourusername/driveguard)

> **Intelligent, resumable backup solution for Google Drive with built-in rate limit protection and smart auto-resume capabilities.**

## 📖 Overview

**DriveGuard** is a production-ready Python tool designed to handle large-scale Google Drive backups without falling victim to API rate limits. Unlike traditional backup scripts that fail when hitting quota limits, DriveGuard intelligently pauses, saves state, and automatically resumes after the cooldown period.

### ✨ Why DriveGuard?

- 🛡️ **Rate Limit Protection**: Automatically detects and handles Google Drive API quotas
- 🔄 **Smart Resume**: Auto-continues from exactly where it stopped - even days later
- 💾 **Checkpoint System**: Never lose progress - state saved after every file
- ⚡ **Multi-threaded**: Optimized parallel processing with auto-resource detection
- 📊 **Real-time Stats**: Live progress tracking with detailed analytics
- 🎯 **Production Ready**: Built for reliability with comprehensive error handling

## 🎥 Demo

```
🚀 STARTING BACKUP...
📁 Source: MyDocuments (2,458 files)
📁 Destination: MyDocuments_BACKUP

[====================75%=====] 1,844/2,458 files
📥 Download: ✅ 1,810 | ❌ 5 | ⏭️ 29
📤 Upload: ✅ 1,800 | ❌ 10

⚠️  RATE LIMIT DETECTED - Occurrence 3/3
🛑 Backup paused safely

💡 NEXT STEPS:
✅ State saved - No progress lost
✅ Stop runtime and wait 24 hours
✅ Restart → Auto-resume from file 1,845

--- Next Day ---

🔄 AUTO-RESUME detected
📊 Pending: 614 files

[====================100%====] 614/614 files
✅ BACKUP COMPLETED!
⏱️  Total duration: 45:32 minutes
```

## 🚀 Quick Start

### Prerequisites

- Python 3.7+
- Google account with Drive access
- Google Colab (recommended) or local Jupyter environment

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/driveguard.git
cd driveguard
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

### Configuration

1. **Get your Folder IDs** from Google Drive:
   - Right-click folder → Share → Copy link
   - Extract ID from URL: `https://drive.google.com/drive/folders/YOUR_FOLDER_ID`

2. **Edit configuration** in the script:
```python
SOURCE_FOLDER_ID = '1ABCdefGHIjklMNOpqrSTUvwxYZ123456'  # Folder to backup
BACKUP_PARENT_ID = '1XYZabcDEFghiJKLmnoPQRstUVWxyz789'  # Destination folder
```

3. **Run the script**
```bash
python DriveGuard_v1_9_1_EN.py
```

## 📋 Features

### Core Capabilities

| Feature | Description |
|---------|-------------|
| **Smart Resume** | Automatically detects interrupted backups and continues from pause point |
| **Rate Limit Handling** | 3-tier protection system with intelligent cooldown management |
| **Checkpoint System** | Progress saved after every successful file operation |
| **Multi-threading** | Auto-optimized parallel processing (up to 8 workers) |
| **Recursive Backup** | Preserves complete folder structure and hierarchy |
| **Deduplication** | Skips already backed-up files automatically |
| **Failed File Retry** | Smart batch retry of all failed operations |
| **Real-time Stats** | Live progress with download/upload metrics |

### Advanced Features

- 🔧 **Auto-worker Detection**: Dynamically adjusts threads based on CPU and RAM
- 📝 **Comprehensive Logging**: Detailed JSON logs for audit and debugging
- 🎛️ **Manual Override**: Fine-grained control over resume behavior
- 🔐 **Secure**: No credentials stored, OAuth-based authentication
- 📦 **Lightweight**: Minimal dependencies, optimized for Colab free tier

## 🛠️ Usage

### Basic Usage

```python
# 1. Configure your folder IDs (see Configuration section)
# 2. Run the script
# 3. Authenticate with Google when prompted
# 4. Monitor progress
# 5. If rate limit hits - follow instructions to pause and resume
```

### Resume After Rate Limit

```python
# Just run the script again after 24 hours
# DriveGuard automatically detects paused state and resumes!
python DriveGuard_v1_9_1_EN.py
```

### Utility Functions

```python
# View current backup state
view_state()

# View backup log
view_log()

# Download state files to local machine
download_files()
```

## 📊 How It Works

### Workflow Diagram

```
┌─────────────────┐
│   Start Backup  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────┐
│  Authenticate   │─────▶│ List Files   │
└─────────────────┘      └──────┬───────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │  Create Backup Folder │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │  Multi-thread Process │◀─┐
                    │  Download → Upload    │  │
                    └───────────┬───────────┘  │
                                │              │
                    ┌───────────▼───────────┐  │
                    │  Save Checkpoint      │  │
                    └───────────┬───────────┘  │
                                │              │
            ┌───────────────────┼──────────────┘
            │                   │
            ▼                   ▼
    ┌───────────────┐   ┌──────────────┐
    │  Rate Limit?  │   │  Complete?   │
    └───────┬───────┘   └──────┬───────┘
            │ Yes              │ Yes
            ▼                  ▼
    ┌───────────────┐   ┌──────────────┐
    │  Save State   │   │  ✅ Success! │
    │  Pause & Wait │   └──────────────┘
    └───────┬───────┘
            │
            ▼
    ┌───────────────┐
    │  Wait 24h     │
    └───────┬───────┘
            │
            ▼
    ┌───────────────┐
    │  Auto Resume  │──┐
    └───────────────┘  │
            │          │
            └──────────┘
```

### State Management

DriveGuard maintains two critical files:

1. **`backup_state.json`**: Current operation state
   - Status (new/in_progress/paused/completed)
   - Pending and failed file lists
   - Rate limit tracking
   - Timestamp information

2. **`backup_log.json`**: Complete backup history
   - All successfully backed up files
   - File metadata and timestamps
   - Audit trail

## 🔧 Configuration Options

### Basic Settings

```python
# Folder configuration
SOURCE_FOLDER_ID = 'your_source_folder_id'
BACKUP_PARENT_ID = 'your_backup_destination_id'
FOLDER_SUFFIX = '_BACKUP'  # Appended to backup folder name

# Performance tuning
MAX_WORKERS = None  # Auto-detect (recommended) or set 1-8

# Rate limit protection
MAX_CONSECUTIVE_RATE_LIMIT_ERRORS = 3  # Stop after N errors
RATE_LIMIT_COOLDOWN_HOURS = 24  # Hours to wait

# Resume behavior
MANUAL_RESUME_MODE = True  # Recommend stopping runtime (True)
                           # or auto-wait (False, not recommended)
```

### Advanced Configuration

```python
# Custom naming with timestamp
from datetime import datetime
FOLDER_SUFFIX = f'_BACKUP_{datetime.now().strftime("%Y%m%d_%H%M")}'

# Multiple folder backup
folders_to_backup = [
    ('source_id_1', 'dest_id_1'),
    ('source_id_2', 'dest_id_2'),
]

# Custom logging
import logging
logging.basicConfig(level=logging.INFO, filename='backup.log')
```

## 📈 Performance

### Benchmarks

| Scenario | Files | Size | Duration | Notes |
|----------|-------|------|----------|-------|
| Small backup | 500 | 2GB | ~15 min | No rate limits |
| Medium backup | 2,500 | 10GB | ~1.5 hrs | 1 rate limit pause |
| Large backup | 10,000 | 50GB | ~2-3 days | Multiple pauses |

### Optimization Tips

- 🚀 Use Colab Pro for fewer rate limits
- 💾 Adjust `MAX_WORKERS` based on file sizes
- 📦 Group small files, reduce workers for large files
- 🔄 Run during off-peak hours for better quotas

## 🔍 Troubleshooting

### Common Issues

**Authentication Failed**
```python
# Solution: Re-authenticate
auth.authenticate_user()
```

**Rate Limit Even After 24h**
```python
# Check exact timing
from datetime import datetime
# View state to see last_rate_limit_time
view_state()
```

**Out of Memory**
```python
# Reduce workers
MAX_WORKERS = 2
# Or use Colab High-RAM runtime
```

See the [User Guide](USER_GUIDE_EN.md) for comprehensive troubleshooting.

## 📚 Documentation

- **[Complete User Guide](USER_GUIDE_EN.md)** - Detailed documentation with examples
- **[Hướng Dẫn Tiếng Việt](USER_GUIDE_VI.md)** - Vietnamese user guide
- **[FAQ](#faq)** - Frequently asked questions

## ❓ FAQ

**Q: Does this cost money?**  
A: No! Google Colab and Drive API are free within quotas.

**Q: How long to backup 10,000 files?**  
A: Typically 2-3 days with rate limits (2-3 hours without).

**Q: Can I resume from a different computer?**  
A: Yes! Just download state files and upload to new environment.

**Q: Does it work with Shared Drives?**  
A: Yes, with minor code modifications (see User Guide).

**Q: Is my data safe?**  
A: DriveGuard only reads from source and writes to destination. Original files are never modified or deleted.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### How to Contribute

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/driveguard.git

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/
```

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Google Drive API team for comprehensive documentation
- Google Colab for providing free compute resources
- The Python community for excellent libraries

## 📞 Support

- 📧 Email: your.email@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/driveguard/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/yourusername/driveguard/discussions)

## 🗺️ Roadmap

- [ ] Web UI for easier configuration
- [ ] Incremental backup support
- [ ] Compression before upload
- [ ] Encryption support
- [ ] Cloud Function deployment option
- [ ] Scheduled backup automation
- [ ] Email notifications
- [ ] Backup verification tools

## ⭐ Star History

If you find DriveGuard useful, please consider giving it a star! ⭐

## 📊 Project Stats

![GitHub stars](https://img.shields.io/github/stars/yourusername/driveguard?style=social)
![GitHub forks](https://img.shields.io/github/forks/yourusername/driveguard?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/yourusername/driveguard?style=social)

---

**Made with ❤️ for the Google Drive community**

*DriveGuard - Because your data deserves better backup protection*
