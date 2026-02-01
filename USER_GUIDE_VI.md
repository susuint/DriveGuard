# 📚 HƯỚNG DẪN SỬ DỤNG - CÔNG CỤ SAO LƯU GOOGLE DRIVE v1.9.1

## 📋 MỤC LỤC

1. [Giới thiệu](#giới-thiệu)
2. [Tính năng chính](#tính-năng-chính)
3. [Yêu cầu hệ thống](#yêu-cầu-hệ-thống)
4. [Cài đặt & Cấu hình](#cài-đặt--cấu-hình)
5. [Hướng dẫn sử dụng](#hướng-dẫn-sử-dụng)
6. [Tính năng nâng cao](#tính-năng-nâng-cao)
7. [Xử lý sự cố](#xử-lý-sự-cố)
8. [FAQ](#faq)
9. [Best Practices](#best-practices)

---

## 🎯 GIỚI THIỆU

### Tổng quan

**Google Drive Backup Tool v1.9.1** là công cụ tự động sao lưu dữ liệu Google Drive được thiết kế đặc biệt để xử lý các tình huống giới hạn tốc độ API của Google. Công cụ này tối ưu hóa cho việc **manual resume** - cho phép bạn dừng quá trình sao lưu và tiếp tục vào ngày hôm sau một cách tự động.

### Vấn đề giải quyết

- ✅ **Giới hạn API**: Google Drive API có giới hạn 20,000 requests/100 seconds/user
- ✅ **Sao lưu dữ liệu lớn**: Sao lưu hàng nghìn file mà không lo bị gián đoạn
- ✅ **Tự động tiếp tục**: Không cần can thiệp thủ công khi chạy lại
- ✅ **An toàn dữ liệu**: Checkpoint sau mỗi file, không lo mất tiến trình

### Điểm nổi bật

- 🚀 **Smart Resume**: Tự động phát hiện và tiếp tục từ điểm dừng
- 💾 **Checkpoint System**: Lưu trạng thái sau mỗi file thành công
- 🛡️ **Rate Limit Protection**: Xử lý thông minh khi gặp giới hạn API
- ⚡ **Multi-threading**: Tối ưu tốc độ với xử lý song song
- 📊 **Real-time Statistics**: Theo dõi tiến trình chi tiết
- 🔄 **Retry Mechanism**: Tự động thử lại các file thất bại

---

## ✨ TÍNH NĂNG CHÍNH

### 1. Sao lưu tự động & đệ quy

```
Source Folder/
├── Subfolder 1/
│   ├── File 1.pdf
│   └── File 2.docx
├── Subfolder 2/
│   └── File 3.xlsx
└── File 4.txt

→ Tự động sao lưu toàn bộ cấu trúc thư mục
```

**Đặc điểm:**
- ✅ Sao lưu đệ quy tất cả thư mục con
- ✅ Giữ nguyên cấu trúc thư mục
- ✅ Hỗ trợ mọi loại file (Office, PDF, hình ảnh, video, v.v.)
- ✅ Tự động bỏ qua file đã được sao lưu

### 2. Smart Resume - Tự động tiếp tục

**Kịch bản sử dụng:**

```
Lần chạy 1 (Ngày 1):
[==============40%==============          ] 2000/5000 files
⚠️ RATE LIMIT! → DỪNG RUNTIME

Lần chạy 2 (Ngày 2 - Sau 24h):
[                              ===========] 3000/5000 files
✅ TỰ ĐỘNG TIẾP TỤC từ file 2001!
```

**Cơ chế hoạt động:**
1. Phát hiện file `backup_state.json`
2. Kiểm tra thời gian đã qua (phải ≥ 24h)
3. Tự động load danh sách file pending/failed
4. Tiếp tục sao lưu mà không cần cấu hình

### 3. Rate Limit Protection - Bảo vệ thông minh

**Hệ thống 3 tầng:**

```
Lỗi lần 1: ⚠️ Cảnh báo - Tiếp tục
Lỗi lần 2: ⚠️⚠️ Cảnh báo nghiêm trọng - Tiếp tục  
Lỗi lần 3: 🛑 DỪNG - Lưu state - Khuyến nghị dừng runtime
```

**Hành động tự động:**
- Lưu trạng thái hiện tại
- Lưu danh sách file đang chờ
- Đặt timestamp cho lần lỗi
- Thông báo rõ ràng cần dừng runtime

### 4. Checkpoint System - Không mất tiến trình

**Lưu sau mỗi hành động:**
- ✅ Sau mỗi file download thành công
- ✅ Sau mỗi file upload thành công  
- ✅ Sau mỗi folder tạo thành công
- ✅ Sau mỗi lỗi rate limit

**File lưu trữ:**
- `backup_state.json`: Trạng thái hiện tại (pending, failed, completed)
- `backup_log.json`: Lịch sử tất cả file đã backup

### 5. Multi-threading - Tối ưu tốc độ

**Auto-detection:**
```python
Workers = min(CPU cores, RAM_GB/2, 8)

Ví dụ:
- CPU: 4 cores, RAM: 12GB → 4 workers
- CPU: 8 cores, RAM: 8GB → 4 workers  
- CPU: 16 cores, RAM: 32GB → 8 workers (max)
```

**Lợi ích:**
- ⚡ Tăng tốc 3-5 lần so với single-thread
- 💾 Tự động điều chỉnh theo tài nguyên
- 🛡️ Không gây quá tải hệ thống

### 6. Real-time Statistics - Thống kê thời gian thực

**Hiển thị:**
```
📊 Tiến trình:
[====================75%=====] 3750/5000 files

📥 Download: ✅ 3700 | ❌ 30 | ⏭️ 20
📤 Upload:   ✅ 3680 | ❌ 50

⏱️ Thời gian: 45:32 phút
🚀 Tốc độ: ~83 files/phút
```

### 7. Retry Mechanism - Thử lại thông minh

**Chiến lược:**
1. **Immediate retry**: Không retry ngay (tránh rate limit)
2. **Batch retry**: Thử lại tất cả failed files khi resume
3. **Smart skip**: Bỏ qua file đã backup thành công

**Quản lý failed files:**
```json
{
  "failed_files": [
    {"id": "file123", "name": "document.pdf", "reason": "rate_limit"},
    {"id": "file456", "name": "image.jpg", "reason": "timeout"}
  ]
}
```

---

## 💻 YÊU CẦU HỆ THỐNG

### Môi trường

| Yêu cầu | Mô tả |
|---------|-------|
| **Platform** | Google Colab (khuyến nghị) hoặc Jupyter Notebook |
| **Python** | 3.7+ |
| **RAM** | Tối thiểu 2GB, khuyến nghị 4GB+ |
| **Google Account** | Tài khoản có quyền truy cập Drive |

### Thư viện phụ thuộc

```python
google-auth>=2.0.0
google-auth-oauthlib>=0.5.0
google-auth-httplib2>=0.1.0
google-api-python-client>=2.0.0
tqdm>=4.60.0
requests>=2.25.0
psutil>=5.8.0
```

### Quyền truy cập Google Drive

- ✅ Đọc file/folder nguồn
- ✅ Tạo folder mới
- ✅ Upload file
- ✅ Liệt kê file/folder

---

## ⚙️ CÀI ĐẶT & CẤU HÌNH

### Bước 1: Lấy Folder ID

**Cách lấy Folder ID từ Google Drive:**

1. Mở Google Drive trong trình duyệt
2. Nhấp chuột phải vào folder → **Chia sẻ** → **Sao chép liên kết**
3. Link có dạng: `https://drive.google.com/drive/folders/1ABC...XYZ`
4. Lấy phần `1ABC...XYZ` (sau `/folders/`)

**Ví dụ:**
```
Link: https://drive.google.com/drive/folders/1ABCdefGHIjklMNOpqrSTUvwxYZ123456
ID:   1ABCdefGHIjklMNOpqrSTUvwxYZ123456
```

### Bước 2: Cấu hình trong code

**Mở file Python và chỉnh sửa:**

```python
# ⚠️ THAY ĐỔI 2 DÒNG NÀY
SOURCE_FOLDER_ID = '1ABC...'  # Folder cần sao lưu
BACKUP_PARENT_ID = '1XYZ...'  # Folder chứa bản sao lưu
```

**Các tùy chọn nâng cao:**

```python
# Hậu tố tên folder backup
FOLDER_SUFFIX = '_BACKUP'  # Kết quả: "MyFolder_BACKUP"

# Số luồng xử lý
MAX_WORKERS = None  # None = tự động, hoặc set số cụ thể (1-8)

# Rate limit protection
MAX_CONSECUTIVE_RATE_LIMIT_ERRORS = 3  # Dừng sau 3 lỗi liên tiếp
RATE_LIMIT_COOLDOWN_HOURS = 24  # Thời gian chờ (giờ)

# Chế độ resume
MANUAL_RESUME_MODE = True  # True = khuyến nghị dừng runtime
                           # False = tự động chờ (không khuyến nghị)
```

### Bước 3: Upload lên Google Colab

1. Truy cập [Google Colab](https://colab.research.google.com/)
2. **File** → **Upload notebook**
3. Chọn file `.py` hoặc tạo notebook mới và copy code vào

---

## 🚀 HƯỚNG DẪN SỬ DỤNG

### Quy trình cơ bản

#### **Lần chạy đầu tiên**

```
1. Mở Google Colab
2. Upload file Python
3. Chỉnh SOURCE_FOLDER_ID và BACKUP_PARENT_ID
4. Runtime → Run all
5. Cho phép quyền truy cập Google Drive
6. Đợi quá trình chạy
```

**Output mẫu:**
```
🔐 Đang xác thực với Google Drive...
✅ Xác thực thành công!

🔧 Tự động phát hiện: 4 workers (CPU: 4, RAM: 12.7GB)

⚙️  CẤU HÌNH:
📁 Source: 1ABCdefGHIjklMNOpqrSTUvwxYZ123456
📁 Backup Parent: 1XYZabcDEFghiJKLmnoPQRstUVWxyz789
🎯 Resume Mode: MANUAL (Khuyến nghị)

🆕 SAO LƯU MỚI
✅ Đã tạo folder: MyDocuments_BACKUP

📥 Đang xử lý 2458 files...
[====================75%=====] 1844/2458

⚠️  CẢNH BÁO: Đã đạt giới hạn tốc độ API!
⚠️  GIỚI HẠN TỐC ĐỘ - Lần thứ 3/3
🛑 ĐÃ ĐẠT GIỚI HẠN TỐI ĐA!

💡 KHUYẾN NGHỊ:
================================================================================
1. ✅ Trạng thái đã được lưu an toàn
2. ✅ DỪNG RUNTIME NGAY (Runtime → Disconnect and delete runtime)
3. ✅ Đợi 24 giờ
4. ✅ Khởi động lại notebook → Tự động tiếp tục
================================================================================
```

**Hành động:**
```
1. Runtime → Disconnect and delete runtime
2. Đóng trình duyệt
3. Đợi 24 giờ
```

#### **Lần chạy thứ 2 (Resume)**

```
1. Mở lại Google Colab
2. Mở cùng notebook
3. Runtime → Run all
4. Chương trình TỰ ĐỘNG RESUME!
```

**Output mẫu:**
```
🔐 Đang xác thực với Google Drive...
✅ Xác thực thành công!

📂 Đã tải trạng thái từ backup_state.json

🔄 TỰ ĐỘNG TIẾP TỤC - Phát hiện sao lưu đã bị dừng
📁 Backup folder: 1BackupFolderID
📊 Đang chờ: 614 | Thất bại: 0

🔄 Thử lại 614 files...
[====================100%====] 614/614

✅ Tiếp tục hoàn tất!

📊 Download: ✅ 2458 | ❌ 0 | ⏭️ 0
📊 Upload: ✅ 2458 | ❌ 0

⏱️ Thời gian: 18:45 phút
```

### Workflow đầy đủ

```
┌─────────────────────────────────────────────────────────────┐
│                    LẦN CHẠY ĐẦU TIÊN                        │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
                  ┌────────────────┐
                  │ Cấu hình code  │
                  │ (Folder IDs)   │
                  └────────┬───────┘
                           │
                           ▼
                  ┌────────────────┐
                  │ Chạy notebook  │
                  └────────┬───────┘
                           │
                           ▼
                  ┌────────────────┐
                  │ Xác thực Drive │
                  └────────┬───────┘
                           │
                           ▼
              ┌────────────┴──────────────┐
              │                           │
              ▼                           ▼
    ┌─────────────────┐         ┌──────────────────┐
    │ Hoàn thành OK   │         │ Gặp Rate Limit   │
    │ ✅ Thành công!  │         │ ⚠️ Cần dừng      │
    └─────────────────┘         └────────┬─────────┘
                                         │
                                         ▼
                                ┌────────────────┐
                                │ Lưu state      │
                                │ Dừng runtime   │
                                └────────┬───────┘
                                         │
                                         ▼
                                ┌────────────────┐
                                │ Đợi 24 giờ     │
                                └────────┬───────┘
                                         │
┌────────────────────────────────────────┴───────────────────┐
│                    LẦN CHẠY THỨ 2 (RESUME)                  │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
                  ┌────────────────┐
                  │ Chạy notebook  │
                  └────────┬───────┘
                           │
                           ▼
                  ┌────────────────┐
                  │ Load state     │
                  │ Tự động resume │
                  └────────┬───────┘
                           │
                           ▼
              ┌────────────┴──────────────┐
              │                           │
              ▼                           ▼
    ┌─────────────────┐         ┌──────────────────┐
    │ Hoàn thành OK   │         │ Còn rate limit   │
    │ ✅ Thành công!  │         │ ⚠️ Lặp lại       │
    └─────────────────┘         └──────────────────┘
                                         │
                                         ▼
                              (Quay lại bước đợi 24h)
```

---

## 🔧 TÍNH NĂNG NÂNG CAO

### 1. Utility Functions

**Xem trạng thái chi tiết:**
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

**Xem log sao lưu:**
```python
view_log()
```

**Output:**
```
📊 NHẬT KÝ SAO LƯU:
Tổng số files đã sao lưu: 1844
```

**Tải file về máy:**
```python
download_files()
```
- Tải `backup_state.json` và `backup_log.json` về máy
- Hữu ích để backup hoặc debug

### 2. Manual Control

**Force resume:**
```python
# Trong trường hợp cần force resume ngay cả khi chưa đủ 24h
# (Không khuyến nghị - có thể gặp lại rate limit)

# 1. Sửa state file
import json
with open('backup_state.json', 'r+') as f:
    state = json.load(f)
    state['last_rate_limit_time'] = None  # Reset thời gian
    f.seek(0)
    json.dump(state, f, indent=2)
    f.truncate()

# 2. Chạy lại notebook
```

**Reset hoàn toàn:**
```python
# Xóa tất cả state và log để bắt đầu lại từ đầu
import os

if os.path.exists('backup_state.json'):
    os.remove('backup_state.json')
    
if os.path.exists('backup_log.json'):
    os.remove('backup_log.json')

print("✅ Đã reset! Chạy lại để bắt đầu backup mới.")
```

### 3. Custom Configuration

**Sao lưu multiple folders:**
```python
# Tạo list các folder cần backup
folders_to_backup = [
    ('1ABC...', '1XYZ...'),  # (Source, Destination)
    ('1DEF...', '1UVW...'),
    ('1GHI...', '1RST...')
]

# Loop qua từng folder
for source, dest in folders_to_backup:
    SOURCE_FOLDER_ID = source
    BACKUP_PARENT_ID = dest
    
    # Tạo manager mới cho mỗi folder
    backup_manager = DriveBackupManager(
        drive_service,
        log_file=f'backup_log_{source[:8]}.json',
        state_file=f'backup_state_{source[:8]}.json',
        max_workers=MAX_WORKERS,
        manual_mode=MANUAL_RESUME_MODE
    )
    
    backup_manager.smart_backup()
```

**Tùy chỉnh naming:**
```python
# Custom folder suffix với timestamp
from datetime import datetime

FOLDER_SUFFIX = f'_BACKUP_{datetime.now().strftime("%Y%m%d")}'
# Kết quả: "MyFolder_BACKUP_20260201"
```

**Tùy chỉnh workers:**
```python
# Giảm workers nếu RAM thấp
MAX_WORKERS = 2

# Tăng workers nếu có nhiều RAM
MAX_WORKERS = 6

# Tắt multi-threading
MAX_WORKERS = 1
```

### 4. Monitoring & Logging

**Custom logging:**
```python
import logging

# Bật detailed logging
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
# Thêm vào _process_files_batch
def _process_files_batch(self, files, backup_folder_id):
    start_time = time.time()
    
    # ... existing code ...
    
    # Tính toán tốc độ
    elapsed = time.time() - start_time
    rate = len(files) / elapsed if elapsed > 0 else 0
    
    print(f"\n⚡ Tốc độ: {rate:.1f} files/giây")
    print(f"📊 Tổng thời gian: {elapsed/60:.1f} phút")
```

---

## 🔍 XỬ LÝ SỰ CỐ

### Vấn đề thường gặp

#### 1. "Authentication failed"

**Nguyên nhân:**
- Chưa cho phép quyền truy cập
- Session hết hạn

**Giải pháp:**
```python
# 1. Chạy lại cell xác thực
auth.authenticate_user()

# 2. Clear output và chạy lại toàn bộ notebook
# Runtime → Restart and run all
```

#### 2. "Folder ID not found"

**Nguyên nhân:**
- Folder ID sai
- Không có quyền truy cập folder

**Giải pháp:**
```python
# Kiểm tra folder có tồn tại không
file_info = drive_service.files().get(fileId=SOURCE_FOLDER_ID).execute()
print(file_info['name'])

# Nếu lỗi → Folder ID sai hoặc không có quyền
```

#### 3. "Rate limit even after 24h"

**Nguyên nhân:**
- Chưa đúng 24h
- Múi giờ khác nhau

**Giải pháp:**
```python
# Kiểm tra thời gian chính xác
from datetime import datetime

with open('backup_state.json', 'r') as f:
    state = json.load(f)
    last_time = datetime.fromisoformat(state['last_rate_limit_time'])
    now = datetime.now()
    hours = (now - last_time).total_seconds() / 3600
    
    print(f"Đã qua: {hours:.1f} giờ")
    print(f"Còn lại: {24 - hours:.1f} giờ")
```

#### 4. "Out of memory"

**Nguyên nhân:**
- Quá nhiều workers
- File quá lớn

**Giải pháp:**
```python
# Giảm số workers
MAX_WORKERS = 2

# Hoặc tăng RAM của Colab
# Runtime → Change runtime type → High-RAM
```

#### 5. "Upload failed - timeout"

**Nguyên nhân:**
- File quá lớn
- Kết nối không ổn định

**Giải pháp:**
```python
# Tăng timeout trong upload_file
media = MediaFileUpload(
    local_path,
    resumable=True,
    chunksize=10*1024*1024  # 10MB chunks
)

# Retry với exponential backoff
```

#### 6. "Backup incomplete but status = completed"

**Nguyên nhân:**
- Có file trong failed_files

**Giải pháp:**
```python
view_state()  # Kiểm tra failed_files

# Manually retry failed files
failed = backup_state.state.get('failed_files', [])
if failed:
    print(f"Có {len(failed)} files thất bại")
    # Chạy lại để retry
```

### Debug Mode

**Bật debug để xem chi tiết:**
```python
import logging

logging.basicConfig(level=logging.DEBUG)

# Xem tất cả API calls
logging.getLogger('googleapiclient.discovery').setLevel(logging.DEBUG)
```

### Error Recovery

**Khôi phục từ lỗi nghiêm trọng:**
```python
# 1. Backup state files
download_files()

# 2. Kiểm tra state
view_state()
view_log()

# 3. Nếu cần, edit state file manually
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

### Q1: Mất bao lâu để backup 10,000 files?

**A:** Phụ thuộc vào:
- Kích thước file (trung bình 1-5MB/file)
- Số workers (4 workers = ~80-100 files/phút)
- Rate limit (có thể cần 2-3 lần chạy)

**Ước tính:**
```
10,000 files × 1MB = ~10GB
Tốc độ: ~80 files/phút × 60 = ~4,800 files/giờ
→ Cần ~2-3 giờ (nếu không gặp rate limit)
→ Thực tế: 2-3 ngày (có rate limit)
```

### Q2: Có mất phí không?

**A:** 
- ✅ Google Colab: MIỄN PHÍ
- ✅ Google Drive API: MIỄN PHÍ (trong giới hạn)
- ⚠️ Colab Pro: $10/tháng (nhiều RAM, ít giới hạn hơn)

### Q3: Có thể backup Google Workspace files (Docs, Sheets)?

**A:** CÓ, nhưng cần export:
```python
# Export Google Docs to .docx
def export_gdoc(file_id):
    request = drive_service.files().export_media(
        fileId=file_id,
        mimeType='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )
    # ... download and upload ...
```

### Q4: Có thể schedule tự động không?

**A:** KHÔNG trực tiếp trên Colab, nhưng có thể:
- Dùng Google Cloud Functions + Scheduler
- Dùng local script + cron job
- Dùng Apps Script (giới hạn hơn)

### Q5: File duplicate được xử lý thế nào?

**A:** 
- Check theo File ID (không theo tên)
- Mỗi file chỉ backup 1 lần
- Update nếu file nguồn thay đổi (cần tùy chỉnh)

### Q6: Có thể resume từ máy khác không?

**A:** CÓ, nếu có state files:
```
1. Download backup_state.json và backup_log.json
2. Upload lên Colab mới
3. Chạy notebook → Tự động resume
```

### Q7: Xóa backup folder có ảnh hưởng không?

**A:**
- Không ảnh hưởng đến folder nguồn
- State file vẫn reference đến folder đã xóa
- Nên reset state nếu muốn backup lại

### Q8: Giới hạn của Google Drive API?

**A:**
```
- 20,000 requests per 100 seconds per user
- 1 billion requests per day (mặc định)
- 10 requests per second per user
```

### Q9: Có thể backup shared drives?

**A:** CÓ, cần thêm parameter:
```python
# Trong list_files
response = drive_service.files().list(
    q=query,
    pageSize=page_size,
    fields='nextPageToken, files(id, name, mimeType, size, parents)',
    pageToken=page_token,
    supportsAllDrives=True,  # Thêm dòng này
    includeItemsFromAllDrives=True  # Và dòng này
).execute()
```

### Q10: RAM của Colab có đủ không?

**A:**
- Colab Free: 12-13GB RAM (đủ cho hầu hết TH)
- Colab Pro: 25GB RAM
- Colab Pro+: 50GB RAM

Tool này tối ưu RAM, thường dùng <2GB.

---

## 💡 BEST PRACTICES

### 1. Chuẩn bị trước khi chạy

```
✅ Kiểm tra dung lượng Drive (đảm bảo đủ chỗ)
✅ Test với folder nhỏ trước
✅ Đọc kỹ output messages
✅ Backup state files định kỳ
✅ Đặt tên folder rõ ràng
```

### 2. Trong quá trình chạy

```
✅ Không đóng trình duyệt
✅ Không tắt máy
✅ Theo dõi output thường xuyên
✅ Sẵn sàng dừng khi có rate limit warning
```

### 3. Khi gặp rate limit

```
✅ DỪNG RUNTIME NGAY (đừng chờ)
✅ Verify state file đã được lưu
✅ Đặt reminder sau 24h
✅ Không chạy bất kỳ Drive API nào trong 24h
```

### 4. Tối ưu hiệu suất

```python
# 1. Tăng chunk size cho file lớn
chunksize=50*1024*1024  # 50MB

# 2. Giảm workers nếu nhiều file nhỏ
MAX_WORKERS = 2

# 3. Batch processing
# Xử lý 100 files một lúc thay vì hết

# 4. Sử dụng Colab Pro nếu cần
# Ít rate limit hơn, nhiều RAM hơn
```

### 5. Bảo mật

```
⚠️ KHÔNG share state files (chứa folder IDs)
⚠️ KHÔNG commit state files lên Git
⚠️ Revoke quyền truy cập sau khi xong
⚠️ Sử dụng service account cho production
```

### 6. Backup strategy

```
Ngày 1: Backup đầy đủ
Ngày 7: Incremental backup (chỉ file mới/thay đổi)
Ngày 30: Full backup mới + xóa backup cũ
```

### 7. Monitoring

```python
# Thêm notifications
def send_notification(message):
    # Discord webhook
    import requests
    webhook_url = "YOUR_DISCORD_WEBHOOK"
    requests.post(webhook_url, json={"content": message})

# Gọi khi hoàn thành hoặc gặp lỗi
send_notification("✅ Backup completed!")
```

---

## 📞 HỖ TRỢ & ĐÓNG GÓP

### Báo lỗi

Nếu gặp vấn đề:
1. Kiểm tra phần [Xử lý sự cố](#xử-lý-sự-cố)
2. Xem [FAQ](#faq)
3. Tạo issue với thông tin:
   - Output đầy đủ
   - State file (xóa sensitive info)
   - Các bước đã làm

### Đóng góp

Contributions welcome!
- Báo bugs
- Đề xuất tính năng
- Cải thiện documentation
- Submit pull requests

### License

MIT License - Sử dụng tự do cho mục đích cá nhân và thương mại.

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

**Chúc bạn sao lưu thành công! 🎉**

*Cập nhật lần cuối: 02/02/2026*
