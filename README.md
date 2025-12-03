# ระบบแนะนำมังงะ/นิยาย

เว็บแอปพลิเคชันแบบ Full-stack สำหรับค้นหา รีวิว และรับคำแนะนำมังงะ นิยาย ไลท์โนเวล มันฮวา และมันฮัว แบบเฉพาะบุคคล

## ฟีเจอร์

### ฟีเจอร์สำหรับผู้ใช้
- 🔐 **การยืนยันตัวตน** - เข้าสู่ระบบด้วย Google ผ่าน Firebase
- 🔍 **การค้นหา** - ค้นหาแบบ Full-text พร้อมตัวกรอง (ประเภท, สถานะ, แท็ก, คะแนน, ปี)
- 📖 **เรียกดู** - ดูรายละเอียดหนังสือ คะแนน และรีวิว
- 💾 **รายการโปรด** - บันทึกหนังสือในรายการที่กำหนดเอง (รายการโปรด, กำลังอ่าน, อ่านจบแล้ว, วางแผนจะอ่าน, เลิกอ่าน)
- ✍️ **รีวิว** - เขียนรีวิวและให้คะแนนหนังสือ ทำเครื่องหมายรีวิวที่มีประโยชน์
- 🤖 **คำแนะนำ** - รับคำแนะนำเฉพาะบุคคลตามความชอบของคุณ

### ฟีเจอร์สำหรับผู้ดูแลระบบ
- 📚 จัดการหนังสือ (การดำเนินการ CRUD)
- 👤 จัดการนักเขียน
- 🏢 จัดการสำนักพิมพ์
- ✅ ตรวจสอบรีวิว (อนุมัติ/ปฏิเสธ)

### ฟีเจอร์ทางเทคนิค
- 🌍 **รองรับภาษาไทย** - รองรับ i18n สำหรับภาษาไทยและภาษาอังกฤษ
- 📱 **ออกแบบ Responsive** - ใช้งานได้บนเดสก์ท็อป แท็บเล็ต และมือถือ
- ⚡ **คำแนะนำจาก AI** โดยใช้:
  - TF-IDF + Cosine Similarity สำหรับการกรองตามเนื้อหา
  - KNN + SVD สำหรับการกรองแบบ Collaborative
  - วิธีผสมผสาน (Hybrid) ที่รวมทั้งสองวิธี

## เทคโนโลยีที่ใช้

### Backend
- **Framework**: Python กับ FastAPI
- **ฐานข้อมูล**: PostgreSQL กับ SQLAlchemy (async) + Supabase (optional)
- **การยืนยันตัวตน**: Firebase Admin SDK + JWT (python-jose)
- **AI/ML**: scikit-learn สำหรับ TF-IDF, KNN, SVD

### Frontend
- **Framework**: React 18
- **Routing**: React Router v6
- **การรองรับหลายภาษา**: i18next
- **การยืนยันตัวตน**: Firebase Auth
- **HTTP Client**: Axios

## เริ่มต้นใช้งาน

### สิ่งที่ต้องมี
- Python 3.10+
- Node.js 18+
- PostgreSQL 13+
- โปรเจกต์ Firebase

### การตั้งค่า Backend

```bash
cd backend

# สร้าง virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# หรือ venv\Scripts\activate  # Windows

# ติดตั้ง dependencies
pip install -r requirements.txt

# คัดลอกไฟล์ตัวแปรสภาพแวดล้อม
cp .env.example .env
# แก้ไข .env ตามการตั้งค่าของคุณ

# ตั้งค่าฐานข้อมูล (รัน schema.sql ใน PostgreSQL)
psql -d your_database -f schema.sql

# เริ่มเซิร์ฟเวอร์สำหรับพัฒนา
uvicorn app.main:app --reload --port 3001
```

### การตั้งค่า Frontend

```bash
cd frontend

# ติดตั้ง dependencies
npm install

# คัดลอกไฟล์ตัวแปรสภาพแวดล้อม
cp .env.example .env
# แก้ไข .env ด้วยการตั้งค่า Firebase ของคุณ

# เริ่มเซิร์ฟเวอร์สำหรับพัฒนา
npm start
```

## API Endpoints

### การยืนยันตัวตน
- `POST /api/auth/register` - ลงทะเบียนผู้ใช้ใหม่
- `POST /api/auth/login/firebase` - เข้าสู่ระบบด้วย Firebase token
- `GET /api/auth/profile` - ดูโปรไฟล์ผู้ใช้ปัจจุบัน
- `PUT /api/auth/profile` - อัปเดตโปรไฟล์

### หนังสือ
- `GET /api/books` - รายการหนังสือพร้อมการแบ่งหน้า
- `GET /api/books/search` - ค้นหาหนังสือพร้อมตัวกรอง
- `GET /api/books/autocomplete` - ค้นหาแบบเติมอัตโนมัติ
- `GET /api/books/:id` - ดูรายละเอียดหนังสือ
- `GET /api/books/:id/recommendations` - ดูหนังสือที่คล้ายกัน
- `POST /api/books` - สร้างหนังสือ (ผู้ดูแลระบบ)
- `PUT /api/books/:id` - อัปเดตหนังสือ (ผู้ดูแลระบบ)
- `DELETE /api/books/:id` - ลบหนังสือ (ผู้ดูแลระบบ)

### รีวิว
- `GET /api/reviews/book/:bookId` - ดูรีวิวของหนังสือ
- `POST /api/reviews` - สร้างรีวิว
- `PUT /api/reviews/:id` - อัปเดตรีวิว
- `DELETE /api/reviews/:id` - ลบรีวิว

### รายการโปรด
- `GET /api/favorites` - ดูรายการโปรดของผู้ใช้
- `POST /api/favorites` - เพิ่มในรายการโปรด
- `DELETE /api/favorites/:bookId` - ลบออกจากรายการโปรด

### คำแนะนำ
- `GET /api/recommendations/personalized` - รับคำแนะนำเฉพาะบุคคล
- `GET /api/recommendations/popular` - ดูหนังสือยอดนิยม
- `POST /api/recommendations/interaction` - บันทึกการโต้ตอบของผู้ใช้

## โครงสร้างฐานข้อมูล

ระบบใช้ตารางหลักดังต่อไปนี้:
- **users** - บัญชีผู้ใช้
- **books** - มังงะ/นิยาย
- **authors** - นักเขียน
- **publishers** - สำนักพิมพ์
- **tags** - หมวดหมู่และธีม
- **reviews** - รีวิวและคะแนนจากผู้ใช้
- **favorites** - หนังสือที่บันทึกไว้ของผู้ใช้
- **search_history** - ประวัติการค้นหาสำหรับคำแนะนำ
- **user_interactions** - การติดตามพฤติกรรมผู้ใช้

## อัลกอริทึมแนะนำจาก AI

### การกรองตามเนื้อหา (TF-IDF + Cosine Similarity)
- วิเคราะห์คำอธิบาย ชื่อเรื่อง และแท็กของหนังสือ
- ค้นหาหนังสือที่คล้ายกันโดยอิงจากเนื้อหาข้อความ
- ทำงานได้ดีสำหรับผู้ใช้ใหม่ที่มีประวัติจำกัด

### การกรองแบบ Collaborative (KNN + SVD)
- **KNN**: ค้นหาผู้ใช้ที่มีความชอบคล้ายกัน
- **SVD**: Matrix factorization สำหรับ latent features
- ทำนายคะแนนโดยอิงจากพฤติกรรมของผู้ใช้ที่คล้ายกัน

### วิธีผสมผสาน (Hybrid)
รวมทั้งสองวิธีด้วยน้ำหนักที่ปรับได้:
- ตามเนื้อหา: 30%
- KNN: 40%
- SVD: 30%

## สัญญาอนุญาต

ISC

---

## Switching to Supabase

This project now supports [Supabase](https://supabase.com/) as an alternative backend data/store integration. Supabase provides a hosted PostgreSQL database with additional features like real-time subscriptions, authentication, and storage.

### ⚠️ Important Security Notice

**If you previously shared your Supabase anon key (e.g., pasted it in chat, code, or any public location), you MUST rotate it immediately:**

1. Go to your [Supabase Dashboard](https://app.supabase.com/)
2. Navigate to **Project Settings > API**
3. Click **Generate new anon key**
4. Update your `.env` file with the new key
5. For production, add the keys to **GitHub Secrets** instead of committing them

**Never commit real API keys or secrets to version control!**

### Environment Variables

Add the following to your `.env` file in the `backend/` directory:

```bash
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here
```

#### Key Types:
- **`SUPABASE_ANON_KEY`**: Safe for client-side use, respects Row Level Security (RLS)
- **`SUPABASE_SERVICE_ROLE_KEY`**: **Server-side ONLY!** Bypasses RLS. Never expose to client code.

### Row Level Security (RLS) Recommendations

For production use, enable RLS on your Supabase tables:

1. In Supabase Dashboard, go to **Authentication > Policies**
2. Enable RLS for each table
3. Create policies that define who can read/write data

Example policies:
```sql
-- Allow authenticated users to read all books
CREATE POLICY "Books are viewable by everyone" ON books
  FOR SELECT USING (true);

-- Allow users to insert their own reviews
CREATE POLICY "Users can insert their own reviews" ON reviews
  FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Allow users to update their own reviews
CREATE POLICY "Users can update their own reviews" ON reviews
  FOR UPDATE USING (auth.uid() = user_id);
```

### Using the Supabase Client

The Supabase client is available at `backend/app/config/supabase_client.py`:

```python
from app.config.supabase_client import get_supabase_client, get_supabase_admin_client

# For user-facing operations (respects RLS)
client = get_supabase_client()
response = client.table("books").select("*").limit(10).execute()

# For admin operations (bypasses RLS - server-side only!)
admin_client = get_supabase_admin_client()
response = admin_client.table("users").select("*").execute()
```

### GitHub Secrets Setup

For CI/CD and production deployments, add these secrets to your GitHub repository:

1. Go to **Repository Settings > Secrets and variables > Actions**
2. Add the following secrets:
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`
   - `SUPABASE_SERVICE_ROLE_KEY`

### Migration Notes

The current codebase uses SQLAlchemy async with a direct PostgreSQL connection. To fully migrate to Supabase:

1. **Database**: Your existing PostgreSQL schema (`schema.sql`) is compatible with Supabase's PostgreSQL
2. **API Routes**: TODO comments have been added to indicate where Supabase client calls can replace SQLAlchemy queries
3. **Storage**: Use `client.storage` for file uploads (e.g., book cover images)
4. **Auth**: Consider using Supabase Auth alongside or instead of Firebase Auth

See the `backend/app/config/supabase_client.py` module for example usage patterns.