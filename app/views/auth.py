from hashlib import sha512
from datetime import datetime

from flask import Blueprint
from flask import session
from flask import request
from flask import redirect
from flask import url_for
from flask import render_template

from app import db
from app.models import User
from app.history import create_history
from app.login_session import create_session
from app.login_session import login_block
from app.email import test_email_with_dns
from app.email import EmailVerifyFail

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.get("/logout")
def logout():
    session.clear()
    return redirect("/")


@bp.get("/sign-in")
@login_block
def sign_in():
    return render_template(
        "auth/sign-in.html"
    )


@bp.post("/sign-in")
@login_block
def sign_in_post():
    try:
        email = request.form['email']
        password = request.form['password']
    except KeyError:
        return redirect(url_for("auth.sign_in", error="이메일과 비밀번호를 입력해주세요."))

    user = User.query.filter_by(
        email=email,
        password=sha512(password.encode()).hexdigest()
    ).first()

    if user is None:
        return redirect(url_for("auth.sign_in", error="이메일 또는 비밀번호가 일치하지 않습니다."))

    print(user.id)

    history = create_history(user=user)
    create_session(user=user, history=history)

    return redirect(url_for("index.quiz_list"))


@bp.get("/sign-up")
@login_block
def sign_up():
    return render_template(
        "auth/sign-up.html"
    )


@bp.post("/sign-up")
@login_block
def sign_up_post():
    try:
        email = request.form['email']
        password = request.form['password']
    except KeyError:
        return redirect(url_for("auth.sign_up", error="이메일과 비밀번호를 입력해주세요."))

    try:
        test_email_with_dns(email=email)
    except EmailVerifyFail as e:
        return redirect(url_for("auth.sign_up", error=e.message))

    user = User()
    user.email = email
    user.password = sha512(password.encode()).hexdigest()
    user.is_admin = False
    user.created_at = datetime.now()

    db.session.add(user)
    db.session.commit()

    return redirect(url_for("auth.sign_up_finished"))


@bp.get("/sign-up-finished")
def sign_up_finished():
    return render_template(
        "auth/sign_up_finished.html"
    )
