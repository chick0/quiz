from os import environ

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import User


def main():
    print("* Enter user email to change user to admin user")
    email = input("user email = ")
    upgrade_user(email=email)


def upgrade_user(email: str):
    if "SQLALCHEMY_DATABASE_URI" not in environ:
        load_dotenv()

    engine = create_engine(environ['SQLALCHEMY_DATABASE_URI'])
    session = sessionmaker(bind=engine)()

    user: User = session.query(User).filter_by(
        email=email
    ).first()

    if user is None:
        print("* Undefined user!")
        session.close()
        print("* Quited.")
    else:
        if user.is_admin:
            print("[WARN] This user is already admin user. So this tool removed the admin permission.")
            user.is_admin = False
        else:
            user.is_admin = True

        session.commit()
        session.close()

        print("* Finished")


if __name__ == "__main__":
    main()
