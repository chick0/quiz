from functools import wraps

from app.models import Quiz
from app.login_session import LoginSession


def check_quiz_owner(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        login_session: LoginSession = kwargs['login_session']

        quiz = Quiz.query.filter_by(
            id=kwargs['quiz_id']
        ).with_entities(
            Quiz.owner_id,
            Quiz.is_public,
        ).first()

        if quiz.is_public:
            return "진행중인 퀴즈의 문항은 수정 할 수 없습니다."

        if quiz.owner_id == login_session.user_id:
            return f(*args, **kwargs)
        else:
            return "해당 퀴즈의 소유자가 아닙니다."

    return decorator
