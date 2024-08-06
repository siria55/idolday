from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

SQLALCHEMY_DATABASE_URL = 'mysql+pymysql://hotdog:TOAItoai1234@rm-2ze8try6287fyk6j3go.mysql.rds.aliyuncs.com:3306/bothub'
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)

session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)
# 创建 scoped_session
db_session = scoped_session(session_factory)

# 依赖项
def get_db():
    db = db_session()
    try:
        yield db
    finally:
        print('in fanalli')
        db.close()
        db_session.remove()

Base = declarative_base()
