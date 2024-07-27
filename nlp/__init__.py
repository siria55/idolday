from openai import OpenAI
from memcached import mc

face_bit_names = [
    'HAPPY-SMILE',
    'DUMB',
    'DOUBT',
    'LOOKAROUND-RIGHT',
    'LAUGH',
    'HUH',
    'WRONGED',
    'QUESTION',
    'ANGRY',
    'SPEECHLESS',
    'SLOBBER',
    'CRY',
    'SAD',
    'DEFAULT',
    'OGLE',
    'CLOSE-EYE',
    'UNHAPPY',
    'SMIRK',
    'AWKWARD-SMILE',
    'SMILE',
    'LOOKAROUND-MIDDLE',
    'SHOCK',
    'HAPPY',
    'SLEEP',
    'LOOKAROUND-LEFT',
    'SOB',
    'LIKE',
    'DOWNTIME']

face_car_names = ['STUPID-LAUGH',
    'DOUBT',
    'OOPS',
    'SOB',
    'INSIDIOUS',
    'SAN',
    'CRY',
    'SMILE',
    'SPEECHLESS',
    'LOOKAROUND',
    'SLEEP',
    'AFRAID',
    'SPOILED',
    'LAUGH',
    'DEFAULT',
    'SWEAT',
    'LOVE',
    'DAZE',
    'CUTE',
    'ANGRY']

client = OpenAI(
    api_key = "sk-gu1UoYqojz3IwJTvB4Fqc5zpcg2mKt0dCyH9xuLAnll8UeL9",
    base_url = "https://api.moonshot.cn/v1",
)

init_history = [
    {"role": "system", "content":
        "你是 ToAI Bot 小柿子，今年 7 岁的小朋友。由 北京图爱网络技术有限公司 "
        "提供的陪伴机器人，你更擅长中文和英文的对话。你会为用户提供安全，有帮助，"
        "准确的回答。同时，你会拒绝一切涉及恐怖主义，种族歧视，黄色暴力等问题的回答。"
        "ToAI Bot 为专有名词，不可翻译成其他语言。回答别加 emoji 表情。"}
]


def get_face(phone_number):
    default_face = {
        'face_code_bit': 'DEFAULT',
        'face_code_car': 'DEFAULT',
    }
    history = mc.get(phone_number + '_history', [])
    if not history or len(history) == 1:
        return default_face
    history.append({
        "role": "system",
        "content": "表情有两种类型：bit 和 car。"
        "bit 表情有: {" + ', '.join(face_bit_names) + "}。"
        "car 表情有: {" + ', '.join(face_car_names) + "}。"
        "请根据最近的对话，从 bit 选择一个表情, 从 car 中选择一个表情。"
        "用,连接两个选择。不要回复其他内容。"
    })
    completion = client.chat.completions.create(
        model="moonshot-v1-8k",
        messages=history,
        temperature=0.3,
    )
    result = completion.choices[0].message.content
    if ',' not in result:
        return default_face
    return {
        'face_code_bit': result.split(',')[0],
        'face_code_car': result.split(',')[1],
    }
    

def chat(query, phone_number):
    history = mc.get(phone_number + '_history', [])

    if not history:
        history = init_history
    if len(history) >= 10:
        history = history[:1] + history[-9:]

    history.append({
        "role": "user",
        "content": query
    })
    completion = client.chat.completions.create(
        model="moonshot-v1-8k",
        messages=history,
        temperature=0.3,
    )
    result = completion.choices[0].message.content
    history.append({
        "role": "assistant",
        "content": result
    })

    mc.set(phone_number + '_history', history)
    return result
