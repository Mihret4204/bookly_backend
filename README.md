# 📚 Bookly Backend

A RESTful backend for **Bookly**, built with **FastAPI**. It provides secure authentication, book management, favorites, reviews, tags, email verification, and image uploads through a clean, scalable API.

---

## ✨ Features

- 🔐 JWT Authentication (Access & Refresh Tokens)
- 📧 Email Verification
- 📖 Book Management (CRUD)
- ❤️ Favorite Books
- ⭐ Book Reviews
- 🏷️ Tags
- 🖼️ Image Uploads
- 🐘 PostgreSQL Database
- 🔄 Alembic Database Migrations
- 📄 Interactive API Documentation (Swagger)

---

## 🛠️ Tech Stack

- FastAPI
- SQLModel / SQLAlchemy
- PostgreSQL
- Alembic
- JWT Authentication
- Redis
- Celery
- FastAPI-Mail
- Uvicorn

---

## 🚀 Live API

| Resource | Link |
|----------|------|
| Base URL | https://bookly-backend-ly2m.onrender.com |
| API Documentation | https://bookly-backend-ly2m.onrender.com/docs |

---

<img width="622" height="254" alt="image" src="https://github.com/user-attachments/assets/dd784875-e717-4a21-a3c8-bbe8c3332944" />


<img width="626" height="271" alt="image" src="https://github.com/user-attachments/assets/e52a2032-d471-42ff-a20f-0f21923a374c" />

## 🎨 Frontend Repository

https://bookly-frontend-52r3.vercel.app/

---


## 📁 Project Structure

```text
src/
├── auth/
├── books/
├── favorites/
├── reviews/
├── tags/
├── db/
├── middleware/
├── migrations/
├── templates/
├── uploads/
└── main.py
```

---

## ⚙️ Installation

### Clone the repository

```bash
git clone <repository-url>
cd bookly-backend
```

### Create a virtual environment

```bash
python -m venv .venv
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Configure environment variables

Create a `.env` file.

```env
DATABASE_URL=
JWT_SECRET_KEY=
JWT_ALGORITHM=
REDIS_URL=
MAIL_USERNAME=
MAIL_PASSWORD=
MAIL_FROM=
MAIL_PORT=
MAIL_SERVER=
MAIL_FROM_NAME=
DOMAIN=
```

### Run migrations

```bash
alembic upgrade head
```

### Start the server

```bash
uvicorn src.main:app --reload
```

---

## 📚 API Documentation

After running the server:

```
http://localhost:8000/docs
```

or

```
https://bookly-backend-ly2m.onrender.com/docs
```

---

## 🔮 Future Improvements

- Docker Support
- CI/CD Pipeline
- Unit & Integration Tests
- Rate Limiting
- API Monitoring
- Caching Improvements

---

## 👨‍💻 Author

**Mihret Tena**

GitHub: https://github.com/Mihret4204
