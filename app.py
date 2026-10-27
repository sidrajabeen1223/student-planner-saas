from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from pathlib import Path

app = Flask(__name__)
DB_PATH = Path(__file__).with_name("planner.db")

def get_db():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection

def init_db():
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                subject TEXT NOT NULL DEFAULT 'General',
                due_date TEXT,
                done INTEGER NOT NULL DEFAULT 0
            )
        """)

@app.route("/")
def index():
    with get_db() as db:
        tasks = db.execute(
            "SELECT * FROM tasks ORDER BY done ASC, due_date ASC, id DESC"
        ).fetchall()
    total = len(tasks)
    completed = sum(task["done"] for task in tasks)
    return render_template(
        "index.html", tasks=tasks, total=total, completed=completed,
        pending=total-completed
    )

@app.route("/add", methods=["POST"])
def add_task():
    title = request.form.get("title", "").strip()
    subject = request.form.get("subject", "General").strip() or "General"
    due_date = request.form.get("due_date", "").strip()
    if title:
        with get_db() as db:
            db.execute(
                "INSERT INTO tasks (title, subject, due_date) VALUES (?, ?, ?)",
                (title, subject, due_date or None)
            )
    return redirect(url_for("index"))

@app.route("/toggle/<int:task_id>", methods=["POST"])
def toggle_task(task_id):
    with get_db() as db:
        db.execute(
            "UPDATE tasks SET done = CASE done WHEN 0 THEN 1 ELSE 0 END WHERE id = ?",
            (task_id,)
        )
    return redirect(url_for("index"))

@app.route("/delete/<int:task_id>", methods=["POST"])
def delete_task(task_id):
    with get_db() as db:
        db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    return redirect(url_for("index"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
