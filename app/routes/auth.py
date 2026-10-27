from flask import Blueprint,render_template

auth_bp = Blueprint(__name__)

@auth_bp.route("/login")
def index():
    return render_template("TaskHub Tasks Page.html")

@auth_bp.route("/register")
def index():
    return render_template("TaskHub Tasks Page.html")