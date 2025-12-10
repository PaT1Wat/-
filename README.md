# 📚 Manga/Novel Recommendation System

ระบบแนะนำมังงะและนิยายพร้อม Backend (FastAPI) และ Frontend (React)

---

## 📋 สารบัญ

- [ความต้องการของระบบ](#-ความต้องการของระบบ)
- [การติดตั้ง Backend](#-การติดตั้ง-backend)
- [การติดตั้ง Frontend](#-การติดตั้ง-frontend)
- [การตั้งค่า Supabase](#-การตั้งค่า-supabase)
- [การแก้ไขปัญหา](#-การแก้ไขปัญหา)

---

## 💻 ความต้องการของระบบ

| ซอฟต์แวร์ | เวอร์ชันขั้นต่ำ | ตรวจสอบด้วยคำสั่ง |
|-----------|-----------------|-------------------|
| Python | 3.10+ | `python --version` |
| Node.js | 18+ | `node --version` |
| npm | 9+ | `npm --version` |

---

## 🔧 การติดตั้ง Backend

### ขั้นตอนที่ 1: เข้าไปที่ folder backend

```bash
cd backend
```

### ขั้นตอนที่ 2: สร้าง Virtual Environment

```bash
python -m venv venv
```

**✅ ผ่าน:**
```
(ไม่มี output แสดงว่าสำเร็จ)
```

**❌ ไม่ผ่าน:**
```
'python' is not recognized as an internal or external command
```
**วิธีแก้:** ติดตั้ง Python จาก https://www.python.org/downloads/ และเลือก "Add Python to PATH"

---

### ขั้นตอนที่ 3: เปิดใช้งาน Virtual Environment

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate
```

**Windows (CMD):**
```cmd
venv\Scripts\activate.bat
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

**✅ ผ่าน:**
```
(venv) C:\Users\...\backend>
```
จะเห็น `(venv)` นำหน้า prompt

**❌ ไม่ผ่าน (PowerShell):**
```
cannot be loaded because running scripts is disabled on this system
```
**วิธีแก้:** รันคำสั่งนี้ก่อน:
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

---

### ขั้นตอนที่ 4: ติดตั้ง Dependencies

```bash
pip install -r requirements.txt
```

**✅ ผ่าน:**
```
Successfully installed fastapi-0.115.5 uvicorn-0.32.1 ...
```

**❌ ไม่ผ่าน:**
```
error: Microsoft Visual C++ 14.0 or greater is required
```
**วิธีแก้:** ติดตั้ง Visual Studio Build Tools จาก https://visualstudio.microsoft.com/visual-cpp-build-tools/

---

### ขั้นตอนที่ 5: สร้างไฟล์ .env

**Windows:**
```bash
copy .env.example .env
```

**macOS/Linux:**
```bash
cp .env.example .env
```

แก้ไขไฟล์ `.env` ใส่ค่า Supabase ของคุณ:
```env
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR...
```

---

### ขั้นตอนที่ 6: รัน Backend Server

```bash
python -m uvicorn app.main:app --reload --port 8000
```

**✅ ผ่าน:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using WatchFiles
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**❌ ไม่ผ่าน:**
```
ModuleNotFoundError: No module named 'app'
```
**วิธีแก้:** ตรวจสอบว่าอยู่ใน folder `backend` และ activate venv แล้ว

**❌ ไม่ผ่าน:**
```
ERROR: Address already in use
```
**วิธีแก้:** เปลี่ยน port หรือปิด process ที่ใช้ port 8000 อยู่:
```bash
python -m uvicorn app.main:app --reload --port 8001
```

---

### ทดสอบ Backend

เปิด browser ไปที่: http://localhost:8000

**✅ ผ่าน:**
```json
{"message":"Manga/Novel Recommendation API","version":"1.0.0","docs":"/docs"}
```

เปิด API docs: http://localhost:8000/docs

---

## ⚛️ การติดตั้ง Frontend

### ขั้นตอนที่ 1: เข้าไปที่ folder frontend

```bash
cd frontend
```

### ขั้นตอนที่ 2: ติดตั้ง Dependencies

```bash
npm install
```

**✅ ผ่าน:**
```
added 1500 packages, and audited 1501 packages in 45s
found 0 vulnerabilities
```

**❌ ไม่ผ่าน:**
```
npm ERR! code ENOENT
npm ERR! syscall open
npm ERR! path .../package.json
```
**วิธีแก้:** ตรวจสอบว่าอยู่ใน folder `frontend` ที่มีไฟล์ `package.json`

**❌ ไม่ผ่าน:**
```
npm WARN deprecated ...
```
**วิธีแก้:** นี่เป็นแค่ warning ไม่ใช่ error สามารถใช้งานได้ปกติ

---

### ขั้นตอนที่ 3: สร้างไฟล์ .env

**Windows:**
```bash
copy .env.example .env
```

**macOS/Linux:**
```bash
cp .env.example .env
```

แก้ไขไฟล์ `.env`:
```env
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_SUPABASE_URL=https://xxxxx.supabase.co
REACT_APP_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR...
```

---

### ขั้นตอนที่ 4: รัน Frontend Server

```bash
npm start
```

**✅ ผ่าน:**
```
Compiled successfully!

You can now view frontend in the browser.

  Local:            http://localhost:3000
  On Your Network:  http://192.168.x.x:3000

webpack compiled successfully
```

**❌ ไม่ผ่าน:**
```
Something is already running on port 3000.
Would you like to run the app on another port instead? (Y/n)
```
**วิธีแก้:** กด `Y` เพื่อใช้ port อื่น หรือปิด process ที่ใช้ port 3000

**❌ ไม่ผ่าน (หน้าเว็บขาว):**

เปิด Developer Tools (F12) > Console ดู error

**สาเหตุที่พบบ่อย:**
1. ไม่มีไฟล์ `.env` → สร้างไฟล์ `.env` จาก `.env.example`
2. ค่า Supabase ไม่ถูกต้อง → ตรวจสอบ URL และ Key
3. Backend ไม่ได้รัน → รัน backend ก่อน

---

## 🗄️ การตั้งค่า Supabase

### ขั้นตอนที่ 1: สร้าง Project

1. ไปที่ https://supabase.com
2. สร้าง Project ใหม่
3. รอให้ Project พร้อมใช้งาน

### ขั้นตอนที่ 2: หา API Keys

1. ไปที่ **Project Settings** > **API**
2. คัดลอก:
   - **Project URL** → ใส่ใน `SUPABASE_URL` / `REACT_APP_SUPABASE_URL`
   - **anon/public key** → ใส่ใน `SUPABASE_ANON_KEY` / `REACT_APP_SUPABASE_ANON_KEY`

### ขั้นตอนที่ 3: สร้าง Database Tables

1. ไปที่ **SQL Editor**
2. Copy เนื้อหาจาก `backend/schema.sql`
3. กด **Run**

**✅ ผ่าน:**
```
Success. No rows returned
```

---

## 🚨 การแก้ไขปัญหา

### ปัญหาทั่วไป

| ปัญหา | สาเหตุ | วิธีแก้ |
|-------|--------|--------|
| `'python' is not recognized` | ไม่ได้ติดตั้ง Python | ติดตั้ง Python และเพิ่มใน PATH |
| `'npm' is not recognized` | ไม่ได้ติดตั้ง Node.js | ติดตั้ง Node.js จาก https://nodejs.org |
| `running scripts is disabled` | PowerShell policy | รัน `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| `Address already in use` | Port ถูกใช้งานอยู่ | เปลี่ยน port หรือปิด process เดิม |
| `ModuleNotFoundError` | ไม่ได้ activate venv | Activate venv ก่อนรัน |
| หน้าเว็บขาว | ไม่มี .env หรือค่าผิด | สร้าง .env และใส่ค่าถูกต้อง |

### ตรวจสอบ Port ที่ใช้งาน

**Windows:**
```powershell
netstat -ano | findstr :3000
netstat -ano | findstr :8000
```

**macOS/Linux:**
```bash
lsof -i :3000
lsof -i :8000
```

### Kill Process ที่ใช้ Port

**Windows:**
```powershell
# ดู PID จากคำสั่ง netstat แล้วใช้
taskkill /PID <PID> /F
```

**macOS/Linux:**
```bash
kill -9 <PID>
```

---

## 📁 โครงสร้างโปรเจค

```
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app
│   │   ├── config/          # การตั้งค่า
│   │   ├── models/          # Database models
│   │   ├── routers/         # API endpoints
│   │   ├── schemas/         # Pydantic schemas
│   │   └── services/        # Business logic
│   ├── requirements.txt     # Python dependencies
│   └── schema.sql           # Database schema
│
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/           # Page components
│   │   ├── services/        # API calls
│   │   └── contexts/        # React contexts
│   └── package.json         # Node dependencies
│
└── supabase/
    └── README.md            # Supabase documentation
```

---

## 🎉 เมื่อติดตั้งสำเร็จ

เปิด 2 terminal พร้อมกัน:

**Terminal 1 - Backend:**
```bash
cd backend
.\venv\Scripts\Activate   # Windows
# source venv/bin/activate  # macOS/Linux
python -m uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```

เปิด browser:
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

---

## ✨ ฟีเจอร์

- 🔐 **การยืนยันตัวตน** - เข้าสู่ระบบด้วย Google ผ่าน Supabase Auth
- 🔍 **การค้นหา** - ค้นหาแบบ Full-text พร้อมตัวกรอง
- 📖 **เรียกดู** - ดูรายละเอียดหนังสือ คะแนน และรีวิว
- 💾 **รายการโปรด** - บันทึกหนังสือในรายการที่กำหนดเอง
- ✍️ **รีวิว** - เขียนรีวิวและให้คะแนนหนังสือ
- 🤖 **คำแนะนำ AI** - รับคำแนะนำเฉพาะบุคคลตามความชอบ
- 🌍 **รองรับหลายภาษา** - ไทย/อังกฤษ
