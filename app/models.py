from app import db


class User(db.Model):
    id = db.Column(
        db.Integer,
        unique=True,
        primary_key=True,
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(128),
        nullable=False
    )

    is_admin = db.Column(
        db.Boolean,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
    )


class History(db.Model):
    id = db.Column(
        db.Integer,
        unique=True,
        primary_key=True,
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
    )

    ip = db.Column(
        db.String(128),
        nullable=False
    )

    user_agent = db.Column(
        db.String(128),
        nullable=False
    )


class Quiz(db.Model):
    id = db.Column(
        db.Integer,
        unique=True,
        primary_key=True,
        nullable=False
    )

    owner_id = db.Column(
        db.Integer,
        nullable=False
    )

    is_public = db.Column(
        db.Boolean,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
    )

    finished_at = db.Column(
        db.DateTime,
        nullable=True,
    )

    title = db.Column(
        db.String(128),
        nullable=False
    )

    text = db.Column(
        db.Text,
        nullable=False
    )

    @property
    def owner(self) -> str:
        return User.query.filter_by(
            id=self.owner_id
        ).with_entities(
            User.email
        ).first().email

    @property
    def joined_people(self) -> int:
        return QuizSession.query.filter_by(
            quiz_id=self.id
        ).count()


class Question(db.Model):
    id = db.Column(
        db.Integer,
        unique=True,
        primary_key=True,
        nullable=False
    )

    quiz_id = db.Column(
        db.Integer,
        nullable=False
    )

    # app.types.QuestionType
    type = db.Column(
        db.Integer,
        nullable=False
    )

    text = db.Column(
        db.Text,
        nullable=False
    )

    options = db.Column(
        db.Text,
        nullable=False
    )

    answer = db.Column(
        db.Text,
        nullable=False
    )

    score = db.Column(
        db.Integer,
        nullable=False
    )


class QuizSession(db.Model):
    id = db.Column(
        db.Integer,
        unique=True,
        primary_key=True,
        nullable=False
    )

    quiz_id = db.Column(
        db.Integer,
        nullable=False
    )

    owner_id = db.Column(
        db.Integer,
        nullable=False
    )

    started_at = db.Column(
        db.DateTime,
        nullable=False,
    )

    finished_at = db.Column(
        db.DateTime,
        nullable=True,
    )


class Answer(db.Model):
    id = db.Column(
        db.Integer,
        unique=True,
        primary_key=True,
        nullable=False
    )

    owner_id = db.Column(
        db.Integer,
        nullable=False
    )

    quiz_id = db.Column(
        db.Integer,
        nullable=False
    )

    question_id = db.Column(
        db.Integer,
        nullable=False
    )

    answer = db.Column(
        db.Text,
        nullable=False
    )

    score = db.Column(
        db.Integer,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
    )

    @property
    def question_type(self) -> int:
        return Question.query.filter_by(
            id=self.question_id,
            quiz_id=self.quiz_id
        ).with_entities(
            Question.type
        ).first().type

    @property
    def max_score(self) -> int:
        return Question.query.filter_by(
            id=self.question_id,
            quiz_id=self.quiz_id
        ).with_entities(
            Question.score
        ).first().score
