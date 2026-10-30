from flask import Blueprint, request,jsonify
from pydantic import ValidationError
from app.schemas import RegisterRequest,LoginRequest
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
from app.models.models import User
from app.orm import SessionLocal
from sqlalchemy import select,or_
from app.jwt_utils import create_access_token
from app.auth_utils import jwt_required

auth_bp = Blueprint("auth",__name__)

from flask import g
from app.auth_utils import jwt_required

@auth_bp.route("/auth/me", methods=["GET"])
@jwt_required
def get_current_user():
    return jsonify({
        "message": "Token is valid",
        "user_id": g.current_user_id
    }), 200
 
@auth_bp.route("/auth/login",methods=["POST"])

def login():
    data = request.get_json(silent=True)
    if not isinstance(data,dict):
        return ({"error":"JSON object required"}),400
    try:
        login_data = LoginRequest.model_validate(data)
    except ValidationError as error:
        return jsonify({
            "error":"Invalid login error",
            "details":error.errors(
                include_input=False,
                include_context=False
        )
        }),400

    account = login_data.account
    password = login_data.password

    

    

    with SessionLocal() as session:

        stmt = select(User).where(or_(User.username == account,User.email == account))
        user = session.scalar(stmt)
       
        if user is None:
            return jsonify({"error":"Invalid credentials"}),401
        is_correct = check_password_hash(user.password_hash, password)
        if not is_correct:
            return jsonify({"error":"invalid credentials"}),401
        
        access_token = create_access_token(user.id)
        return jsonify({"message":"Login successful",
                        "access_token":access_token,
                        "token_type":"Bearer",
                        "user":{
                            "id":user.id,
                            "username":user.username,
                            "email":user.email
                        }}),200
        

@auth_bp.route("/auth/register", methods=["POST"])
def register():
    data = request.get_json(silent=True)
    if not isinstance(data,dict):
        return jsonify({"error":"JSON object required"}),400

    try:
        userdata = RegisterRequest.model_validate(data)

    except ValidationError as error:
        return jsonify({
            "error":"validation error",
            "details":error.errors(
                include_context=False,
                include_input=False
            )
        }),400

    username = userdata.username
    email = userdata.email
    password = userdata.password
    hashed_password = generate_password_hash(password)

    new_user = User(
        username=username,
        email=email,
        password_hash = hashed_password
    )

    try:
        with SessionLocal() as session:
            session.add(new_user)
            session.commit()
            session.refresh(new_user)

            user={
                "id":new_user.id,
                "username":new_user.username,
                "email":new_user.email}
    except IntegrityError:
        return jsonify({
            "error":"Username or email already exists"
        }),409

    return jsonify({"message":"User registered successfully","user":user
    }),201