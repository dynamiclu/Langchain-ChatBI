import os
from langchain.chat_models.tongyi import ChatTongyi
from configs.config import DASHSCOPE_API_KEY


os.environ["DASHSCOPE_API_KEY"] = DASHSCOPE_API_KEY

class LLMTongyi(ChatTongyi):
    streaming = True

    def __init__(self):
        super().__init__()
