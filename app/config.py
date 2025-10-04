import os

BASEDIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = "18102007"
    SQLALCHEMY_DATABASE_URI = "mysql+mysqldb://yuri:18102007@localhost:3306/cloudserver"
