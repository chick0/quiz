from flask import Blueprint
from flask import render_template

from app.models import History
from app.login_session import LoginSession
from app.login_session import login_required

bp = Blueprint("user", __name__, url_prefix="/user")


@bp.get("/login-history")
@login_required
def login_history(login_session: LoginSession):
    history_list = History.query.filter_by(
        user_id=login_session.user_id
    ).order_by(
        History.created_at.desc()
    ).limit(100).all()

    return render_template(
        "user/login-history.html",
        history_list=history_list,
        login_session=login_session
    )
