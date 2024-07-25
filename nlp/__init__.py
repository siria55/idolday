from openai import OpenAI
from memcached import mc
 
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
