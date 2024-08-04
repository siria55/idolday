

from memcached import mc
from sms import get_voice_token

def gen_voice_token():
    print('init run')
    token = get_voice_token()
    mc.set('nls_token', token, 60 * 60 * 24)
