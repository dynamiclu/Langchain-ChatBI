import os
from langchain.chat_models.baichuan import ChatBaichuan

from configs.config import chat_model_baichuan_dict

os.environ["DEFAULT_API_BASE"] = chat_model_baichuan_dict["DEFAULT_API_BASE"]
os.environ["BAICHUAN_API_KEY"] = chat_model_baichuan_dict["BAICHUAN_API_KEY"]
os.environ["BAICHUAN_SECRET_KEY"] = chat_model_baichuan_dict["BAICHUAN_SECRET_KEY"]

class LLMBaiChuan(ChatBaichuan):
    model = "Baichuan2-53B"
    """model name of Baichuan, default is `Baichuan2-53B`."""
    temperature: float = 0.3
    """What sampling temperature to use."""
    top_k: int = 5
    """What search sampling control to use."""
    top_p: float = 0.85

    def __init__(self):
        super().__init__()

