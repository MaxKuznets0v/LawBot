from flask import Flask
from flask_cors import CORS, cross_origin
from flask_restful import Api
from resources import Chatbot, Register, Login, History


if __name__ == '__main__':
    app = Flask(__name__)
    api = Api(app)
    CORS(app, origins="http://localhost:3000", allow_headers=["Content-Type", "Access-Control-Allow-Credentials"])
    api.add_resource(Chatbot, '/question', '/question/')
    api.add_resource(Register, '/register', '/register/')
    api.add_resource(Login, '/login', '/login/')
    api.add_resource(History, '/history', '/history/')
    app.run('0.0.0.0', debug=False)
