from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey


Base = declarative_base()


class User(Base):
    __tablename__ = 'User'

    id = Column(String(40), primary_key=True)
    login = Column(String, nullable=False, unique=True)
    salt = Column(String(20), nullable=False)
    hash = Column(String, nullable=False)


class Question(Base):
    __tablename__ = 'Question'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user = Column(String(40), ForeignKey("User.id"), nullable=False)
    query = Column(String, nullable=False)


class History_DB(Base):
    __tablename__ = 'History'

    id = Column(Integer, primary_key=True, autoincrement=True)
    question = Column(Integer, ForeignKey("Question.id"), nullable=False)
    answer = Column(String, nullable=False)
    law_name = Column(String, nullable=False)
    article = Column(String, nullable=False)


def create_all(engine):
    Base.metadata.create_all(engine)
