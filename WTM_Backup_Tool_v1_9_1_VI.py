# -*- coding: utf-8 -*-
"""
================================================================================
    CÔNG CỤ SAO LƯU GOOGLE DRIVE v1.9.1 - TỰ ĐỘNG TIẾP TỤC
    Tối ưu cho Manual Resume - Dừng runtime và chạy lại ngày hôm sau
================================================================================

PHIÊN BẢN: 1.9.1 FINAL
NGÀY CẬP NHẬT: 02/02/2026

QUY TRÌNH KHUYẾN NGHỊ:
1. Chạy sao lưu bình thường
2. Nếu gặp giới hạn tốc độ → DỪNG RUNTIME NGAY (Runtime → Disconnect and delete runtime)
3. Đợi 24 giờ
4. Khởi động lại notebook → Chương trình TỰ ĐỘNG TIẾP TỤC

TÍNH NĂNG NỔI BẬT v1.9.1:
✅ Tự động phát hiện chế độ tiếp tục (không cần chọn thủ công)
✅ Thông báo rõ ràng khi nên dừng runtime
✅ Checkpoint sau mỗi file thành công
✅ Smart resume - tự động phát hiện trạng thái
✅ Khuyến nghị DỪNG RUNTIME thay vì chờ đợi

================================================================================
"""

# ============================================================
# BƯỚC 1: CÀI ĐẶT THƯ VIỆN
# ============================================================

print("📦 Đang cài đặt thư viện cần thiết...")
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

print("✅ Hoàn tất cài đặt thư viện!\n")


# ============================================================
# BƯỚC 2: IMPORT THƯ VIỆN
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

# Thanh tiến trình
from tqdm.notebook import tqdm

# Giám sát hệ thống
import psutil

# Tắt cảnh báo
logging.getLogger('google_auth_httplib2').setLevel(logging.ERROR)


# ============================================================
# ⚙️  BƯỚC 3: CẤU HÌNH CHÍNH - CHỈNH SỬA Ở ĐÂY
# ============================================================

# 📁 FOLDER IDs (BẮT BUỘC PHẢI THAY ĐỔI)
# Hướng dẫn: Nhấp chuột phải vào folder → Chia sẻ → Sao chép liên kết
# Link có dạng: https://drive.google.com/drive/folders/ABC123XYZ
# Lấy phần ABC123XYZ làm FOLDER_ID

SOURCE_FOLDER_ID = '1ABCdefGHIjklMNOpqrSTUvwxYZ123456'  # ⚠️ THAY ĐỔI: Folder nguồn cần sao lưu
BACKUP_PARENT_ID = '1XYZabcDEFghiJKLmnoPQRstUVWxyz789'  # ⚠️ THAY ĐỔI: Folder đích chứa bản sao lưu

# 🏷️  Hậu tố tên folder
FOLDER_SUFFIX = '_BACKUP'

# 🚀 Số luồng xử lý song song
MAX_WORKERS = None  # Tự động phát hiện (khuyến nghị)

# 🛡️  Bảo vệ giới hạn tốc độ
MAX_CONSECUTIVE_RATE_LIMIT_ERRORS = 3   # Dừng sau 3 lỗi liên tiếp
RATE_LIMIT_COOLDOWN_HOURS = 24          # Thời gian chờ 24 giờ

# 📝 Tên file lưu trữ
LOG_FILE = 'backup_log.json'
STATE_FILE = 'backup_state.json'

# 🎯 CHẾ ĐỘ TIẾP TỤC THỦ CÔNG (Mặc định)
# True = Đề xuất DỪNG RUNTIME khi gặp giới hạn tốc độ (KHUYẾN NGHỊ)
# False = Tự động thử lại (không khuyến nghị)
MANUAL_RESUME_MODE = True

print("="*80)
print("⚙️  CẤU HÌNH HỆ THỐNG:")
print("="*80)
print(f"📁 Folder nguồn: {SOURCE_FOLDER_ID}")
print(f"📁 Folder đích: {BACKUP_PARENT_ID}")
print(f"🎯 Chế độ tiếp tục: {'THỦ CÔNG (Khuyến nghị)' if MANUAL_RESUME_MODE else 'TỰ ĐỘNG'}")
print("="*80 + "\n")


# ============================================================
# BƯỚC 4: XÁC THỰC GOOGLE DRIVE
# ============================================================

print("🔐 Đang xác thực với Google Drive...")
auth.authenticate_user()
creds, _ = default()
drive_service = build('drive', 'v3', credentials=creds)
print("✅ Xác thực thành công!\n")


# ============================================================
# BƯỚC 5: ĐỊNH NGHĨA CÁC LỚP XỬ LÝ
# ============================================================

class BackupState:
    """Quản lý trạng thái sao lưu với tính năng tiếp tục thủ công tối ưu"""
    
    def __init__(self, state_file='backup_state.json'):
        self.state_file = state_file
        self.state = self.load_state()
    
    def load_state(self):
        """Tải trạng thái từ file"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                    print(f"📂 Đã tải trạng thái từ {self.state_file}")
                    return state
            except:
                print(f"⚠️  Không thể tải trạng thái, tạo mới...")
        
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
        """Lưu trạng thái - Checkpoint sau mỗi thay đổi"""
        self.state['updated_at'] = datetime.now().isoformat()
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)
    
    def update(self, **kwargs):
        """Cập nhật và lưu ngay lập tức"""
        self.state.update(kwargs)
        self.save_state()
    
    def can_resume(self):
        """Kiểm tra xem có thể tiếp tục không"""
        if self.state['last_rate_limit_time']:
            try:
                last_error = datetime.fromisoformat(self.state['last_rate_limit_time'])
                now = datetime.now()
                hours_passed = (now - last_error).total_seconds() / 3600
                
                if hours_passed < RATE_LIMIT_COOLDOWN_HOURS:
                    remaining = RATE_LIMIT_COOLDOWN_HOURS - hours_passed
                    next_time = last_error + timedelta(hours=RATE_LIMIT_COOLDOWN_HOURS)
                    
                    print(f"\n⏰ CẦN ĐỢI THÊM {remaining:.1f} GIỜ")
                    print(f"🕐 Thử lại sau: {next_time.strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"💡 Khuyến nghị: Đợi đủ thời gian rồi khởi động lại notebook\n")
                    return False
            except:
                pass
        
        return True
    
    def reset_rate_limit_counter(self):
        """Đặt lại bộ đếm giới hạn tốc độ"""
        self.state['consecutive_rate_limit_errors'] = 0
        self.save_state()
    
    def increment_rate_limit_error(self):
        """Tăng bộ đếm lỗi giới hạn tốc độ"""
        self.state['consecutive_rate_limit_errors'] += 1
        self.state['last_rate_limit_time'] = datetime.now().isoformat()
        self.save_state()
        return self.state['consecutive_rate_limit_errors']
    
    def should_auto_resume(self):
        """Kiểm tra xem có nên tự động tiếp tục không"""
        # Nếu trạng thái = đã tạm dừng và đã qua 24 giờ
        if self.state['status'] == 'paused':
            if self.can_resume():
                return True
        return False


class DriveBackupManager:
    """Trình quản lý sao lưu tối ưu cho chế độ tiếp tục thủ công"""
    
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
        """Tự động phát hiện số luồng tối ưu"""
        cpu_count = multiprocessing.cpu_count()
        available_memory_gb = psutil.virtual_memory().available / (1024**3)
        
        # Công thức tối ưu: min(CPU cores, available_memory_GB / 2, 8)
        optimal_workers = min(cpu_count, int(available_memory_gb / 2), 8)
        optimal_workers = max(1, optimal_workers)  # Tối thiểu 1 worker
        
        print(f"🔧 Tự động phát hiện: {optimal_workers} workers (CPU: {cpu_count}, RAM: {available_memory_gb:.1f}GB)")
        return optimal_workers
    
    def load_log(self):
        """Tải nhật ký sao lưu"""
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    log = json.load(f)
                    print(f"📂 Đã tải log từ {self.log_file}")
                    return log
            except:
                print("⚠️  Không thể tải log, tạo mới...")
        
        return {
            'backed_up_files': {},
            'last_run': None
        }
    
    def save_log(self):
        """Lưu nhật ký sao lưu"""
        self.backup_log['last_run'] = datetime.now().isoformat()
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(self.backup_log, f, indent=2, ensure_ascii=False)
    
    def get_file_info(self, file_id):
        """Lấy thông tin file/folder"""
        try:
            return self.service.files().get(
                fileId=file_id,
                fields='id, name, mimeType, size, parents'
            ).execute()
        except HttpError as e:
            print(f"❌ Lỗi lấy thông tin: {e}")
            return None
    
    def list_files(self, folder_id, page_size=1000):
        """Liệt kê tất cả files trong folder"""
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
                print("\n⚠️  CẢNH BÁO: Đã đạt giới hạn tốc độ API!")
                self._handle_rate_limit()
            else:
                print(f"❌ Lỗi liệt kê files: {e}")
            return []
    
    def create_folder(self, folder_name, parent_id):
        """Tạo folder mới"""
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
            
            print(f"✅ Đã tạo folder: {folder_name}")
            return folder.get('id')
        except HttpError as e:
            if e.resp.status == 429:
                print("\n⚠️  CẢNH BÁO: Đã đạt giới hạn tốc độ API!")
                self._handle_rate_limit()
            else:
                print(f"❌ Lỗi tạo folder: {e}")
            return None
    
    def _handle_rate_limit(self):
        """Xử lý khi gặp giới hạn tốc độ"""
        error_count = self.backup_state.increment_rate_limit_error()
        
        print(f"\n{'='*80}")
        print(f"⚠️  GIỚI HẠN TỐC ĐỘ - Lần thứ {error_count}/{MAX_CONSECUTIVE_RATE_LIMIT_ERRORS}")
        print(f"{'='*80}")
        
        if error_count >= MAX_CONSECUTIVE_RATE_LIMIT_ERRORS:
            print("\n🛑 ĐÃ ĐẠT GIỚI HẠN TỐI ĐA!")
            
            if self.manual_mode:
                print("\n💡 KHUYẾN NGHỊ:")
                print("="*80)
                print("1. ✅ Trạng thái đã được lưu an toàn")
                print("2. ✅ DỪNG RUNTIME NGAY (Runtime → Disconnect and delete runtime)")
                print("3. ✅ Đợi 24 giờ")
                print("4. ✅ Khởi động lại notebook → Tự động tiếp tục")
                print("="*80)
                
                # Lưu trạng thái tạm dừng
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
                print(f"\n⏰ Đợi {RATE_LIMIT_COOLDOWN_HOURS} giờ rồi thử lại...")
                time.sleep(RATE_LIMIT_COOLDOWN_HOURS * 3600)
    
    def download_file(self, file_id, file_name, local_path):
        """Tải file từ Drive"""
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
                print(f"❌ Lỗi tải file {file_name}: {e}")
                self.download_stats['failed'] += 1
                return False
        except Exception as e:
            print(f"❌ Lỗi không xác định: {e}")
            self.download_stats['failed'] += 1
            return False
    
    def upload_file(self, local_path, file_name, parent_id):
        """Tải file lên Drive"""
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
                print(f"❌ Lỗi upload file {file_name}: {e}")
                self.upload_stats['failed'] += 1
                return None
        except Exception as e:
            print(f"❌ Lỗi không xác định: {e}")
            self.upload_stats['failed'] += 1
            return None
    
    def _process_single_file(self, file_item, backup_folder_id):
        """Xử lý một file đơn lẻ"""
        if self.should_stop:
            return None
        
        file_id = file_item['id']
        file_name = file_item['name']
        
        # Kiểm tra đã backup chưa
        if file_id in self.backup_log['backed_up_files']:
            self.download_stats['skipped'] += 1
            return None
        
        # Tạo đường dẫn local tạm thời
        local_path = os.path.join(self.local_temp_dir, file_name)
        
        # Tải file xuống
        if not self.download_file(file_id, file_name, local_path):
            return {'id': file_id, 'name': file_name, 'status': 'failed'}
        
        # Upload lên folder backup
        new_file_id = self.upload_file(local_path, file_name, backup_folder_id)
        
        # Xóa file local
        try:
            os.remove(local_path)
        except:
            pass
        
        if new_file_id:
            # Lưu vào log ngay lập tức
            with self.log_lock:
                self.backup_log['backed_up_files'][file_id] = {
                    'name': file_name,
                    'type': 'file',
                    'backup_id': new_file_id,
                    'backup_time': datetime.now().isoformat()
                }
                self.save_log()
            
            # Cập nhật state
            with self.state_lock:
                self.backup_state.state['total_files_processed'] += 1
                self.backup_state.save_state()
            
            return {'id': file_id, 'name': file_name, 'status': 'success'}
        else:
            return {'id': file_id, 'name': file_name, 'status': 'failed'}
    
    def _process_files_batch(self, files, backup_folder_id):
        """Xử lý batch files với đa luồng"""
        if not files or self.should_stop:
            return
        
        print(f"\n📥 Đang xử lý {len(files)} files...")
        
        # Lưu batch hiện tại
        self.current_batch = files
        
        failed_files = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            with tqdm(total=len(files), desc="Tiến trình") as pbar:
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
                        print(f"❌ Lỗi xử lý: {e}")
                        failed_files.append(futures[future])
                    
                    pbar.update(1)
                    
                    # Dọn dẹp bộ nhớ
                    if pbar.n % 10 == 0:
                        gc.collect()
        
        # Lưu failed files vào state
        if failed_files:
            with self.state_lock:
                current_failed = self.backup_state.state.get('failed_files', [])
                current_failed.extend(failed_files)
                self.backup_state.update(failed_files=current_failed)
    
    def _backup_folder_recursive(self, source_folder_id, backup_folder_id):
        """Sao lưu folder đệ quy"""
        if self.should_stop:
            return
        
        # Lấy danh sách items
        items = self.list_files(source_folder_id)
        
        if not items:
            return
        
        # Phân loại
        folders = [i for i in items if i['mimeType'] == 'application/vnd.google-apps.folder']
        files = [i for i in items if i['mimeType'] != 'application/vnd.google-apps.folder']
        
        # Xử lý folders trước
        for folder_item in folders:
            if self.should_stop:
                break
            
            item_id = folder_item['id']
            item_name = folder_item['name']
            
            if item_id in self.backup_log['backed_up_files']:
                continue
            
            print(f"\n📁 Đang xử lý: {item_name}")
            new_folder_id = self.create_folder(item_name, backup_folder_id)
            
            if new_folder_id:
                self._backup_folder_recursive(item_id, new_folder_id)
                
                with self.log_lock:
                    self.backup_log['backed_up_files'][item_id] = {
                        'name': item_name,
                        'type': 'folder',
                        'backup_time': datetime.now().isoformat()
                    }
        
        # Xử lý files
        if files and not self.should_stop:
            self._process_files_batch(files, backup_folder_id)
    
    def smart_backup(self):
        """
        SAO LƯU THÔNG MINH - Tự động phát hiện và tiếp tục
        Không cần chọn chế độ thủ công
        """
        
        # Kiểm tra có trạng thái tạm dừng không
        if self.backup_state.state['status'] == 'paused':
            if not self.backup_state.can_resume():
                print("\n⏰ Chưa đủ 24 giờ để tiếp tục")
                print("💡 Hãy quay lại sau\n")
                return None
            
            # Tự động tiếp tục
            print("\n" + "="*80)
            print("🔄 TỰ ĐỘNG TIẾP TỤC - Phát hiện sao lưu đã bị dừng")
            print("="*80)
            
            backup_folder_id = self.backup_state.state.get('backup_folder_id')
            
            if not backup_folder_id:
                print("❌ Không tìm thấy ID folder sao lưu")
                return None
            
            print(f"📁 Folder sao lưu: {backup_folder_id}")
            
            pending = self.backup_state.state.get('pending_files', [])
            failed = self.backup_state.state.get('failed_files', [])
            
            print(f"📊 Đang chờ: {len(pending)} | Thất bại: {len(failed)}")
            
            all_retry = pending + failed
            
            if all_retry:
                print(f"\n🔄 Thử lại {len(all_retry)} files...")
                self._process_files_batch(all_retry, backup_folder_id)
                
                if not self.should_stop:
                    self.backup_state.update(
                        pending_files=[],
                        failed_files=[],
                        status='completed'
                    )
                    print("\n✅ Tiếp tục hoàn tất!")
            else:
                print("\n✅ Không có file cần thử lại!")
                self.backup_state.update(status='completed')
            
            return backup_folder_id
        
        # Sao lưu mới
        print("\n" + "="*80)
        print("🆕 SAO LƯU MỚI")
        print("="*80)
        
        source_info = self.get_file_info(SOURCE_FOLDER_ID)
        if not source_info:
            print("❌ Không thể lấy thông tin folder nguồn")
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
            print(f"\n⏸️  SAO LƯU BỊ DỪNG")
        else:
            self.backup_state.update(status='completed')
            print(f"\n✅ HOÀN TẤT SAO LƯU!")
        
        print(f"\n📊 Tải xuống: ✅ {self.download_stats['success']} | "
              f"❌ {self.download_stats['failed']} | ⏭️ {self.download_stats['skipped']}")
        print(f"📊 Tải lên: ✅ {self.upload_stats['success']} | ❌ {self.upload_stats['failed']}")
        
        return backup_folder_id
    
    def get_backup_stats(self):
        """Hiển thị thống kê sao lưu"""
        total = len(self.backup_log['backed_up_files'])
        files = sum(1 for i in self.backup_log['backed_up_files'].values() if i['type'] == 'file')
        folders = sum(1 for i in self.backup_log['backed_up_files'].values() if i['type'] == 'folder')
        
        print("\n" + "="*80)
        print("📊 THỐNG KÊ SAO LƯU")
        print("="*80)
        print(f"Tổng số: {total} | Files: {files} | Folders: {folders}")
        print(f"Lần chạy cuối: {self.backup_log.get('last_run', 'Chưa có')}")
        print(f"Trạng thái: {self.backup_state.state['status']}")
        
        if self.backup_state.state.get('pending_files'):
            print(f"Đang chờ: {len(self.backup_state.state['pending_files'])}")
        if self.backup_state.state.get('failed_files'):
            print(f"Thất bại: {len(self.backup_state.state['failed_files'])}")
        
        print("="*80 + "\n")


# ============================================================
# BƯỚC 6: KHỞI TẠO & CHẠY SAO LƯU
# ============================================================

print("🔧 Khởi tạo Trình quản lý sao lưu...")
backup_manager = DriveBackupManager(
    drive_service,
    log_file=LOG_FILE,
    state_file=STATE_FILE,
    max_workers=MAX_WORKERS,
    manual_mode=MANUAL_RESUME_MODE
)

# Hiển thị thống kê hiện tại
backup_manager.get_backup_stats()

# ============================================================
# 🚀 CHẠY SAO LƯU - TỰ ĐỘNG THÔNG MINH
# ============================================================

print("\n" + "="*80)
print("🎯 QUY TRÌNH KHUYẾN NGHỊ:")
print("="*80)
print("1. Chạy sao lưu bình thường")
print("2. Nếu gặp giới hạn tốc độ → DỪNG RUNTIME")
print("3. Đợi 24 giờ")
print("4. Khởi động lại notebook → TỰ ĐỘNG TIẾP TỤC")
print("="*80 + "\n")

print("🚀 BẮT ĐẦU SAO LƯU...")
start_time = time.time()

# SAO LƯU THÔNG MINH - Tự động phát hiện tiếp tục hoặc sao lưu mới
backup_folder_id = backup_manager.smart_backup()

end_time = time.time()

# ============================================================
# KẾT QUẢ
# ============================================================

if backup_folder_id:
    duration = end_time - start_time
    print(f"\n✅ THÀNH CÔNG!")
    print(f"⏱️  Thời gian: {duration:.2f}s ({duration/60:.2f} phút)")
    print(f"📁 ID Folder sao lưu: {backup_folder_id}")
    print(f"🔗 Liên kết: https://drive.google.com/drive/folders/{backup_folder_id}")
    
    backup_manager.get_backup_stats()
elif backup_manager.should_stop:
    print(f"\n💡 CÁC BƯỚC TIẾP THEO:")
    print("="*80)
    print("✅ Trạng thái đã được lưu an toàn")
    print("✅ DỪNG RUNTIME NGAY (Runtime → Disconnect)")
    print("✅ Đợi 24 giờ")
    print("✅ Mở lại notebook → Chạy lại → Tự động tiếp tục")
    print("="*80 + "\n")
else:
    print("\n❌ SAO LƯU THẤT BẠI!")

# ============================================================
# TIỆN ÍCH BỔ SUNG
# ============================================================

def view_state():
    """Xem trạng thái sao lưu"""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            state = json.load(f)
            print("\n📊 TRẠNG THÁI SAO LƯU:")
            print(json.dumps(state, indent=2, ensure_ascii=False))

def view_log():
    """Xem nhật ký sao lưu"""
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as f:
            log = json.load(f)
            print(f"\n📊 NHẬT KÝ SAO LƯU:")
            print(f"Tổng số files đã sao lưu: {len(log['backed_up_files'])}")

def download_files():
    """Tải các file trạng thái và nhật ký về máy"""
    from google.colab import files
    for filename in [STATE_FILE, LOG_FILE]:
        if os.path.exists(filename):
            files.download(filename)
            print(f"✅ Đã tải: {filename}")

print("""
================================================================================
                        TIỆN ÍCH BỔ SUNG
================================================================================

view_state()      # Xem trạng thái sao lưu chi tiết
view_log()        # Xem nhật ký sao lưu
download_files()  # Tải các file state + log về máy

================================================================================
""")
