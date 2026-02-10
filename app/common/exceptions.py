class AppException(Exception):
    """Base exception cho toàn hệ thống"""
    status_code = 400
#Server không thể hoặc sẽ không xử lý yêu cầu do lỗi từ phía người dùng (Client).
    message = "Application error"

    def __init__(self, message=None, status_code=None):
#Cho phép:
#Truyền & ghi đè message, status code tùy ý

        self.message = message if message is not None else self.message
        self.status_code = status_code if status_code is not None else self.status_code
        super().__init__(self.message)


class ValidationError(AppException):
    status_code = 422
    message = "Validation error"#Lỗi xác thực dữ liệu
#dữ liệu client gửi không hợp lệ
#Bạn bỏ trống ô "Số điện thoại" hoặc nhập email thiếu ký tự @
class UnauthorizedError(AppException):
    status_code = 401
    message = "Unauthorized"#Không có quyền truy cập
#Người dùng chưa đăng nhập
#Token không tồn tại / hết hạn

class ForbiddenError(AppException):
    status_code = 403
    message = "Forbidden"#Bị cấm truy cập
#Đã đăng nhập nhưng không có quyền

class NotFoundError(AppException):
    status_code = 404
    message = "Resource not found"
#Không tìm thấy tài nguyên

class ConflictError(AppException):
    status_code = 409
    message = "Conflict"
#Xung đột dữ liệu
#Ví dụ:
#Email đã tồn tại
#Username bị trùng

class AppExceptions(Exception):
    message="application error"
    status_code=400
    def __init__(self, message=None, status_code=None):
        self.message=message if message is not None else self.message
        self.status_code=status_code if status_code is not None else self.status_code
#với giá trị rỗng hoặc số 0 thì if vẫn mặc định là none => kiểm tra None một cách trực tiếp is not None
        super().__init__(self.message)

class ValidationError(AppException):
    message="validation error"
    status_code=422

