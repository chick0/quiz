from flask import Blueprint
from flask import render_template

from app.models import Quiz
from app.login_session import get_session

bp = Blueprint("index", __name__, url_prefix="/")


def safe_get_session():
    try:
        return get_session()
    except (KeyError, Exception):
        return None


@bp.get("")
def quiz_list():
    return render_template(
        "index/quiz_list.html",
        login_session=safe_get_session(),
        quiz_list=Quiz.query.order_by(
            Quiz.created_at.desc()
        ).all()
    )
