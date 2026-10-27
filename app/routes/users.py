from flask import Blueprint,render_template

users_bp = Blueprint(__name__)

@users_bp.route("/users")
def index():
    return render_template("TaskHub Tasks Page.html")