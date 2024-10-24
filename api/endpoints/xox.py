
from fastapi import APIRouter

from api import  res_json

from models.xox import Xox, XoxGroup, ManagementCompany

router = APIRouter()

@router.get('/xoxs')
def xoxs():
    """
    获取所有 xox
    """
    xoxs = Xox.gets()
    data = [xox.to_dict for xox in xoxs]
    print(xoxs)
    return res_json({
        'xoxs': data,
    })

@router.get('/xox-groups')
def xox_groups():
    """
    获取所有 xox_group
    """
    groups = XoxGroup.gets()
    data = [group.to_dict for group in groups]
    return res_json({
        'groups': data,
    })

@router.get('/management-companies')
def management_companies():
    """
    获取所有经纪公司
    """
    companies = ManagementCompany.gets()
    data = [company.to_dict for company in companies]
    return res_json({
        'management_companies': data,
    })
