from datetime import datetime

from flask import request

from app import db
from app.models import User
from app.models import History


def get_ip() -> str:
    return request.headers.get("X-Forwarded-For", request.remote_addr)


def create_history(user: User) -> History:
    history = History()
    history.user_id = user.id
    history.created_at = datetime.now()
    history.ip = get_ip()
    history.user_agent = request.user_agent

    db.session.add(history)
    db.session.commit()
    return history
