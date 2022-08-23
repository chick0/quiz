from functools import wraps
from datetime import datetime

from flask import redirect
from flask import url_for

from app.models import Quiz
from app.models import QuizSession
from app.models import Question
from app.models import Answer
from app.login_session import LoginSession


def check_before_solve(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        login_session: LoginSession = kwargs['login_session']

        quiz = Quiz.query.filter_by(
            id=kwargs['quiz_id']
        ).with_entities(
            Quiz.id,
            Quiz.is_public,
            Quiz.finished_at
        ).first()

        # 퀴즈 비공개
        if quiz.is_public is False:
            return redirect(url_for("index.quiz_list"))

        quiz_session = QuizSession.query.filter_by(
            quiz_id=quiz.id,
            owner_id=login_session.user_id
        ).filter(
            QuizSession.finished_at != None
        ).first()

        # 퀴즈 제출 여부 검사
        if quiz_session is not None:
            return redirect(url_for("result.panel", quiz_id=quiz.id))

        # 퀴즈 마감 검사
        if datetime.now() >= quiz.finished_at:
            return "해당 퀴즈는 마감되었습니다. 더 이상 문제를 풀수없습니다."

        return f(*args, **kwargs)

    return decorator
