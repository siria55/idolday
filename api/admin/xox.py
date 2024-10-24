
from pydantic import BaseModel
from fastapi import APIRouter

from api import  res_json, res_err, ERRCODES

from models.xox import Xox, XoxGroup, ManagementCompany

router = APIRouter()

class ReqXoxs(BaseModel):
    name: str
    group_id: int
    management_company_id: int


@router.post('/admin/xoxs')
def xoxs(req: ReqXoxs):
    """
    创建 xox
    """
    group = XoxGroup.get(req.group_id)
    company = ManagementCompany.get(req.management_company_id)
    if not group or not company:
        return res_err(ERRCODES.PARAMS_ERROR, 'group_id or management_company_id not found')
    if group.management_company_id != company.id:
        return res_err(ERRCODES.PARAMS_ERROR, 'group_id and management_company_id not match')
    xox = Xox.create(name=req.name, group_id=req.group_id, management_company_id=req.management_company_id)
    return res_json({
        'xox': xox.to_dict,
    })

class ReqXoxGroups(BaseModel):
    name: str
    management_company_id: int

@router.post('/admin/xox-groups')
def xox_groups(req: ReqXoxGroups):
    """
    创建 xox_group
    """
    company = ManagementCompany.get(req.management_company_id)
    if not company:
        return res_err(ERRCODES.PARAMS_ERROR, 'management_company_id not found')
    group = XoxGroup.create(name=req.name, management_company_id=req.management_company_id)
    return res_json({
        'group': group.to_dict,
    })


class ReqManagementCompanies(BaseModel):
    name: str

@router.post('/admin/management-companies')
def management_companies(req: ReqManagementCompanies):
    """
    创建经纪公司
    """
    company = ManagementCompany.create(name=req.name)
    return res_json({
        'management_company': company.to_dict,
    })
