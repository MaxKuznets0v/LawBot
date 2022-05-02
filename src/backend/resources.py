from flask_restful import Resource, reqparse
from flask import request
import uuid
import hashlib
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from schema import User, Question, History_DB, create_all
from LawQA import LawBot


class MockBot:
    def __init__(self, gpu) -> None:
        pass

    def answer(self, query):
        return {"answers": [
            {"answer": "Глава государства",
            "meta": {"name": "Конституция", "law_name": "Конституция"}
            },
            {"answer": "Второй",
            "meta": {"name": "Первый", "law_name": "Закон"}
            }],
        }


class Chatbot(Resource):
    bot = LawBot(True, False)

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('question')
        args = parser.parse_args()
        question = args.get('question')
        if question is None:
            return "Question is not provided", 400
        resp = self.bot.answer(question)
        try:
            return {"answers": [elem.to_dict() for elem in resp['answers']]}, 200
        except:
            return resp, 200

engine = create_engine("sqlite:///uribot_data.db", echo=True)
create_all(engine)


class Register(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('login')
        parser.add_argument('password')
        args = parser.parse_args()
        login = args.get('login')
        password = args.get('password')
        if login is None or password is None:
            return "Credentials are not provided", 400

        with Session(engine) as session:
            user_id = session.query(User.id).filter_by(login=login).first()
            if user_id is None:
                user = User(id=str(uuid.uuid4()))
                while session.query(User.id).filter_by(id=user.id).first() is not None:
                    user.id = str(uuid.uuid4())

                user.login = login
                salt = str(uuid.uuid4())
                user.hash = hashlib.sha256(password.encode('utf-8') + salt.encode('utf-8')).hexdigest()
                user.salt = salt

                session.add(user)
                session.commit()
                return "Успешная регистрация", 201
            else:
                return "Пользователь с таким логином уже существует", 409


class Login(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('login')
        parser.add_argument('password')
        args = parser.parse_args()
        login = args.get('login')
        password = args.get('password')
        if login is None or password is None:
            return "Credentials are not provided", 400

        with Session(engine) as session:
            user = session.query(User.id, User.salt, User.hash).filter_by(login=login).first()
            if user is not None:
                salt = user[1]
                given_hash = hashlib.sha256(password.encode('utf-8') + salt.encode('utf-8')).hexdigest() 
                if given_hash == user[2]:
                    return user[0], 200
            return "Неверный логин или пароль", 404


class History(Resource):
    def post(self):
        args = request.get_json()
        user = args.get('user_id')
        query = args.get('query')
        answers = args.get('answers')
        if user is None:
            return "Необходима авторизация", 401
        if query is None or answers is None:
            return "Not all args are not provided", 400

        with Session(engine) as session:
            found = session.query(User.id).filter_by(id=user).first()
            if found is not None:
                user_id = found[0]
                q = Question(user=user_id, query=query)
                session.add(q)
                q_id = session.query(Question.id).order_by(Question.id.desc()).first()[0]
                for ans in answers:
                    a = History_DB(question=q_id, answer=ans['answer'], law_name=ans['meta']['law_name'], article=ans['meta']['name'])
                    session.add(a)
                session.commit()
                return "Вопрос сохранен", 201
            else:
                return "Пользователь не найден", 404

    def get(self):
        user = request.args.get('user_id')
        if user is None:
            return "User id is not provided", 400
        
        with Session(engine) as session:
            query = session.query(Question, History_DB).filter(Question.user == user).filter(Question.id == History_DB.question)
            records = query.all()
            res = list()
            questions = set()
            for question, answer in records:
                if question.id not in questions:
                    questions.add(question.id)
                    res.append({"id": question.id, "question": question.query, "answers": list()})
                res[-1]['answers'].append({'answer': answer.answer, 'meta': {'law_name': answer.law_name, 'name': answer.article}})          
            return res, 200

    def delete(self):
        args = request.get_json()
        user = args.get('user_id')
        question = args.get('question_id')
        
        if user is None or question is None:
            return "Not all args provided", 400
        
        with Session(engine) as session:
            q = session.query(Question).filter(Question.id == question)
            if q.first() is None:
                return "Вопрос не найден", 404
            q.delete()
            ans = session.query(History_DB).filter(History_DB.question == question)
            ans.delete()
            session.commit()
            return "Успешное удаление", 200
