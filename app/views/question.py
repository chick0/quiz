from datetime import datetime

from flask import Blueprint
from flask import request
from flask import redirect
from flask import url_for
from flask import render_template

from app import db
from app.models import Quiz
from app.models import QuizSession
from app.models import Question
from app.models import Answer
from app.login_session import LoginSession
from app.login_session import login_required
from app.question_utils import check_before_solve
from app.quiz_utils import check_quiz_owner
from app.types import QuestionType

bp = Blueprint("question", __name__, url_prefix="/question")


@bp.get("/restore/<int:quiz_id>")
@login_required
def restore(quiz_id: int, login_session: LoginSession):
    last_question = Answer.query.filter_by(
        owner_id=login_session.user_id,
        quiz_id=quiz_id
    ).order_by(
        Answer.question_id.desc()
    ).with_entities(
        Answer.question_id
    ).first()

    if last_question is not None:
        next_question = Question.query.filter(
            Question.id > last_question.question_id
        ).order_by(
            Question.id.asc()
        ).with_entities(
            Question.id
        ).first()

        if next_question is None:
            qz = QuizSession.query.filter_by(
                quiz_id=quiz_id,
                owner_id=login_session.user_id
            ).first()

            qz.finished_at = datetime.now()
            db.session.commit()

            return redirect(url_for("result.panel", quiz_id=quiz_id))

        next_question_id = next_question.id
    else:
        first_question = Question.query.filter_by(
            quiz_id=quiz_id
        ).order_by(
            Question.id.asc()
        ).with_entities(
            Question.id
        ).first()

        next_question_id = first_question.id

    return redirect(url_for("question.solve", quiz_id=quiz_id, question_id=next_question_id))


@bp.get("/solve/<int:quiz_id>/<int:question_id>")
@login_required
@check_before_solve
def solve(quiz_id: int, question_id: int, login_session: LoginSession):
    return render_template(
        "question/solve.html",
        question=Question.query.filter_by(
            id=question_id,
            quiz_id=quiz_id
        ).first()
    )


@bp.post("/solve/<int:quiz_id>/<int:question_id>")
@login_required
@check_before_solve
def solve_post(quiz_id: int, question_id: int, login_session: LoginSession):
    question = Question.query.filter_by(
        id=question_id,
        quiz_id=quiz_id
    ).with_entities(
        Question.type,
        Question.answer,
        Question.score
    ).first()

    answer = Answer()
    answer.owner_id = login_session.user_id
    answer.quiz_id = quiz_id
    answer.question_id = question_id
    answer.created_at = datetime.now()

    try:
        answer.answer = request.form[f'answer-{question.type}'].strip()

        if len(answer.answer) == 0:
            raise ValueError

        if question.type == 0:
            if answer.answer == "O" or answer.answer == "X":
                pass
            else:
                raise TypeError
    except (KeyError, ValueError, Exception):
        return redirect(url_for("question.solve", quiz_id=quiz_id, question_id=question_id, error="정답을 입력해주세요."))

    if question.type == 0 or question.type == 1:
        if question.answer == answer.answer:
            answer.score = question.score
        else:
            answer.score = 0
    else:
        answer.score = 0

    db.session.add(answer)
    db.session.commit()

    return redirect(url_for("question.restore", quiz_id=quiz_id))


@bp.get("/manage/<int:quiz_id>")
@login_required
@check_quiz_owner
def manage(quiz_id: int, login_session: LoginSession):
    return render_template(
        "question/manage/list.html",
        quiz_id=quiz_id,
        question_list=Question.query.filter_by(
            quiz_id=quiz_id
        ).order_by(
            Question.id.asc()
        ).all()
    )


@bp.get("/manage/<int:quiz_id>/create-new")
@login_required
@check_quiz_owner
def manage_new(quiz_id: int, login_session: LoginSession):
    return render_template(
        "question/manage/create-new.html",
        quiz_id=quiz_id
    )


@bp.post("/manage/<int:quiz_id>/create-new")
@login_required
@check_quiz_owner
def manage_new_post(quiz_id: int, login_session: LoginSession):
    question = Question()
    question.quiz_id = quiz_id

    try:
        question.type = int(request.form['type'])
    except (KeyError, ValueError):
        return redirect(url_for("question.manage_new", quiz_id=quiz_id, error="프로젝트 형식이 올바르지 않습니다."))

    try:
        question.text = request.form['text'].strip()
        if len(question.text) == 0:
            raise ValueError
    except (KeyError, ValueError):
        return redirect(url_for("question.manage_new", quiz_id=quiz_id, error="문제를 입력해야 합니다."))

    if question.type == QuestionType.MultipleChoice.value:
        question.options = request.form.get("options-1").strip()
    else:
        question.options = ""

    question.answer = request.form[f'answer-{question.type}']

    try:
        question.score = int(request.form.get("score", "1"))
    except ValueError:
        question.score = 1

    db.session.add(question)
    db.session.commit()

    return redirect(url_for("question.manage_new", quiz_id=quiz_id, alert="새로운 문항이 등록되었습니다."))


@bp.get("/manage/<int:quiz_id>/<int:question_id>/delete")
@login_required
@check_quiz_owner
def manage_delete(quiz_id: int, question_id: int, login_session: LoginSession):
    Question.query.filter_by(
        id=question_id,
        quiz_id=quiz_id,
    ).delete()

    db.session.commit()

    return redirect(url_for("question.manage", quiz_id=quiz_id, alert="해당 선택지는 삭제되었습니다."))


@bp.get("/manage/<int:quiz_id>/<int:question_id>")
@login_required
@check_quiz_owner
def manage_edit(quiz_id: int, question_id: int, login_session: LoginSession):
    return


@bp.post("/manage/<int:quiz_id>/<int:question_id>")
@login_required
@check_quiz_owner
def manage_edit_post(quiz_id: int, question_id: int, login_session: LoginSession):
    return
