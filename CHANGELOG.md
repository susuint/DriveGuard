# Changelog

All notable changes to DriveGuard will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.9.1] - 2026-02-02

### Added
- Auto-detect resume mode - no manual selection needed
- Enhanced rate limit handling with 3-tier protection system
- Improved checkpoint system with granular state saving
- Better logging and error messages
- Real-time statistics during backup process
- Utility functions for state inspection (`view_state()`, `view_log()`)

### Changed
- Optimized multi-threading with auto-resource detection
- Improved manual resume workflow with clearer instructions
- Enhanced error messages for better user guidance
- Updated documentation with comprehensive examples

### Fixed
- State file corruption handling
- Memory management for large file batches
- Rate limit counter reset issues
- Timezone handling in cooldown calculations

## [1.9.0] - 2026-01-15

### Added
- Smart resume feature with automatic state detection
- Multi-threading support with configurable workers
- State management system with JSON persistence
- Comprehensive logging system
- Rate limit detection and handling
- Checkpoint system for progress preservation

### Changed
- Refactored codebase into class-based architecture
- Improved error handling throughout
- Enhanced progress tracking with tqdm

### Fixed
- Various edge cases in file handling
- Memory leaks in long-running backups

## [1.8.0] - 2025-12-01

### Added
- Initial release
- Basic recursive backup functionality
- Google Drive API integration
- Simple progress tracking

---

## Version History Summary

- **1.9.1** (2026-02-02) - Enhanced resume & rate limit handling
- **1.9.0** (2026-01-15) - Smart resume & multi-threading
- **1.8.0** (2025-12-01) - Initial release

## Upcoming Features

See [Roadmap](README.md#roadmap) in README for planned features.

## Migration Guide

### From 1.9.0 to 1.9.1

No breaking changes. State files from 1.9.0 are compatible with 1.9.1.

If upgrading:
1. Replace script file
2. Run as normal - existing state files will work
3. Enjoy improved resume detection!

### From 1.8.0 to 1.9.0

**Breaking Changes:**
- State file format changed
- Configuration moved to top of file

**Migration Steps:**
1. Complete or abandon existing 1.8.0 backups
2. Delete old state files: `backup_state.json`, `backup_log.json`
3. Update to 1.9.0
4. Reconfigure SOURCE_FOLDER_ID and BACKUP_PARENT_ID
5. Start fresh backup

---

For full documentation, see [User Guide](USER_GUIDE_EN.md).
