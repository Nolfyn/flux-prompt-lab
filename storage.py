import os
import sqlite3
import uuid
import json
from datetime import datetime

DB_PATH = os.getenv("STORAGE_DB", "storage.db")
OUTPUTS_DIR = "outputs"
os.makedirs(OUTPUTS_DIR, exist_ok=True)


def _conn():
    """Открыть соединение с БД."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _ensure_table():
    """Создать таблицу saved_prompts, если её ещё нет."""
    sql = """
    CREATE TABLE IF NOT EXISTS saved_prompts (
        id TEXT PRIMARY KEY,
        name TEXT,
        prompt TEXT,
        negative_prompt TEXT,
        lora_name TEXT,
        lora_id TEXT,
        lora_weight REAL,
        slider_value INTEGER,
        llm_input TEXT,
        llm_raw_response TEXT,
        tags TEXT,
        created_at TEXT
    );
    """
    conn = _conn()
    conn.execute(sql)
    conn.commit()
    conn.close()


# Создаём таблицу при импорте модуля (MVP)
_ensure_table()


def save_prompt(record):
    """Сохранить запись промпта."""
    rid = record.get("id") or str(uuid.uuid4())
    name = record.get("name") or ""
    prompt = record.get("prompt") or ""
    negative = record.get("negative_prompt") or ""
    lora_name = record.get("lora_name") or ""
    lora_id = record.get("lora_id") or ""
    lora_weight = record.get("lora_weight")
    slider = record.get("slider_value")
    llm_input = record.get("llm_input") or ""
    llm_raw = record.get("llm_raw_response") or ""
    tags = record.get("tags") or []
    if isinstance(tags, str):
        tags_list = [t.strip() for t in tags.split(",") if t.strip()]
    else:
        tags_list = list(tags)
    tags_json = json.dumps(tags_list, ensure_ascii=False)
    created = record.get("created_at") or datetime.now().isoformat() + "Z"

    sql = """
    INSERT OR REPLACE INTO saved_prompts
    (id, name, prompt, negative_prompt, lora_name, lora_id, lora_weight,
    slider_value, llm_input, llm_raw_response, tags, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    params = (
        rid,
        name,
        prompt,
        negative,
        lora_name,
        lora_id,
        lora_weight,
        slider,
        llm_input,
        llm_raw,
        tags_json,
        created,
    )
    conn = _conn()
    conn.execute(sql, params)
    conn.commit()
    conn.close()
    return rid


def get_prompt(record_id):
    """Получить запись по id."""
    conn = _conn()
    cur = conn.execute(
        "SELECT * FROM saved_prompts WHERE id = ? LIMIT 1", (record_id,)
    )
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    d = dict(row)
    try:
        d["tags"] = json.loads(d.get("tags") or "[]")
    except Exception:
        d["tags"] = []
    return d


def list_prompts(limit=100):
    """Вернуть список последних сохранённых промптов."""
    conn = _conn()
    cur = conn.execute(
        "SELECT * FROM saved_prompts ORDER BY created_at DESC LIMIT ?",
        (limit,),
    )
    rows = cur.fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        try:
            d["tags"] = json.loads(d.get("tags") or "[]")
        except Exception:
            d["tags"] = []
        result.append(d)
    return result


def delete_prompt(record_id):
    """Удалить запись по id."""
    conn = _conn()
    cur = conn.execute("DELETE FROM saved_prompts WHERE id = ?", (record_id,))
    conn.commit()
    conn.close()
    return cur.rowcount > 0


def export_prompt_json(record_id, filename=None):
    """Экспортировать запись в JSON-файл в папке outputs/."""
    rec = get_prompt(record_id)
    if not rec:
        return None
    if not filename:
        filename = f"{record_id}.json"
    outpath = os.path.join(OUTPUTS_DIR, filename)
    with open(outpath, "w", encoding="utf-8") as f:
        json.dump(rec, f, ensure_ascii=False, indent=2)
    return outpath
