🇻🇳 BẢN 1: TIẾNG VIỆT
Tên file gợi ý: HUONG_DAN_SU_DUNG_VIETNAMESE.md

Hướng dẫn sử dụng Google Drive Backup Tool v1.9.1
Phiên bản: 1.9.1 FINAL (Manual Resume Optimized)
Ngày phát hành: February 02, 2026

📖 Giới thiệu
Google Drive Backup Tool là một công cụ mạnh mẽ chạy trên Google Colab, được thiết kế để sao lưu toàn bộ thư mục từ Google Drive này sang thư mục khác một cách tự động, an toàn và hiệu quả.

Điểm đặc biệt nhất của phiên bản v1.9.1 là khả năng Manual Resume tối ưu, giúp bạn vượt qua giới hạn Rate Limit (Quá mức giới hạn truy cập) của Google mà không bị mất dữ liệu hay phải cấu hình lại từ đầu.

✨ Tính năng nổi bật (Key Features)
🔄 Smart Resume (Tự động khôi phục): Tự động phát hiện trạng thái backup bị gián đoạn và tiếp tục chạy mà không cần thiết lập thủ công.
🛡️ Xử lý Rate Limit chuyên nghiệp: Thay vì chờ đợi vô tận, công cụ sẽ hướng dẫn bạn dừng Runtime an toàn và tiếp tục sau 24 giờ.
📁 Backup Đệ quy (Recursive): Tự động sao lưu toàn bộ cấu trúc thư mục con và file nằm sâu bên trong.
🔐 Kiểm tra tính toàn vẹn: Hỗ trợ kiểm tra MD5 và kích thước file để đảm bảo dữ liệu sao lưu chính xác 100%.
🚀 Tối ưu hiệu năng: Tự động phát hiện số lượng worker (luồng xử lý) dựa trên CPU và RAM của môi trường Colab.
💾 Checkpointing: Lưu trạng thái sau mỗi file thành công, đảm bảo không bị mất tiến độ khi sự cố xảy ra.
⚙️ Cấu hình & Cài đặt (Setup)
1. Lấy ID thư mục
Trước khi chạy, bạn cần chuẩn bị ID của 2 thư mục:

Thư mục Nguồn (Source): Thư mục bạn muốn sao lưu.
Thư mục Đích (Destination): Nơi sẽ chứa thư mục backup.
Cách lấy ID: Mở thư mục trên Google Drive -> Xem đường dẫn trên thanh địa chỉ. Phần chuỗi ký tự dài nằm giữa /folders/ và / là ID.
Ví dụ: https://drive.google.com/drive/folders/1A2B3C4D5E... -> ID là 1A2B3C4D5E...
2. Chỉnh sửa mã nguồn
Trong phần BƯỚC 3: CẤU HÌNH CHÍNH của mã nguồn, hãy thay thế các giá trị sau:

# 📁 FOLDER IDs (BẮT BUỘC - THAY THẾ ID CỦA BẠN VÀO ĐÂY)SOURCE_FOLDER_ID = 'ĐÁNH_ID_THƯ_MỤC_NGUỒN_VÀO_ĐÂY'BACKUP_PARENT_ID = 'ĐÁNH_ID_THƯ_MỤC_ĐÍCH_VÀO_ĐÂY'# 🏷️  Đuôi tên thư mục backup (Tùy chọn)FOLDER_SUFFIX = '_BACKUP' # Tên thư mục backup sẽ là "TênGốc_BACKUP"
🚀 Hướng dẫn sử dụng (Workflow)
Quy trình chuẩn (Khuyến nghị)
Chạy tất cả các ô (Run All): Nhấn menu Runtime -> Run all.
Xác thực: Chấp nhận quyền truy cập Google Drive khi được hỏi.
Giám sát: Theo dõi tiến trình trên màn hình.
🛑 Xử lý khi gặp lỗi "Rate Limit" (Quan trọng)
Công cụ được thiết kế để đối phó với lỗi 403: userRateLimitExceeded.

Khi gặp lỗi này liên tiếp 3 lần, chương trình sẽ tự động dừng và thông báo.
Làm theo hướng dẫn trên màn hình:
DỪNG RUNTIME NGAY: Runtime -> Disconnect and delete runtime.
ĐÓNG TAB: Bạn có thể tắt trình duyệt.
Đợi 24h: Google sẽ reset giới hạn truy cập sau 24 giờ.
Khởi động lại:
Mở lại notebook.
Nhấn Run All một lần nữa.
Chương trình sẽ TỰ ĐỘNG NHẬN DIỆN rằng bạn đang tiếp tục, bỏ qua các file đã xong và xử lý các file còn lại.
⚡ Tính năng Nâng cao (Advanced Features)
1. Manual Resume Mode
Mặc định là True. Đây là chế độ an toàn nhất.

True: Khi gặp giới hạn, công cụ sẽ báo bạn dừng Runtime (để bảo vệ tài khoản).
False: Công cụ sẽ tự động thử lại (không khuyến nghị vì có thể làm khóa tài khoản lâu hơn).
2. Quản lý Worker (Luồng xử lý)
Công cụ tự động tính toán số lượng worker tối ưu dựa trên RAM trống. Tuy nhiên, bạn có thể ép buộc bằng cách sửa dòng:

python

MAX_WORKERS = None # None = Tự động, hoặc nhập số cụ thể (ví dụ: 4)
3. File Log & State
Hệ thống tạo ra 2 file quan trọng trong Colab:

backup_state.json: Chứa trạng thái hiện tại (file đang chờ, file lỗi, thời gian). Không được xóa file này nếu bạn muốn resume.
backup_log.json: Chứa lịch sử các file đã backup thành công.
🛠️ Tiện ích & Debug (Utilities)
Sau khi chạy xong hoặc khi cần kiểm tra, bạn có thể sử dụng các lệnh sau ở ô code cuối cùng:

view_state(): Xem chi tiết trạng thái backup (số file chờ, file lỗi, thời gian).
view_log(): Xem tổng số file đã backup thành công.
download_files(): Tải file state.json và log.json về máy tính cá nhân để lưu trữ.
❓ Hỏi đáp (Q&A)
Q1: Tôi có thể tắt trình duyệt khi đang backup không?
A: Có, nhưng hãy đảm bảo bạn đã để tab Colab mở và không để máy tính ngủ. Tuy nhiên, cách an toàn nhất là nếu bạn phải đi vắng, hãy để nó chạy đến khi gặp giới hạn Rate Limit, làm theo hướng dẫn "Dừng Runtime" và quay lại sau 24h.

Q2: Tại sao phải dừng Runtime thay vì để nó tự retry?
A: Khi Google chặn truy cập (Rate Limit), việc cố gắng gửi liên tiếp sẽ khiến thời gian bị khóa lâu hơn hoặc đánh dấu IP của bạn là nghi vấn. Việc dừng Runtime và đợi 24h là cách "manual reset" an toàn nhất do chính quy định của Google khuyến nghị cho việc sao lưu hàng loạt.

Q3: Làm sao để biết file nào đã bị lỗi?
A: Chạy lệnh view_state(). Các file bị lỗi sẽ nằm trong danh sách failed_files. Khi Resume, chương trình sẽ tự động thử lại các file này.

Q4: Tôi có thể đổi thư mục đích giữa chừng không?
A: Không nên. Thay đổi ID thư mục đích sẽ khiến chức năng Resume không hoạt động đúng vì chương trình không tìm thấy các file đã backup cũ. Nếu muốn đổi, hãy xóa file backup_state.json để bắt đầu lại từ đầu.

Q5: Chương trình có hỗ trợ Google Doc/Sheet không?
A: Hiện tại chương trình tập trung vào file nhị phân (Video, Ảnh, Zip, PDF...). Các file Google Docs/Sheets khi export sẽ có định dạng khác, chương trình sẽ cố gắng download nhưng có thể cần cấu hình thêm để export về PDF/Docx tùy vào API.
