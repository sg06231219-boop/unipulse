"""
UniPulse Backend v2 - 选校·选专业·看就业
FastAPI + SQLite + User Auth + Employment Data + Enhanced Forum
"""
import sqlite3, json, os, sys, hashlib, secrets
from pathlib import Path
from datetime import datetime, timedelta
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException, Query, Depends, Security, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional

ROOT = Path(__file__).parent
DB = ROOT / "unipulse.db"
DIST = ROOT / "dist"

# ── Auth setup ──────────────────────────────────────────
security = HTTPBearer(auto_error=False)

def hash_pw(pwd: str) -> str:
    return hashlib.sha256(pwd.encode()).hexdigest()

def make_token(db, user_id: int) -> str:
    token = secrets.token_hex(32)
    exp = (datetime.now() + timedelta(days=7)).isoformat()
    db.execute("INSERT INTO sessions(token, user_id, expires_at) VALUES(?,?,?)",
               (token, user_id, exp))
    db.commit()
    return token

def get_current_user(
    creds: HTTPAuthorizationCredentials = Security(security)
) -> dict | None:
    if not creds:
        return None
    db = get_db()
    row = db.execute(
        "SELECT user_id FROM sessions WHERE token=? AND expires_at > datetime('now')",
        (creds.credentials,)
    ).fetchone()
    if not row:
        db.close()
        return None
    user = db.execute(
        "SELECT id, username, email, role FROM users WHERE id=?", (row['user_id'],)
    ).fetchone()
    db.close()
    return dict(user) if user else None

def require_user(user: dict = Depends(get_current_user)) -> dict:
    if not user:
        raise HTTPException(status_code=401, detail="请先登录")
    return user

def require_admin(user: dict = Depends(get_current_user)) -> dict:
    if not user:
        raise HTTPException(status_code=401, detail="请先登录")
    db = get_db()
    row = db.execute("SELECT role FROM users WHERE id=?", (user['id'],)).fetchone()
    db.close()
    if not row or row['role'] != 'admin':
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return user

# ── Pydantic Models ─────────────────────────────────────

class CreatePostBody(BaseModel):
    title: str = Field(..., max_length=100)
    category: str = "全部话题"
    content: str
    tags: list = Field(default_factory=list)
    uni_id: Optional[int] = None
    program_name: Optional[str] = None

class CreateCommentBody(BaseModel):
    text: str = Field(..., min_length=1)

class RegisterBody(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)
    email: str
    password: str = Field(..., min_length=6)

class LoginBody(BaseModel):
    email: str
    password: str

# ── Database ────────────────────────────────────────────

def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def init_db():
    db = get_db()
    db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            created_at TEXT DEFAULT (datetime('now','localtime'))
        );
        CREATE TABLE IF NOT EXISTS sessions (
            token TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            expires_at TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now','localtime'))
        );
        CREATE TABLE IF NOT EXISTS universities (
            id INTEGER PRIMARY KEY, name TEXT, cn TEXT, loc TEXT,
            region TEXT, country TEXT, logo TEXT, initials TEXT,
            score REAL, trend TEXT, trendV TEXT, stars REAL,
            reviews INTEGER, rank INTEGER, metrics TEXT,
            tags TEXT, description TEXT
        );
        CREATE TABLE IF NOT EXISTS programs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, icon TEXT, ranking TEXT
        );
        CREATE TABLE IF NOT EXISTS uni_programs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uni_id INTEGER NOT NULL,
            program_name TEXT NOT NULL,
            salary_avg INTEGER,
            salary_entry INTEGER,
            employment_rate REAL,
            pressure INTEGER,
            prospects INTEGER,
            description TEXT,
            FOREIGN KEY (uni_id) REFERENCES universities(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS forum_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
            title TEXT NOT NULL, category TEXT DEFAULT '全部话题',
            author TEXT DEFAULT '匿名用户',
            content TEXT,
            views INTEGER DEFAULT 0, likes INTEGER DEFAULT 0,
            tags TEXT DEFAULT '[]',
            uni_id INTEGER, program_name TEXT,
            created_at TEXT DEFAULT (datetime('now','localtime'))
        );
        CREATE TABLE IF NOT EXISTS forum_comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL REFERENCES forum_posts(id) ON DELETE CASCADE,
            user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
            author TEXT DEFAULT '匿名用户', text TEXT NOT NULL,
            likes INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now','localtime'))
        );
        CREATE INDEX IF NOT EXISTS idx_comments_post ON forum_comments(post_id);
        CREATE INDEX IF NOT EXISTS idx_posts_category ON forum_posts(category);
        CREATE INDEX IF NOT EXISTS idx_uni_programs_uni ON uni_programs(uni_id);
        CREATE INDEX IF NOT EXISTS idx_uni_programs_name ON uni_programs(program_name);
    """)

    # Migrate: add columns if missing
    try: db.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user'")
    except: pass
    try: db.execute("ALTER TABLE forum_posts ADD COLUMN likes INTEGER DEFAULT 0")
    except: pass
    try: db.execute("ALTER TABLE forum_posts ADD COLUMN uni_id INTEGER")
    except: pass
    try: db.execute("ALTER TABLE forum_posts ADD COLUMN program_name TEXT")
    except: pass

    if not db.execute("SELECT 1 FROM users WHERE role='admin'").fetchone():
        admin_hash = hash_pw('admin123')
        try:
            db.execute("INSERT INTO users(username,email,password_hash,role) VALUES('admin','admin@unipulse.com',?,'admin')", (admin_hash,))
        except:
            db.execute("UPDATE users SET role='admin' WHERE id=1")
    db.commit()

    if db.execute("SELECT COUNT(*) FROM universities").fetchone()[0] == 0:
        seed_data(db)
    if db.execute("SELECT COUNT(*) FROM uni_programs").fetchone()[0] == 0:
        seed_employment(db)
    db.commit()
    db.close()

def seed_data(db: sqlite3.Connection):
    from seed import UNIVERSITIES, PROGRAMS, FORUM_POSTS, FORUM_COMMENTS
    for u in UNIVERSITIES:
        db.execute("INSERT INTO universities VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (u['id'],u['name'],u['cn'],u['loc'],u['region'],u['country'],
             u['logo'],u['initials'],u['score'],u['trend'],u['trendV'],
             u['stars'],u['reviews'],u['rank'],
             json.dumps(u['metrics'],ensure_ascii=False),
             json.dumps(u['tags'],ensure_ascii=False),
             u.get('description','')))
    for p in PROGRAMS:
        db.execute("INSERT INTO programs(name,icon,ranking) VALUES(?,?,?)",
            (p['name'],p['icon'],json.dumps(p['univs'],ensure_ascii=False)))
    for fp in FORUM_POSTS:
        db.execute("INSERT INTO forum_posts(id,user_id,title,category,author,content,views,tags,created_at) VALUES(?,?,?,?,?,?,?,?,?)",
            (fp['id'], fp.get('user_id'), fp['title'], fp['category'],
             fp['author'], fp['content'], fp['views'],
             json.dumps(fp['tags'],ensure_ascii=False),
             fp.get('time','datetime("now","localtime")')))
    for fc in FORUM_COMMENTS:
        db.execute("INSERT INTO forum_comments(id,post_id,author,text,likes,created_at) VALUES(?,?,?,?,?,?)",
            (fc['id'],fc['post_id'],fc['author'],fc['text'],fc['likes'],
             fc.get('time','datetime("now","localtime")')))

def seed_employment(db: sqlite3.Connection):
    from employment_data import UNI_PROGRAMS
    for ep in UNI_PROGRAMS:
        db.execute("INSERT INTO uni_programs(uni_id,program_name,salary_avg,salary_entry,employment_rate,pressure,prospects,description) VALUES(?,?,?,?,?,?,?,?)",
            (ep['uni_id'], ep['program_name'], ep['salary_avg'], ep['salary_entry'],
             ep['employment_rate'], ep['pressure'], ep['prospects'], ep['description']))

# ── App ─────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="UniPulse API v2", lifespan=lifespan)
app.add_middleware(CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# ── Helpers ─────────────────────────────────────────────

def row_to_dict(row) -> dict:
    return dict(row) if row else None

def parse_json_field(v):
    if v is None: return None
    if isinstance(v, (dict, list)): return v
    try: return json.loads(v)
    except: return v

# ── Auth API ────────────────────────────────────────────

@app.post("/api/auth/register")
def auth_register(body: RegisterBody):
    db = get_db()
    if db.execute("SELECT 1 FROM users WHERE email=?", (body.email,)).fetchone():
        db.close(); raise HTTPException(400, "邮箱已被注册")
    if db.execute("SELECT 1 FROM users WHERE username=?", (body.username,)).fetchone():
        db.close(); raise HTTPException(400, "用户名已被占用")
    pw_hash = hash_pw(body.password)
    cur = db.execute("INSERT INTO users(username,email,password_hash) VALUES(?,?,?)",
                     (body.username, body.email, pw_hash))
    db.commit()
    user_id = cur.lastrowid
    token = make_token(db, user_id)
    user = db.execute("SELECT id,username,email FROM users WHERE id=?",(user_id,)).fetchone()
    db.close()
    return {"token": token, "user": dict(user)}

@app.post("/api/auth/login")
def auth_login(body: LoginBody):
    db = get_db()
    row = db.execute("SELECT id,username,email,password_hash FROM users WHERE email=?",
                     (body.email,)).fetchone()
    if not row or hash_pw(body.password) != row['password_hash']:
        db.close(); raise HTTPException(401, "邮箱或密码错误")
    token = make_token(db, row['id'])
    db.close()
    return {"token": token, "user": {"id": row['id'], "username": row['username'], "email": row['email']}}

@app.get("/api/auth/me")
def auth_me(user: dict = Depends(require_user)):
    return user

@app.post("/api/auth/logout")
def auth_logout(creds: HTTPAuthorizationCredentials = Security(security)):
    if creds:
        db = get_db()
        db.execute("DELETE FROM sessions WHERE token=?", (creds.credentials,))
        db.commit()
        db.close()
    return {"ok": True}

# ── University API ──────────────────────────────────────

@app.get("/api/universities")
def list_universities(search: str = Query(""), region: str = Query("all"), country: str = Query(""), page: int = Query(1, ge=1), size: int = Query(30, ge=1, le=100)):
    db = get_db()
    q = "SELECT * FROM universities WHERE 1=1"
    params = []
    if region and region != "all":
        q += " AND region = ?"; params.append(region)
    if country:
        q += " AND country = ?"; params.append(country)
    if search:
        q += " AND (cn LIKE ? OR name LIKE ? OR description LIKE ? OR loc LIKE ?)"
        s = f"%{search}%"; params.extend([s,s,s,s])
    cnt_q = q.replace("SELECT *", "SELECT COUNT(*)")
    total = db.execute(cnt_q, params).fetchone()[0]
    q += " ORDER BY rank ASC LIMIT ? OFFSET ?"
    params.extend([size, (page - 1) * size])
    rows = db.execute(q, params).fetchall()
    result = []
    for r in rows:
        d = row_to_dict(r)
        d['metrics'] = parse_json_field(d['metrics'])
        d['tags'] = parse_json_field(d['tags'])
        result.append(d)
    db.close()
    return {"total": total, "page": page, "size": size, "items": result}

@app.get("/api/universities/{uni_id}")
def get_university(uni_id: int):
    db = get_db()
    r = db.execute("SELECT * FROM universities WHERE id = ?", (uni_id,)).fetchone()
    if not r:
        db.close(); raise HTTPException(404, "高校不存在")
    d = row_to_dict(r)
    d['metrics'] = parse_json_field(d['metrics'])
    d['tags'] = parse_json_field(d['tags'])
    # attach employment data
    progs = db.execute("SELECT * FROM uni_programs WHERE uni_id=?", (uni_id,)).fetchall()
    d['programs'] = [dict(p) for p in progs]
    db.close()
    return d

@app.get("/api/universities/{uni_id}/programs")
def get_uni_programs(uni_id: int):
    db = get_db()
    rows = db.execute("SELECT * FROM uni_programs WHERE uni_id=?", (uni_id,)).fetchall()
    db.close()
    return [dict(r) for r in rows]

# ── Employment / Majors API ─────────────────────────────

@app.get("/api/majors/overview")
def majors_overview():
    """按专业聚合全站就业数据"""
    db = get_db()
    rows = db.execute("""
        SELECT program_name,
               COUNT(*) as uni_count,
               ROUND(AVG(salary_avg)) as avg_salary,
               ROUND(AVG(salary_entry)) as avg_entry,
               ROUND(AVG(employment_rate),1) as avg_employment,
               ROUND(AVG(pressure),1) as avg_pressure,
               ROUND(AVG(prospects),1) as avg_prospects
        FROM uni_programs
        GROUP BY program_name
        ORDER BY avg_salary DESC
    """).fetchall()
    db.close()
    return [dict(r) for r in rows]

@app.get("/api/majors/{program_name}")
def get_major_detail(program_name: str):
    """某专业在各大学的就业数据对比"""
    db = get_db()
    rows = db.execute("""
        SELECT up.*, u.cn as uni_cn, u.name as uni_name, u.country, u.rank
        FROM uni_programs up
        JOIN universities u ON up.uni_id = u.id
        WHERE up.program_name = ?
        ORDER BY up.salary_avg DESC
    """, (program_name,)).fetchall()
    db.close()
    if not rows:
        raise HTTPException(404, f"未找到专业「{program_name}」的数据")
    return [dict(r) for r in rows]

@app.get("/api/majors")
def list_majors():
    """所有专业名称列表"""
    db = get_db()
    rows = db.execute("SELECT DISTINCT program_name FROM uni_programs ORDER BY program_name").fetchall()
    db.close()
    return [r['program_name'] for r in rows]

# ── Ranking API ──────────────────────────────────────────

@app.get("/api/rankings")
def get_rankings(dimension: str = Query("academic")):
    valid = {'academic','research','reputation','campus','support','international','value','career'}
    if dimension not in valid:
        raise HTTPException(400, f"无效维度，可选: {valid}")
    db = get_db()
    rows = db.execute("SELECT id,cn,name,country,metrics FROM universities").fetchall()
    result = []
    for r in rows:
        d = row_to_dict(r)
        metrics = parse_json_field(d['metrics'])
        d['dim_value'] = metrics.get(dimension)
        d.pop('metrics', None)
        result.append(d)
    result.sort(key=lambda x: x.get('dim_value') or 0, reverse=True)
    db.close()
    return result

@app.get("/api/dimensions")
def get_dimensions():
    return [
        {"key":"academic","label":"学术水平","weight":25},
        {"key":"research","label":"科研产出","weight":20},
        {"key":"reputation","label":"行业声誉","weight":15},
        {"key":"campus","label":"校园环境","weight":10},
        {"key":"support","label":"学生关怀","weight":10},
        {"key":"international","label":"国际化","weight":10},
        {"key":"value","label":"性价比","weight":5},
        {"key":"career","label":"就业前景","weight":5},
    ]

# ── Programs API ────────────────────────────────────────

@app.get("/api/programs")
def get_programs():
    db = get_db()
    rows = db.execute("SELECT * FROM programs").fetchall()
    result = []
    for r in rows:
        d = row_to_dict(r)
        d['univs'] = parse_json_field(d['ranking'])
        d.pop('ranking', None)
        result.append(d)
    db.close()
    return result

# ── Forum API (Enhanced) ───────────────────────────────

@app.get("/api/forum/categories")
def get_forum_categories():
    db = get_db()
    rows = db.execute("SELECT category as cat, COUNT(*) as count FROM forum_posts GROUP BY category").fetchall()
    cats = [
        {"key":"all","label":"🔥 全部","count":0},
        {"key":"选校咨询","label":"🏫 选校咨询","count":0},
        {"key":"专业对比","label":"📊 专业对比","count":0},
        {"key":"就业前景","label":"💼 就业前景","count":0},
        {"key":"留学申请","label":"✈️ 留学申请","count":0},
        {"key":"考研交流","label":"📖 考研交流","count":0},
        {"key":"校园生活","label":"🏠 校园生活","count":0},
        {"key":"奖学金","label":"💰 奖学金","count":0},
        {"key":"实习经验","label":"🏢 实习经验","count":0},
    ]
    total = 0
    cat_map = {r['cat']: r['count'] for r in rows}
    for c in cats:
        cnt = cat_map.get(c['key'], 0)
        c['count'] = cnt
        total += cnt
    cats[0]['count'] = total
    db.close()
    return cats

@app.get("/api/forum/posts")
def list_forum_posts(category: str = Query("all"), search: str = Query(""),
                     uni_id: int = Query(None), program_name: str = Query(""),
                     sort: str = Query("new"), page: int = Query(1, ge=1), size: int = Query(20, ge=1, le=100)):
    db = get_db()
    q = "SELECT p.* FROM forum_posts p WHERE 1=1"
    params = []
    if category and category != "all":
        q += " AND p.category = ?"; params.append(category)
    if search:
        q += " AND (p.title LIKE ? OR p.content LIKE ?)"
        s = f"%{search}%"; params.extend([s,s])
    if uni_id:
        q += " AND p.uni_id = ?"; params.append(uni_id)
    if program_name:
        q += " AND p.program_name = ?"; params.append(program_name)
    # count
    cnt_q = q.replace("SELECT p.*", "SELECT COUNT(*)")
    total = db.execute(cnt_q, params).fetchone()[0]
    # sort
    if sort == "hot":
        q += " ORDER BY (p.views + p.likes*3) DESC"
    else:
        q += " ORDER BY p.id DESC"
    q += " LIMIT ? OFFSET ?"
    params.extend([size, (page-1)*size])
    rows = db.execute(q, params).fetchall()
    result = []
    for r in rows:
        d = row_to_dict(r)
        d['tags'] = parse_json_field(d['tags'])
        d['replies'] = db.execute("SELECT COUNT(*) FROM forum_comments WHERE post_id=?", (d['id'],)).fetchone()[0]
        # attach uni name if linked
        if d.get('uni_id'):
            uni = db.execute("SELECT cn FROM universities WHERE id=?", (d['uni_id'],)).fetchone()
            d['uni_cn'] = uni['cn'] if uni else None
        result.append(d)
    db.close()
    return {"total": total, "page": page, "size": size, "items": result}

@app.get("/api/forum/posts/{post_id}")
def get_forum_post(post_id: int):
    db = get_db()
    post = db.execute("SELECT * FROM forum_posts WHERE id = ?", (post_id,)).fetchone()
    if not post:
        db.close(); raise HTTPException(404, "帖子不存在")
    db.execute("UPDATE forum_posts SET views = views + 1 WHERE id = ?", (post_id,))
    db.commit()
    comments = db.execute("SELECT * FROM forum_comments WHERE post_id = ? ORDER BY id ASC", (post_id,)).fetchall()
    result = row_to_dict(post)
    result['tags'] = parse_json_field(result['tags'])
    result['comments'] = [row_to_dict(c) for c in comments]
    if result.get('uni_id'):
        uni = db.execute("SELECT cn FROM universities WHERE id=?", (result['uni_id'],)).fetchone()
        result['uni_cn'] = uni['cn'] if uni else None
    db.close()
    return result

@app.post("/api/forum/posts")
def create_post(data: CreatePostBody, user: dict = Depends(require_user)):
    db = get_db()
    tags = json.dumps(data.tags, ensure_ascii=False)
    cur = db.execute(
        "INSERT INTO forum_posts(user_id,title,category,author,content,tags,uni_id,program_name) VALUES(?,?,?,?,?,?,?,?)",
        (user['id'], data.title, data.category, user['username'], data.content, tags,
         data.uni_id, data.program_name))
    db.commit()
    new_id = cur.lastrowid
    db.close()
    return {"id": new_id, "message": "✅ 发帖成功！"}

@app.post("/api/forum/posts/{post_id}/like")
def like_post(post_id: int):
    db = get_db()
    if not db.execute("SELECT 1 FROM forum_posts WHERE id=?", (post_id,)).fetchone():
        db.close(); raise HTTPException(404, "帖子不存在")
    db.execute("UPDATE forum_posts SET likes = likes + 1 WHERE id = ?", (post_id,))
    db.commit()
    new_likes = db.execute("SELECT likes FROM forum_posts WHERE id=?", (post_id,)).fetchone()[0]
    db.close()
    return {"likes": new_likes}

@app.post("/api/forum/posts/{post_id}/comments")
def create_comment(post_id: int, data: CreateCommentBody, user: dict = Depends(require_user)):
    db = get_db()
    if not db.execute("SELECT 1 FROM forum_posts WHERE id=?", (post_id,)).fetchone():
        db.close(); raise HTTPException(404, "帖子不存在")
    cur = db.execute(
        "INSERT INTO forum_comments(post_id,user_id,author,text) VALUES(?,?,?,?)",
        (post_id, user['id'], user['username'], data.text))
    db.commit()
    new_id = cur.lastrowid
    db.close()
    return {"id": new_id, "message": "✅ 回复成功！"}

@app.post("/api/forum/comments/{comment_id}/like")
def like_comment(comment_id: int):
    db = get_db()
    if not db.execute("SELECT 1 FROM forum_comments WHERE id=?", (comment_id,)).fetchone():
        db.close(); raise HTTPException(404, "评论不存在")
    db.execute("UPDATE forum_comments SET likes = likes + 1 WHERE id = ?", (comment_id,))
    db.commit()
    new_likes = db.execute("SELECT likes FROM forum_comments WHERE id=?", (comment_id,)).fetchone()[0]
    db.close()
    return {"likes": new_likes}

@app.get("/api/forum/hot")
def get_hot_topics(limit: int = Query(10)):
    db = get_db()
    rows = db.execute("SELECT id, title, views, likes, category FROM forum_posts ORDER BY (views + likes*3) DESC LIMIT ?", (limit,)).fetchall()
    result = [dict(r) for r in rows]
    db.close()
    return result

# ── Admin API ───────────────────────────────────────────

@app.get("/api/admin/stats")
def admin_stats(_: dict = Depends(require_admin)):
    db = get_db()
    users = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    posts = db.execute("SELECT COUNT(*) FROM forum_posts").fetchone()[0]
    comments = db.execute("SELECT COUNT(*) FROM forum_comments").fetchone()[0]
    unis = db.execute("SELECT COUNT(*) FROM universities").fetchone()[0]
    programs_cnt = db.execute("SELECT COUNT(*) FROM programs").fetchone()[0]
    emp_cnt = db.execute("SELECT COUNT(*) FROM uni_programs").fetchone()[0]
    recent = db.execute("SELECT COUNT(*) FROM users WHERE created_at > datetime('now','localtime','-7 days')").fetchone()[0]
    recent_posts = db.execute("SELECT COUNT(*) FROM forum_posts WHERE created_at > datetime('now','localtime','-7 days')").fetchone()[0]
    db.close()
    return {"users": users, "posts": posts, "comments": comments,
            "universities": unis, "programs": programs_cnt, "employment_records": emp_cnt,
            "recent_users": recent, "recent_posts": recent_posts}

@app.get("/api/admin/users")
def admin_list_users(page: int = Query(1, ge=1), size: int = Query(20, ge=1, le=100), _: dict = Depends(require_admin)):
    db = get_db()
    total = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    rows = db.execute("SELECT id,username,email,role,created_at FROM users ORDER BY id DESC LIMIT ? OFFSET ?",
                      (size, (page-1)*size)).fetchall()
    db.close()
    return {"total": total, "items": [dict(r) for r in rows]}

@app.put("/api/admin/users/{user_id}/role")
def admin_set_role(user_id: int, role: str = Query(...), _: dict = Depends(require_admin)):
    if role not in ('user', 'admin'):
        raise HTTPException(400, "role 必须是 user 或 admin")
    db = get_db()
    if not db.execute("SELECT 1 FROM users WHERE id=?", (user_id,)).fetchone():
        db.close(); raise HTTPException(404, "用户不存在")
    db.execute("UPDATE users SET role=? WHERE id=?", (role, user_id))
    db.commit(); db.close()
    return {"ok": True, "user_id": user_id, "role": role}

@app.delete("/api/admin/users/{user_id}")
def admin_delete_user(user_id: int, _: dict = Depends(require_admin)):
    db = get_db()
    if not db.execute("SELECT 1 FROM users WHERE id=?", (user_id,)).fetchone():
        db.close(); raise HTTPException(404, "用户不存在")
    db.execute("DELETE FROM sessions WHERE user_id=?", (user_id,))
    db.execute("UPDATE forum_posts SET user_id=NULL, author='[已删除用户]' WHERE user_id=?", (user_id,))
    db.execute("UPDATE forum_comments SET user_id=NULL, author='[已删除用户]' WHERE user_id=?", (user_id,))
    db.execute("DELETE FROM users WHERE id=?", (user_id,))
    db.commit(); db.close()
    return {"ok": True}

@app.get("/api/admin/posts")
def admin_list_posts(page: int = Query(1, ge=1), size: int = Query(20, ge=1, le=100), _: dict = Depends(require_admin)):
    db = get_db()
    total = db.execute("SELECT COUNT(*) FROM forum_posts").fetchone()[0]
    rows = db.execute("SELECT p.*, (SELECT COUNT(*) FROM forum_comments WHERE post_id=p.id) as comment_count FROM forum_posts p ORDER BY p.id DESC LIMIT ? OFFSET ?",
                      (size, (page-1)*size)).fetchall()
    db.close()
    return {"total": total, "items": [dict(r) for r in rows]}

@app.delete("/api/admin/posts/{post_id}")
def admin_delete_post(post_id: int, _: dict = Depends(require_admin)):
    db = get_db()
    if not db.execute("SELECT 1 FROM forum_posts WHERE id=?", (post_id,)).fetchone():
        db.close(); raise HTTPException(404, "帖子不存在")
    db.execute("DELETE FROM forum_comments WHERE post_id=?", (post_id,))
    db.execute("DELETE FROM forum_posts WHERE id=?", (post_id,))
    db.commit(); db.close()
    return {"ok": True}

@app.get("/api/admin/comments")
def admin_list_comments(page: int = Query(1, ge=1), size: int = Query(20, ge=1, le=100), _: dict = Depends(require_admin)):
    db = get_db()
    total = db.execute("SELECT COUNT(*) FROM forum_comments").fetchone()[0]
    rows = db.execute("SELECT c.*, p.title as post_title FROM forum_comments c LEFT JOIN forum_posts p ON c.post_id=p.id ORDER BY c.id DESC LIMIT ? OFFSET ?",
                      (size, (page-1)*size)).fetchall()
    db.close()
    return {"total": total, "items": [dict(r) for r in rows]}

@app.delete("/api/admin/comments/{comment_id}")
def admin_delete_comment(comment_id: int, _: dict = Depends(require_admin)):
    db = get_db()
    if not db.execute("SELECT 1 FROM forum_comments WHERE id=?", (comment_id,)).fetchone():
        db.close(); raise HTTPException(404, "评论不存在")
    db.execute("DELETE FROM forum_comments WHERE id=?", (comment_id,))
    db.commit(); db.close()
    return {"ok": True}

@app.get("/api/admin/universities")
def admin_list_unis(page: int = Query(1, ge=1), size: int = Query(20, ge=1, le=100), _: dict = Depends(require_admin)):
    db = get_db()
    total = db.execute("SELECT COUNT(*) FROM universities").fetchone()[0]
    rows = db.execute("SELECT * FROM universities ORDER BY rank ASC LIMIT ? OFFSET ?",
                      (size, (page-1)*size)).fetchall()
    result = []
    for r in rows:
        d = dict(r)
        d['metrics'] = parse_json_field(d['metrics'])
        d['tags'] = parse_json_field(d['tags'])
        result.append(d)
    db.close()
    return {"total": total, "items": result}

@app.delete("/api/admin/universities/{uni_id}")
def admin_delete_uni(uni_id: int, _: dict = Depends(require_admin)):
    db = get_db()
    if not db.execute("SELECT 1 FROM universities WHERE id=?", (uni_id,)).fetchone():
        db.close(); raise HTTPException(404, "高校不存在")
    db.execute("DELETE FROM universities WHERE id=?", (uni_id,))
    db.commit(); db.close()
    return {"ok": True}

@app.put("/api/admin/universities/{uni_id}")
def admin_update_uni(uni_id: int, data: dict = None, _: dict = Depends(require_admin)):
    db = get_db()
    if not db.execute("SELECT 1 FROM universities WHERE id=?", (uni_id,)).fetchone():
        db.close(); raise HTTPException(404, "高校不存在")
    allowed = ['name','cn','loc','region','country','logo','initials','score','trend','trendV','stars','reviews','rank','description']
    sets = []; vals = []
    for k in allowed:
        if k in (data or {}):
            sets.append(k+'=?'); vals.append(data[k])
    if data and 'metrics' in data:
        sets.append('metrics=?'); vals.append(json.dumps(data['metrics'], ensure_ascii=False))
    if data and 'tags' in data:
        sets.append('tags=?'); vals.append(json.dumps(data['tags'], ensure_ascii=False))
    if not sets:
        db.close(); return {"ok": True}
    vals.append(uni_id)
    db.execute('UPDATE universities SET '+','.join(sets)+' WHERE id=?', vals)
    db.commit(); db.close()
    return {"ok": True}

@app.get("/api/admin/employment")
def admin_list_employment(page: int = Query(1, ge=1), size: int = Query(20, ge=1, le=100), _: dict = Depends(require_admin)):
    db = get_db()
    total = db.execute("SELECT COUNT(*) FROM uni_programs").fetchone()[0]
    rows = db.execute("""
        SELECT up.*, u.cn as uni_cn FROM uni_programs up
        LEFT JOIN universities u ON up.uni_id = u.id
        ORDER BY up.id LIMIT ? OFFSET ?
    """, (size, (page-1)*size)).fetchall()
    db.close()
    return {"total": total, "items": [dict(r) for r in rows]}

@app.delete("/api/admin/employment/{ep_id}")
def admin_delete_employment(ep_id: int, _: dict = Depends(require_admin)):
    db = get_db()
    if not db.execute("SELECT 1 FROM uni_programs WHERE id=?", (ep_id,)).fetchone():
        db.close(); raise HTTPException(404, "记录不存在")
    db.execute("DELETE FROM uni_programs WHERE id=?", (ep_id,))
    db.commit(); db.close()
    return {"ok": True}

# ── Health ──────────────────────────────────────────────

@app.get("/api/health")
def health():
    return {"status": "ok", "version": "2.0", "time": datetime.now().isoformat()}

# ── Countries/Regions API ───────────────────────────────

@app.get("/api/countries")
def list_countries():
    db = get_db()
    rows = db.execute("SELECT DISTINCT country FROM universities ORDER BY country").fetchall()
    db.close()
    return [r['country'] for r in rows]

@app.get("/api/regions")
def list_regions():
    db = get_db()
    rows = db.execute("SELECT DISTINCT region FROM universities WHERE region IS NOT NULL ORDER BY region").fetchall()
    db.close()
    return [r['region'] for r in rows]

# ── AI Report generation (background) ──────────────────

import threading, uuid, time

report_jobs: dict = {}
report_lock = threading.Lock()

def generate_ai_report(report_id: str, gpa: float, major: str, regions: list, budget: str, language: str):
    from seed import UNIVERSITIES
    results = []
    for u in UNIVERSITIES:
        score = 0
        reasons = []
        rank = u.get('rank', 999)
        if rank <= 10: score += 40
        elif rank <= 20: score += 30
        elif rank <= 50: score += 20
        elif rank <= 100: score += 10
        else: score += 5
        reasons.append("QS排名" + str(rank))
        desc_lower = u.get('description', '').lower()
        major_lower = major.lower()
        major_categories = {
            '计算机/软件': ['cs','computer','软件','计算机','编程','ai','人工智能','信息科学','数据','算法','machine learning','software','信息技术'],
            '商科': ['business','management','economics','finance','商','管理','经济','金融','会计','marketing','mba'],
            '工程': ['engineering','mechanical','electrical','工科','工程','制造','电子','机械','土木','建筑','civil','aerospace','航空'],
            '医学/健康': ['medicine','medical','health','临床','医学','健康','护理','药学','nursing','pharmacy'],
            '艺术/设计': ['art','design','architecture','music','艺术','设计','音乐','建筑','美术','fashion','创意'],
            '法律': ['law','legal','法学','法律','司法','justice'],
            '理科': ['physics','chemistry','biology','science','物理','化学','生物','数学','统计','mathematics','statistics','自然'],
        }
        user_cat = None
        for cat, keywords in major_categories.items():
            if any(k in major_lower for k in keywords):
                user_cat = (cat, keywords); break
        if user_cat:
            cat_name, cat_keywords = user_cat
            if any(k in desc_lower for k in cat_keywords):
                score += 20; reasons.append(cat_name + "方向突出")
            else:
                score += 10; reasons.append("综合实力强")
        budget_ok = False
        if budget in ['0-20万', '20万以下']:
            budget_ok = u.get('country','') in ['中国', '日本', '新加坡', '韩国', '马来西亚']
        elif budget in ['20-50万']:
            budget_ok = u.get('country','') in ['英国', '澳洲', '加拿大', '欧洲']
        elif budget in ['50万以上']:
            budget_ok = True
        if budget_ok: score += 20
        else: reasons.append("⚠️ 费用可能超标")
        if regions and regions != ['不限']:
            if u.get('region','') in regions or u.get('country','') in regions:
                score += 15
        results.append({
            'id': u['id'], 'name': u['name'], 'cn': u['cn'],
            'country': u.get('country', ''), 'loc': u.get('loc', ''),
            'rank': rank, 'score': min(score, 100),
            'match_reasons': reasons[:4],
            'tuition_hint': u.get('country', '')
        })
    results.sort(key=lambda x: x['score'], reverse=True)
    report = {
        'report_id': report_id,
        'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'input': {'gpa': gpa, 'major': major, 'regions': regions, 'budget': budget, 'language': language},
        'summary': "基于您的" + str(gpa) + " GPA + " + major + "专业偏好，为您精选" + str(len(results)) + "所院校",
        'top_recommendations': results[:3],
        'other_options': results[3:10],
        'total_matched': len(results),
        'ai_notice': "本报告基于公开数据综合分析，仅供参考。"
    }
    with report_lock:
        report_jobs[report_id] = {'status': 'done', 'result': report}

@app.post("/api/ai/report")
async def create_ai_report(
    background_tasks: BackgroundTasks,
    gpa: float = Query(..., ge=0, le=5),
    major: str = Query("..."),
    regions: str = Query("不限"),
    budget: str = Query("不限"),
    language: str = Query("待定"),
):
    if not major.strip(): raise HTTPException(400, "请填写意向专业")
    report_id = str(uuid.uuid4())[:8]
    region_list = [r.strip() for r in regions.split(',') if r.strip()]
    with report_lock:
        report_jobs[report_id] = {'status': 'processing', 'result': None}
    background_tasks.add_task(generate_ai_report, report_id, gpa, major, region_list, budget, language)
    return {'report_id': report_id, 'status': 'processing', 'poll_url': '/api/ai/report/' + report_id}

@app.get("/api/ai/report/{report_id}")
async def get_ai_report(report_id: str):
    with report_lock:
        job = report_jobs.get(report_id)
    if not job: raise HTTPException(404, "报告不存在或已过期")
    if job['status'] == 'processing':
        return {'status': 'processing', 'progress': '50%'}
    return {'status': 'done', 'result': job['result']}

@app.get("/api/ai/wait/{report_id}")
async def wait_ai_report(report_id: str, timeout: int = Query(30)):
    for _ in range(timeout):
        with report_lock:
            job = report_jobs.get(report_id)
        if not job: raise HTTPException(404, "报告不存在")
        if job['status'] == 'done':
            return job['result']
        time.sleep(1)
    raise HTTPException(504, "报告生成超时，请稍后重试")

# ── Static files (frontend) ─────────────────────────────

@app.get("/admin")
async def admin_page():
    p = DIST / "admin.html"
    if p.exists():
        return FileResponse(str(p))
    raise HTTPException(404, "admin.html not found")

if DIST.exists():
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str = ""):
        file_path = DIST / full_path
        if full_path and file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))
        return FileResponse(str(DIST / "index.html"))

    @app.get("/")
    async def root():
        return FileResponse(str(DIST / "index.html"))
else:
    @app.get("/")
    async def root():
        return {"message": "UniPulse API v2 running.", "api": True}

if __name__ == "__main__":
    print("UniPulse v2 - 选校·选专业·看就业")
    print("  API: http://localhost:9999/api/health")
    print("  前端: http://localhost:9999")
    uvicorn.run(app, host="0.0.0.0", port=9999, log_level="info")
