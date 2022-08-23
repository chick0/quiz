from datetime import datetime

from user_agents import parse
from mistune import create_markdown

from app.types import QuestionType


def date_to_string(date: datetime) -> str:
    return date.strftime("%Y-%m-%d %H:%M")


def parse_user_agent(user_agent: str) -> str:
    ua = parse(user_agent)
    return str(ua)


def to_html(markdown: str) -> str:
    return create_markdown(
        escape=False,
        renderer="html",
        plugins=[
            'strikethrough',
            'footnotes',
            'table',
            'task_lists',
        ]
    )(markdown)


def parse_options(options: str) -> str:
    markdown = ""

    for line in [x.strip() for x in options.split("\n")]:
        sep = line.find(":")
        num = line[:sep]
        text = line[sep + 1:]
        markdown += f"{num}. {text}\n"

    return to_html(
        markdown=markdown
    )


def type_to_string(question_type: int) -> str:
    if question_type == QuestionType.OX.value:
        return "O/X"
    if question_type == QuestionType.MultipleChoice.value:
        return "객관식"
    if question_type == QuestionType.OX.value:
        return "주관식"
