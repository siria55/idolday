from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, select
from database import Base, Session

class Xox(Base):
    __tablename__ = 'xox'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    group_id = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f'<Xox {self.id} {self.name} {self.group_id} {self.created_at}>'

    @property
    def group(self):
        group = Session().scalars(select(XoxGroup).filter_by(id=self.group_id)).first()
        return group

    @property
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'group_id': self.group.id,
            'group_name': self.group.name,
            'management_company_id': self.group.management_company_id,
            'management_company_name': self.group.management_company.name,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        }


class XoxGroup(Base):
    __tablename__ = 'xox_group'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    management_company_id = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f'<XoxGroup {self.id} {self.name} {self.management_company_id} {self.created_at}>'
    
    @property
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'management_company_id': self.management_company_id,
            'management_company_name': self.management_company.name,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        }

    @property
    def management_company(self):
        management_company = Session().scalars(select(ManagementCompany).filter_by(id=self.management_company_id)).first()
        return management_company

    @property
    def xoxs(self):
        xoxs = Session().scalars(select(Xox).filter_by(group_id=self.id)).all()
        return xoxs


class ManagementCompany(Base):
    __tablename__ = 'management_company'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    created_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f'<ManagementCompany {self.id} {self.name} {self.created_at}>'

    @property
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        }

    @property
    def groups(self):
        groups = Session().scalars(select(XoxGroup).filter_by(management_company_id=self.id)).all()
        return groups

    @property
    def xoxs(self):
        xoxs = []
        for group in self.groups:
            xoxs += group.xoxs
        return xoxs
