
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, field_validator

from database import get_db
from api import gen_token, verify_hcaptcha
from models.user import User

from aliyun_services.sms import send_sms, generate_verification_code
from aliyun_services.email import send_email
from memcached import mc

router = APIRouter()


class ResSwitches(BaseModel):
    use_captcha: bool


@router.get('/switches')
def switches() -> ResSwitches:
    return {
        'use_captcha': False,
    }
