from flask import Blueprint,render_template, jsonify,request
from app.db import get_db_connection 
from app.auth_utils import jwt_required

tasks_bp = Blueprint("tasks",__name__)
allowed_status =["todo", "in_progress","done"]

def validate_task_data(data):
     if not isinstance(data,dict):
          return None,"Json body must be an object"

     title = data.get("title")
     status = data.get("status","todo")

     if not isinstance(title,str):
          return None, "Title must be a string"

     title = title.strip()
     if not title:
          return None, "Title can not be empty"
     if len(title) >200:
            return None, "Title cannot exceed 200 characters"
     if not status in allowed_status:
            return None, "Invalid status"

     return {"title":title,"status":status}, None
     

@tasks_bp.route("/tasks", methods=["GET"])
@jwt_required
def get_tasks():
    sort = request.args.get("sort", default="asc")
    status = request.args.get("status")
    page = request.args.get("page", default=1, type=int)
    limit = request.args.get("limit", default=10, type=int)

    # 排序白名单验证
    if sort not in ("asc", "desc"):
        return jsonify({"error": "Invalid sort"}), 400

    # 状态白名单验证
    if status is not None and status not in ("todo", "in_progress", "done"):
        return jsonify({"error": "Invalid status"}), 400

    # 分页参数验证
    if page < 1:
        return jsonify({"error": "Invalid page"}), 400

    if limit < 1 or limit > 100:
        return jsonify({"error": "Invalid limit"}), 400

    order = "ASC" if sort == "asc" else "DESC"
    offset = (page - 1) * limit

    with get_db_connection() as conn:
        with conn.cursor() as cur:

            # 查询任务
            if status is not None:
                cur.execute(
                    f"""
                    SELECT * FROM tasks
                    WHERE status = %s
                    ORDER BY id {order}
                    LIMIT %s OFFSET %s
                    """,
                    (status, limit, offset)
                )
            else:
                cur.execute(
                    f"""
                    SELECT * FROM tasks
                    ORDER BY id {order}
                    LIMIT %s OFFSET %s
                    """,
                    (limit, offset)
                )

            tasks = cur.fetchall()

            # 统计符合条件的任务总数
            if status is not None:
                cur.execute(
                    "SELECT COUNT(*) AS total FROM tasks WHERE status = %s",
                    (status,)
                )
            else:
                cur.execute(
                    "SELECT COUNT(*) AS total FROM tasks"
                )

            result = cur.fetchone()
            total = result["total"]

            total_pages = (total + limit - 1) // limit

    return jsonify({
        "tasks": tasks,
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": total_pages
    }), 200

@tasks_bp.route("/tasks/<int:task_id>", methods=["GET"])
@jwt_required
def get_task(task_id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT*FROM tasks WHERE id = %s',(task_id,))
            task = cur.fetchone()
    if task is None:
        return jsonify("not found"),404
    return jsonify(task),200
   


@tasks_bp.route("/tasks",methods=["POST"])
@jwt_required
def post_task():
    data = request.get_json(silent=True)
    task_data,error = validate_task_data(data)
   
    if error:
         return jsonify({"error":error}),400
    
    title = task_data["title"]
    status = task_data['status']
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO tasks(title, status) VALUES (%s,%s) RETURNING id,title,status",(title,status))
            new_task = cur.fetchone()
    return jsonify(new_task),201




@tasks_bp.route("/tasks/<int:task_id>", methods=["PUT"])
@jwt_required
def update_task(task_id):
    data = request.get_json(silent=True)
    task_data,error = validate_task_data(data)

    if error:
         return jsonify({"error":error}),400

    
    title = task_data["title"]
    status =task_data["status"]
 

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

@tasks_bp.route("/tasks/<int:task_id>", methods=["PATCH"])
@jwt_required
def patch_task(task_id):
    data= request.get_json(silent=True)

    if not isinstance(data,dict):
        return jsonify({"error":"bad request"}), 400
    if not data or not any(key in data for key in("title","status")):
        return jsonify({"error":"no fields to update"}),400

    if "title" in data:
        title = data["title"]
         
   
        if not isinstance(title,str):
              return jsonify({"error":"Bad request"}),400
    
        title = title.strip()
        if not title or len(title) > 200:
            return jsonify({"error":"Bad request"}),400
    
    if "status" in data:
         status = data["status"]

         if status not in allowed_status:
              return jsonify({"error":"Invalid status"}),400

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            if "title" in data and "status" in data:
                cur.execute("UPDATE tasks SET title = %s, status = %s WHERE id = %s RETURNING id,title,status",(title,status,task_id))
            elif "status" in data:
                cur.execute("UPDATE tasks SET status = %s WHERE id = %s RETURNING id,title,status",(status,task_id))
            else:
                 cur.execute("UPDATE tasks SET title = %s WHERE id = %s RETURNING id,title,status",(title,task_id)) 

            updated_task = cur.fetchone()
            if updated_task is None:
                return jsonify("not found"),404
            return jsonify(updated_task), 200


@tasks_bp.route("/tasks/<int:task_id>", methods=["DELETE"])
@jwt_required
def delete_task(task_id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM tasks WHERE id = %s RETURNING id",(task_id,))
            deleted_task = cur.fetchone()
    if deleted_task is None:
        return jsonify({"error":"not found"}),404
    return "",204

  
