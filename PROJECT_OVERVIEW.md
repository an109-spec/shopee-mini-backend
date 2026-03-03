# Tổng quan cấu trúc & luồng nghiệp vụ (kèm chuyển hướng trang)

## 1) Cấu trúc thư mục hiện tại

```text
shopee-mini-backend/
├── app/
│   ├── __init__.py                # App factory, load config, init extensions, register blueprint
│   ├── cli.py                     # CLI command (init-db)
│   ├── common/
│   │   ├── __init__.py
│   │   ├── constants.py
│   │   ├── decorators.py
│   │   ├── exceptions.py
│   │   └── security/
│   │       ├── __init__.py
│   │       ├── otp.py
│   │       ├── password.py
│   │       └── permission.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── config.py              # Development/Production/Test config
│   ├── extensions/
│   │   ├── __init__.py
│   │   ├── db.py
│   │   ├── jwt.py
│   │   ├── mail.py
│   │   └── socketio.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── user.py
│   │   ├── otp.py
│   │   ├── product.py
│   │   ├── order.py
│   │   ├── cart.py
│   │   ├── payment.py
│   │   ├── voucher.py
│   │   ├── review.py
│   │   ├── shop.py
│   │   ├── flash_sale.py
│   │   ├── wishlist.py
│   │   ├── chat.py
│   │   └── audit_log.py
│   ├── modules/
│   │   ├── auth/
│   │   │   ├── __init__.py        # auth blueprint: /auth
│   │   │   ├── routes.py          # route render/redirect cho auth
│   │   │   ├── service.py
│   │   │   ├── dto.py
│   │   │   ├── validators.py
│   │   │   ├── otp_service.py
│   │   │   ├── mail_service.py
│   │   │   ├── email_service.py
│   │   │   └── sms_service.py
│   │   └── user/
│   │       ├── __init__.py        # user blueprint: /user
│   │       ├── routes.py          # user center + API profile/avatar/password/order
│   │       └── service.py
│   ├── static/
│   │   ├── css/
│   │   │   ├── base.css
│   │   │   ├── auth.css
│   │   │   └── user.css
│   │   ├── js/
│   │   │   ├── base.js
│   │   │   ├── auth.js
│   │   │   └── user.js
│   │   └── uploads/
│   │       └── avatars/
│   └── templates/
│       ├── layouts/
│       │   └── base.html
│       ├── auth/
│       │   ├── login.html
│       │   ├── register.html
│       │   ├── forgot_password.html
│       │   ├── reset_password.html
│       │   └── verify_otp.html
│       └── user/
│           └── center.html
├── migrations/
│   ├── env.py
│   ├── alembic.ini
│   ├── script.py.mako
│   └── versions/
├── scripts/
│   └── postgres_setup.sql
├── requirements.txt
├── run.py                          # Entry point Flask app
├── README.md
└── PROJECT_OVERVIEW.md             # Tài liệu này
```

---

## 2) Luồng nghiệp vụ chính (kèm chuyển hướng trang)

> Ứng dụng hiện tại là **Flask server-rendered cho màn hình auth/user center** kết hợp **API JSON** cho thao tác hồ sơ người dùng.

### 2.1 Khởi tạo app và đăng ký route
1. `run.py` gọi `create_app()`.
2. `create_app()` nạp config theo `FLASK_ENV`, init extension, rồi đăng ký 2 blueprint:
   - `auth_bp` với prefix `/auth`
   - `user_bp` với prefix `/user`

Điều này quyết định toàn bộ URL chính của giao diện:
- `/auth/login`, `/auth/register`, `/auth/forgot-password`, ...
- `/user/center`, `/user/profile`, ...

---

### 2.2 Luồng Đăng ký (Register)
**Điểm vào:** `GET /auth/register`
- Render trang `auth/register.html`.

**Submit form:** `POST /auth/register`
- Validate dữ liệu.
- Thành công: tạo user, set `session["user_id"]`.
- **Redirect:** sang `url_for("user.user_center_page")` → **`/user/center`**.
- Thất bại (trùng email/phone...): render lại `register.html` với lỗi.

**Chuyển hướng liên quan từ UI:**
- Trong `register.html` có link “Đăng nhập” → `/auth/login`.

---

### 2.3 Luồng Đăng nhập (Login)
**Điểm vào:** `GET /auth/login`
- Render trang `auth/login.html`.

**Submit form:** `POST /auth/login`
- Validate + xác thực tài khoản.
- Thành công: set `session["user_id"]`.
- **Redirect:** sang **`/user/center`**.
- Sai thông tin / bị khóa: render lại `login.html` kèm thông báo lỗi.

**Chuyển hướng liên quan từ UI:**
- Link “Quên mật khẩu?” → `/auth/forgot-password`
- Link “đăng kí” → `/auth/register`

---

### 2.4 Luồng Đăng xuất (Logout)
**Điểm vào:** `GET|POST /auth/logout`
- Xóa `session["user_id"]`.
- **Redirect:** về `url_for("auth.login")` → **`/auth/login`**.

---

### 2.5 Luồng Quên mật khẩu + OTP + Đặt lại mật khẩu

#### Bước 1: Yêu cầu OTP
**Điểm vào:** `GET /auth/forgot-password`
- Render form nhập email/sđt.

**Submit:** `POST /auth/forgot-password`
- Gọi `request_password_reset` để phát OTP qua email/SMS.
- Thành công: render lại cùng trang nhưng ở trạng thái `otp_sent=True`.
- Form ở trạng thái này submit sang `POST /auth/reset-password`.

#### Bước 2: Đặt lại mật khẩu
**Điểm vào:** `GET /auth/reset-password`
- Render `reset_password.html`.

**Submit:** `POST /auth/reset-password`
- Verify OTP + đổi mật khẩu mới.
- Thành công:
  - **Redirect:** về `url_for("auth.login")` → **`/auth/login`**.
- Thất bại:
  - Render lại `reset_password.html` với lỗi.

#### Bước 3 (route phụ): verify OTP
**`GET|POST /auth/verify-otp`**
- Cũng xử lý reset mật khẩu và khi thành công sẽ
- **Redirect:** về **`/auth/login`**.

---

### 2.6 Luồng User Center và bảo vệ đăng nhập

#### Truy cập trang user center
**`GET /user/center`**
- Nếu **chưa có** `session["user_id"]`:
  - **Redirect:** `url_for("auth.login")` → **`/auth/login`**.
- Nếu đã đăng nhập:
  - Render `user/center.html`.

#### Thao tác trong user center (AJAX)
Trang `user/center.html` tải `user.js`, sau đó gọi các API JSON:
- `GET /user/profile` (nạp hồ sơ)
- `PATCH /user/profile` (cập nhật hồ sơ)
- `POST /user/avatar/upload` (upload avatar)
- `PATCH /user/avatar` (đổi avatar bằng URL)
- `PATCH /user/password` (đổi mật khẩu)
- `GET /user/purchase-history` (xem lịch sử đơn)

Các API này **không redirect**; trả JSON để JS cập nhật giao diện hoặc báo lỗi.

---

## 3) Tóm tắt nhanh mapping chuyển hướng trang

- `/auth/register` (POST thành công) → **`/user/center`**
- `/auth/login` (POST thành công) → **`/user/center`**
- `/auth/logout` → **`/auth/login`**
- `/auth/reset-password` (POST thành công) → **`/auth/login`**
- `/auth/verify-otp` (POST thành công) → **`/auth/login`**
- `/user/center` (khi chưa login) → **`/auth/login`**