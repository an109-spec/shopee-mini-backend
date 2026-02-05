📌 Mô tả dự án (Description)

**Shopee Mini Backend** là hệ thống backend RESTful API mô phỏng các chức năng cốt lõi của một sàn thương mại điện tử, phục vụ cho đồ án tốt nghiệp.
Dự án tập trung vào việc xây dựng các API quản lý người dùng, xác thực – phân quyền, sản phẩm, đơn hàng và các nghiệp vụ liên quan, tuân theo kiến trúc backend hiện đại.
Hệ thống được thiết kế theo mô hình **client–server**, tách biệt frontend và backend, dễ mở rộng, dễ bảo trì và sẵn sàng tích hợp với các ứng dụng web hoặc mobile.

---

## 🛠 Công nghệ sử dụng

- **Python 3**
- **Flask** – Web framework
- **Flask SQLAlchemy** – ORM thao tác cơ sở dữ liệu
- **Flask-JWT-Extended** – Xác thực & phân quyền bằng JWT
- **Flask-Migrate** – Quản lý migration database
- **Flask-Mail** – Gửi email
- **MySQL / PostgreSQL**
- **Git & GitHub** – Quản lý source code

---

## ⚙️ Chức năng chính

- Đăng ký / đăng nhập người dùng
- Xác thực & phân quyền (JWT)
- Quản lý người dùng
- Quản lý sản phẩm
- Quản lý đơn hàng
- Theo dõi trạng thái đơn hàng
- API phục vụ frontend / mobile app

---

## 🚀 Hướng dẫn chạy dự án

### 1️⃣ Clone repository

git clone https://github.com/an109-spec/shopee-mini-backend.git
cd shopee-mini-backend

### 2️⃣ Tạo virtual environment

python -m venv venv
source venv/bin/activate # Linux / Mac
venv\Scripts\activate # Windows

### 3️⃣ Cài đặt thư viện

pip install -r requirements.txt

### 4️⃣ Tạo file `.env`

```env
FLASK_ENV=development
SECRET_KEY=your_secret_key
JWT_SECRET_KEY=your_jwt_secret
DATABASE_URL=your_database_url
```

### 5️⃣ Chạy ứng dụng

python run.py

API mặc định chạy tại:

http://127.0.0.1:5000

## 📁 Cấu trúc thư mục

```
DO_AN_TOT_NGHIEP/
│── app/
│   ├── models/
│   ├── routes/
│   ├── services/
│   ├── extensions/
│   └── __init__.py
│── run.py
│── requirements.txt
│── .gitignore
│── README.md
```

## 🎯 Mục tiêu đồ án

- Áp dụng kiến thức Backend Web vào dự án thực tế
- Nắm vững RESTful API, JWT, ORM
- Rèn luyện quy trình làm việc với Git/GitHub
- Sẵn sàng mở rộng thành hệ thống thương mại điện tử hoàn chỉnh
