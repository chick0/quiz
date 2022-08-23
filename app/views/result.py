from flask import Blueprint
from flask import render_template
from flask import redirect
from flask import url_for

from app.models import Question
from app.models import QuizSession
from app.models import Answer
from app.login_session import LoginSession
from app.login_session import login_required

bp = Blueprint("result", __name__, url_prefix="/result")


@bp.get("/<int:quiz_id>")
@login_required
def panel(quiz_id: int, login_session: LoginSession):
    qz = QuizSession.query.filter_by(
        quiz_id=quiz_id,
        owner_id=login_session.user_id
    ).first()

    if qz.finished_at is None:
        return redirect(url_for("question.restore", quiz_id=quiz_id))

    answer_list = Answer.query.filter_by(
        owner_id=login_session.user_id,
        quiz_id=quiz_id
    ).order_by(
        Answer.question_id.asc()
    ).all()

    return render_template(
        "result/panel.html",
        answer_list=answer_list,
        score=sum(x.score for x in answer_list),
        max_score=sum(x.score for x in Question.query.filter_by(
            quiz_id=quiz_id
        ).with_entities(
            Question.score
        ).all())
    )
