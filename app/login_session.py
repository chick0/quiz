from typing import NamedTuple
from datetime import datetime
from datetime import timedelta
from functools import wraps

from flask import session
from flask import redirect
from flask import url_for

from app.models import User
from app.models import History


class LoginSession(NamedTuple):
    user_id: int
    history_id: int
    user_agent: str
    expired_at: int


class LoginFail(Exception):
    def __init__(self, message: str):
        super().__init__()
        self.message: str = message


def create_session(user: User, history: History) -> LoginSession:
    login_session = LoginSession(
        user_id=user.id,
        history_id=history.id,
        user_agent=history.user_agent,
        expired_at=int((datetime.now() + timedelta(hours=6)).timestamp())
    )

    session['login'] = login_session._asdict()
    return login_session


def get_session() -> LoginSession:
    login_session = LoginSession(**session['login'])

    now = datetime.now().timestamp()

    if now > login_session.expired_at:
        raise LoginFail(message="만료된 세션 입니다.")
    else:
        return login_session


def login_block(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        try:
            get_session()
        except (KeyError, LoginFail):
            return f(*args, **kwargs)

        return redirect(url_for("index.quiz_list"))

    return decorator


def login_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        try:
            login_session = get_session()
        except KeyError:
            return redirect(url_for("auth.sign_in"))

        kwargs.update({"login_session": login_session})
        return f(*args, **kwargs)

    return decorator
