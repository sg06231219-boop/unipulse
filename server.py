"""
UniPulse Backend - FastAPI + SQLite + User Auth
一键启动：python -m uvicorn server:app --host 127.0.0.1 --port 9999
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
        "SELECT id, username, email FROM users WHERE id=?", (row['user_id'],)
    ).fetchone()
    db.close()
    return dict(user) if user else None

def require_user(user: dict = Depends(get_current_user)) -> dict:
    if not user:
        raise HTTPException(status_code=401, detail="请先登录")
    return user

# ── Pydantic Models ─────────────────────────────────────

class CreatePostBody(BaseModel):
    title: str = Field(..., max_length=100)
    category: str = "全部话题"
    content: str
    tags: list = Field(default_factory=list)

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
        CREATE TABLE IF NOT EXISTS forum_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
            title TEXT NOT NULL, category TEXT DEFAULT '全部话题',
            author TEXT DEFAULT '匿名用户',
            content TEXT,
            views INTEGER DEFAULT 0, tags TEXT DEFAULT '[]',
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
    """)

    if db.execute("SELECT COUNT(*) FROM universities").fetchone()[0] == 0:
        seed_data(db)
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
        db.execute("""INSERT INTO forum_posts(id,user_id,title,category,author,content,views,tags,created_at)
                     VALUES(?,?,?,?,?,?,?,?,?)""",
            (fp['id'], fp.get('user_id'), fp['title'], fp['category'],
             fp['author'], fp['content'], fp['views'],
             json.dumps(fp['tags'],ensure_ascii=False),
             fp.get('time','datetime("now","localtime")')))

    for fc in FORUM_COMMENTS:
        db.execute("""INSERT INTO forum_comments(id,post_id,author,text,likes,created_at)
                     VALUES(?,?,?,?,?,?)""",
            (fc['id'],fc['post_id'],fc['author'],fc['text'],fc['likes'],
             fc.get('time','datetime("now","localtime")')))

# ── App ─────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="UniPulse API", lifespan=lifespan)
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
    # check duplicate
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
def list_universities(search: str = Query(""), region: str = Query("all"), page: int = Query(1, ge=1), size: int = Query(30, ge=1, le=100)):
    db = get_db()
    q = "SELECT * FROM universities WHERE 1=1"
    params = []
    if region and region != "all":
        q += " AND region = ?"; params.append(region)
    if search:
        q += " AND (cn LIKE ? OR name LIKE ? OR description LIKE ? OR loc LIKE ?)"
        s = f"%{search}%"; params.extend([s,s,s,s])
    # count
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
    db.close()
    if not r: raise HTTPException(404, "高校不存在")
    d = row_to_dict(r)
    d['metrics'] = parse_json_field(d['metrics'])
    d['tags'] = parse_json_field(d['tags'])
    return d

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

# ── Forum API ───────────────────────────────────────────

@app.get("/api/forum/categories")
def get_forum_categories():
    db = get_db()
    rows = db.execute("SELECT category as cat, COUNT(*) as count FROM forum_posts GROUP BY category").fetchall()
    cats = [
        {"key":"all","label":"全部","count":0},
        {"key":"心理健康","label":"💚 心理健康","count":0},
        {"key":"校园生活","label":"🏠 校园生活","count":0},
        {"key":"学术氛围","label":"📚 学术氛围","count":0},
        {"key":"就业发展","label":"💼 就业发展","count":0},
        {"key":"人文关怀","label":"🤝 人文关怀","count":0},
        {"key":"留学申请","label":"✈️ 留学申请","count":0},
        {"key":"专业选择","label":"🎯 专业选择","count":0},
        {"key":"院校对比","label":"⚖️ 院校对比","count":0},
        {"key":"奖学金","label":"💰 奖学金","count":0},
        {"key":"实习","label":"🏢 实习","count":0},
        {"key":"研究生","label":"🎓 研究生","count":0},
        {"key":"博士","label":"🔬 博士","count":0},
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
def list_forum_posts(category: str = Query("all"), search: str = Query(""), limit: int = Query(50)):
    db = get_db()
    q = "SELECT * FROM forum_posts WHERE 1=1"
    params = []
    if category and category != "all":
        q += " AND category = ?"; params.append(category)
    if search:
        q += " AND (title LIKE ? OR content LIKE ?)"
        s = f"%{search}%"; params.extend([s,s])
    q += " ORDER BY id DESC LIMIT ?"; params.append(limit)
    rows = db.execute(q, params).fetchall()
    result = []
    for r in rows:
        d = row_to_dict(r)
        d['tags'] = parse_json_field(d['tags'])
        d['cat'] = d['category']
        d['time'] = d['created_at']
        d['replies'] = db.execute("SELECT COUNT(*) FROM forum_comments WHERE post_id=?", (d['id'],)).fetchone()[0]
        result.append(d)
    db.close()
    return result

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
    result['cat'] = result['category']
    result['time'] = result['created_at']
    result['comments'] = [row_to_dict(c) for c in comments]
    db.close()
    return result

@app.post("/api/forum/posts")
def create_post(data: CreatePostBody, user: dict = Depends(require_user)):
    db = get_db()
    tags = json.dumps(data.tags, ensure_ascii=False)
    cur = db.execute(
        "INSERT INTO forum_posts(user_id,title,category,author,content,tags) VALUES(?,?,?,?,?,?)",
        (user['id'], data.title, data.category, user['username'], data.content, tags))
    db.commit()
    new_id = cur.lastrowid
    db.close()
    return {"id": new_id, "message": "✅ 发帖成功！"}

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

@app.get("/api/forum/hot")
def get_hot_topics(limit: int = Query(5)):
    db = get_db()
    rows = db.execute("SELECT title as text, views FROM forum_posts ORDER BY views DESC LIMIT ?", (limit,)).fetchall()
    result = [{"text": r['text'], "views": r['views']} for r in rows]
    db.close()
    return result

# ── Health ──────────────────────────────────────────────

@app.get("/api/health")
def health():
    return {"status": "ok", "time": datetime.now().isoformat()}

# ── AI Report generation (background) ──────────────────

import threading, uuid, time

# In-memory job store
report_jobs: dict = {}
report_lock = threading.Lock()

def generate_ai_report(report_id: str, gpa: float, major: str, regions: list, budget: str, language: str):
    """Background worker: generate university recommendations."""
    # Import inside to avoid circular issues
    from seed import UNIVERSITIES
    
    # Score each university
    results = []
    for u in UNIVERSITIES:
        score = 0
        reasons = []
        
        # GPA fit (max 40 points)
        rank = u.get('rank', 999)
        if rank <= 10: score += 40
        elif rank <= 20: score += 30
        elif rank <= 50: score += 20
        elif rank <= 100: score += 10
        else: score += 5
        reasons.append(f"QS排名{rank}，")
        
        # Major match — first determine user's category, then match uni description
        desc_lower = u.get('description', '').lower()
        major_lower = major.lower()
        major_categories = {
            '计算机/软件': ['cs','computer','软件','计算机','编程','ai','人工智能','信息科学','数据','算法','machine learning','software','信息技术'],
            '商科': ['business','management','economics','finance','商','管理','经济','金融','会计','marketing','mba'],
            '工程': ['engineering','mechanical','electrical','工科','工程','制造','电子','机械','土木','建筑','civil','aerospace','航空'],
            '医学/健康': ['medicine','medical','health','临床','医学','健康','护理','药学','nursing','pharmacy','护理'],
            '艺术/设计': ['art','design','architecture','music','艺术','设计','音乐','建筑','美术','fashion','创意'],
            '法律': ['law','legal','法学','法律','司法','justice'],
            '理科': ['physics','chemistry','biology','science','物理','化学','生物','数学','统计','mathematics','statistics','自然'],
        }
        # Step 1: find user's category
        user_cat = None
        for cat, keywords in major_categories.items():
            if any(k in major_lower for k in keywords):
                user_cat = (cat, keywords)
                break
        # Step 2: check if uni matches user's category
        if user_cat:
            cat_name, cat_keywords = user_cat
            if any(k in desc_lower for k in cat_keywords):
                score += 20
                reasons.append(f"{cat_name}方向突出")
            else:
                score += 10
                reasons.append(f"综合实力强（{cat_name}方向待确认）")
        
        # Budget check
        budget_ok = False
        if budget in ['0-20万', '20万以下']:
            budget_ok = u.get('country','') in ['中国', '日本', '新加坡', '韩国', '马来西亚']
        elif budget in ['20-50万']:
            budget_ok = u.get('country','') in ['英国', '澳洲', '加拿大', '欧洲']
        elif budget in ['50万以上']:
            budget_ok = True
        if budget_ok: score += 20
        else: reasons.append("⚠️ 费用可能超标")
        
        # Region preference
        if regions and regions != ['不限']:
            region_ok = u.get('region','') in regions or u.get('country','') in regions
            if region_ok: score += 15
            else: reasons.append(f"不在首选地区")
        
        results.append({
            'id': u['id'], 'name': u['name'], 'cn': u['cn'],
            'country': u.get('country', ''), 'loc': u.get('loc', ''),
            'rank': rank, 'score': min(score, 100),
            'match_reasons': reasons[:4],
            'tuition_hint': u.get('country', '')
        })
    
    results.sort(key=lambda x: x['score'], reverse=True)
    top3 = results[:3]
    mid = results[3:10]
    
    report = {
        'report_id': report_id,
        'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'input': {'gpa': gpa, 'major': major, 'regions': regions, 'budget': budget, 'language': language},
        'summary': f"基于您的{gpa} GPA + {major}专业偏好，为您精选{len(results)}所院校，匹配度最高的前3所如下：",
        'top_recommendations': top3,
        'other_options': mid,
        'total_matched': len(results),
        'ai_notice': "本报告基于公开数据综合分析，仅供参考。选校决策请结合个人情况综合判断，UniPulse 不对录取结果承担责任。"
    }
    
    with report_lock:
        report_jobs[report_id] = {'status': 'done', 'result': report}

@app.post("/api/ai/report")
async def create_ai_report(
    background_tasks: BackgroundTasks,
    gpa: float = Query(..., ge=0, le=5),
    major: str = Query("..."),
    regions: str = Query("不限"),    # comma-separated
    budget: str = Query("不限"),
    language: str = Query("待定"),
):
    if not major.strip(): raise HTTPException(400, "请填写意向专业")
    report_id = str(uuid.uuid4())[:8]
    region_list = [r.strip() for r in regions.split(',') if r.strip()]
    with report_lock:
        report_jobs[report_id] = {'status': 'processing', 'result': None}
    background_tasks.add_task(generate_ai_report, report_id, gpa, major, region_list, budget, language)
    return {'report_id': report_id, 'status': 'processing', 'poll_url': f'/api/ai/report/{report_id}'}

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
    """Poll until report is ready (max 30s)."""
    for _ in range(timeout):
        with report_lock:
            job = report_jobs.get(report_id)
        if not job: raise HTTPException(404, "报告不存在")
        if job['status'] == 'done':
            return job['result']
        time.sleep(1)
    raise HTTPException(504, "报告生成超时，请稍后重试")


# ── Static files (frontend) ─────────────────────────────

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
        return {"message": "UniPulse API running. Run `npx vite build` first.", "api": True}

# ── Main ────────────────────────────────────────────────

if __name__ == "__main__":
    print("🚀 UniPulse 启动中...")
    print(f"   API: http://localhost:9999/api/health")
    print(f"   前端: http://localhost:9999")
    uvicorn.run(app, host="127.0.0.1", port=9999, log_level="info")
