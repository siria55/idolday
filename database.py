from sqlalchemy import create_engine, select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

SQLALCHEMY_DATABASE_URL = 'mysql+pymysql://hotdog:TOAItoai1234@rm-2ze8try6287fyk6j3go.mysql.rds.aliyuncs.com:3306/idolday'
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)

session_factory = sessionmaker(bind=engine)
# 创建 scoped_session
db_session = scoped_session(session_factory)
Session = scoped_session(sessionmaker(bind=engine))

# 依赖项
def get_db():
    db = db_session()
    try:
        yield db
    finally:
        db.close()
        db_session.remove()

def get_db_non_async():
    db = db_session()
    return db

real_base = declarative_base()

class Base(real_base):
    __abstract__ = True
    @classmethod
    def get(cls, **kwargs):
        session = Session()
        stmt = select(cls).filter_by(**kwargs)
        return session.scalars(stmt).first()

    @classmethod
    def gets(cls):
        session = Session()
        return session.scalars(select(cls)).all()

    @classmethod
    def create(cls, **kwargs):
        session = Session()
        obj = cls(**kwargs)
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj
