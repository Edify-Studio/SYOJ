# -*- coding: utf-8 -*-

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

oj = Flask(__name__)
oj.config.from_object("config")
oj.config['SQLALCHEMY_COMMIT_ON_TEARDOWN']=True  # 设置这一项是每次请求结束后都会自动提交数据库中的变动
db = SQLAlchemy(oj)

from .views import *
from .models import *
from .controller import *
# import views, models, controller
