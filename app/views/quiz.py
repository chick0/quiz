from datetime import datetime
from datetime import timedelta

from flask import Blueprint
from flask import request
from flask import redirect
from flask import url_for
from flask import render_template

from app import db
from app.models import User
from app.models import Quiz
from app.models import QuizSession
from app.login_session import LoginSession
from app.login_session import login_required

bp = Blueprint("quiz", __name__, url_prefix="/quiz")


@bp.route("/join/<int:quiz_id>", methods=['GET', 'POST'])
@login_required
def join(quiz_id: int, login_session: LoginSession):
    quiz = Quiz.query.filter_by(
        id=quiz_id
    ).first()

    if quiz is None:
        return redirect("/")

    if quiz.owner_id == login_session.user_id:
        return redirect(url_for("quiz.custom", quiz_id=quiz_id))

    if not quiz.is_public:
        return render_template(
            "quiz/cant-join.html",
            why="private"
        )

    if datetime.now() >= quiz.finished_at:
        return render_template(
            "quiz/cant-join.html",
            why="expired"
        )

    qz = QuizSession.query.filter_by(
        quiz_id=quiz_id,
        owner_id=login_session.user_id
    ).first()

    if qz is not None:
        if qz.finished_at is not None:
            return render_template(
                "quiz/cant-join.html",
                why="finished"
            )

        return redirect(url_for("question.restore", quiz_id=quiz_id))

    if request.method == "GET":
        return render_template(
            "quiz/join.html",
            quiz=quiz
        )
    else:
        del qz

        qz = QuizSession()
        qz.quiz_id = quiz.id
        qz.owner_id = login_session.user_id
        qz.started_at = datetime.now()

        db.session.add(qz)
        db.session.commit()

        return redirect(url_for("question.restore", quiz_id=quiz_id))


@bp.get("/create-new")
@login_required
def create_new(login_session: LoginSession):
    if User.query.filter_by(
        id=login_session.user_id
    ).with_entities(
        User.is_admin
    ).first().is_admin is False:
        return render_template(
            "quiz/cant-create.html"
        )

    return render_template(
        "quiz/create-new.html",
        default_finished_at=(datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    )


@bp.post("/create-new")
@login_required
def create_new_post(login_session: LoginSession):
    if User.query.filter_by(
        id=login_session.user_id
    ).with_entities(
        User.is_admin
    ).first().is_admin is False:
        return render_template(
            "quiz/cant-create.html"
        )

    quiz = Quiz()
    quiz.owner_id = login_session.user_id
    quiz.is_public = False
    quiz.created_at = datetime.now()

    try:
        quiz.finished_at = datetime.strptime(request.form['finished_at'], "%Y-%m-%d")
    except KeyError:
        quiz.finished_at = datetime.now() + timedelta(days=1)
    finally:
        quiz.finished_at = quiz.finished_at.replace(hour=23, minute=59, second=59)

    quiz.title = request.form.get("title", "제목 없는 퀴즈")[:128]
    quiz.text = request.form.get("text", "추가 설명이 없습니다.")

    db.session.add(quiz)
    db.session.commit()

    return redirect(url_for("quiz.custom", quiz_id=quiz.id))


@bp.get("/custom/<int:quiz_id>")
@login_required
def custom(quiz_id: int, login_session: LoginSession):
    quiz = Quiz.query.filter_by(
        id=quiz_id,
        owner_id=login_session.user_id
    ).first()

    if quiz is None:
        return redirect("/")

    return render_template(
        "quiz/custom.html",
        quiz=quiz
    )


@bp.post("/custom/<int:quiz_id>")
@login_required
def custom_post(quiz_id: int, login_session: LoginSession):
    quiz = Quiz.query.filter_by(
        id=quiz_id,
        owner_id=login_session.user_id
    ).first()

    if quiz is None:
        return redirect("/")

    quiz.is_public = request.form.get("is_public", "idk") == "on"

    try:
        quiz.finished_at = datetime.strptime(request.form['finished_at'], "%Y-%m-%d")
    except KeyError:
        quiz.finished_at = datetime.now() + timedelta(days=1)
    finally:
        quiz.finished_at = quiz.finished_at.replace(hour=23, minute=59, second=59)

    quiz.title = request.form.get("title", "제목 없는 퀴즈")[:128]
    quiz.text = request.form.get("text", "추가 설명이 없습니다.")

    db.session.commit()

    return redirect(url_for("quiz.custom", quiz_id=quiz_id))


@bp.get("/delete/<int:quiz_id>")
def delete(quiz_id: int):
    # TODO:WIP
    return "WIP"
