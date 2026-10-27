from flask import Blueprint,render_template, jsonify,request
import psycopg
from psycopg.rows import dict_row
import os


tasks_bp = Blueprint("tasks",__name__)

tasks = [
{
    "id": 1,
    "title": "Learn Flask",
    "status": "todo"
},
{
    "id": 2,
    "title": "Build TaskHub",
    "status": "in_progress"
}
]
allowed_status =["todo","in_progress","done"]

def get_db_connection():
    return psycopg.connect(
        host="127.0.0.1",
        port=5432,
        dbname="taskhub",
        user="taskhub_user",
        password=os.environ["TASKHUB_DB_PASSWORD"],
        row_factory=dict_row
    )



@tasks_bp.route("/tasks", methods=["GET"])
def get_tasks():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM tasks")
            tasks = cur.fetchall()
    return jsonify(tasks),200

@tasks_bp.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT*FROM tasks WHERE id = %s',(task_id,))
            task = cur.fetchone()
    if task is None:
        return jsonify("not found"),404
    return jsonify(task),200
   


@tasks_bp.route("/tasks",methods=["POST"])
def post_task():
    data = request.get_json()
    title = data.get("title")
    status = data.get('status')
    if not isinstance(data, dict) or not isinstance(data.get("title"),str ):
        return jsonify({"error": "JSON object required"}), 400
   
    
    if not data.get("title").strip() or data.get("status") not in allowed_status:

        return jsonify("invalid: bad request"),400
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO tasks(title, status) VALUES (%s,%s) RETURNING id,title,status",(title,status))
            new_task = cur.fetchone()
    return jsonify(new_task),201




@tasks_bp.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.get_json()

    title = data.get("title")
    status = data.get("status")

    if not isinstance(title,str) or not title.strip() :
        return jsonify("bad request"),400

    if status not in allowed_status:
        return jsonify("bad request"),400
    
    title = title.strip()

    with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE tasks 
                    SET title=%s,status=%s 
                    WHERE id = %s 
                    RETURNING id,title,status
                    """,
                    (title,status,task_id)
                ) 
                updated_task = cur.fetchone()
    if updated_task is None:
            return jsonify("not found"),404         
                
    return jsonify(updated_task),200


@tasks_bp.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM tasks WHERE id = %s RETURNING id, title,status",(task_id,))
            deleted_task = cur.fetchone()
    if deleted_task is None:
        return jsonify({"error":"not found"},404)
    return jsonify(deleted_task),204

  
