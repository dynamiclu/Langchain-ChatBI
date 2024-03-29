import torch.cuda
import torch.backends

APP_BOOT_PATH = "/Users/PycharmProjects/Langchain-ChatBI"
MODEL_BOOT_PATH = "/Users/PycharmProjects/Langchain-ChatBI/llm/models"

# 本地chatGLM模型配置
VECTOR_SEARCH_TOP_K = 10
LOCAL_EMBEDDING_DEVICE = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
LOCAL_LLM_DEVICE = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
VECTOR_STORE_PATH = APP_BOOT_PATH + "/vector_store"
# 多模型选择，向量模型选择
embedding_model_dict = {
    "bge-large-zh": MODEL_BOOT_PATH + "/bge-large-zh-v1.5",
    "text2vec": MODEL_BOOT_PATH + "/text2vec-large-chinese",
}
LLM_TOP_K = 6
LLM_HISTORY_LEN = 8

llm_model_dict = {
    "chatglm2-6b-int4": MODEL_BOOT_PATH + "/chatglm2-6b-int4",
    "Baichuan2-53B": "",
    "qwen-turbo": "",
}
EMBEDDING_MODEL_DEFAULT = "bge-large-zh"

LLM_MODEL_CHAT_GLM = "chatglm2-6b-int4"
LLM_MODEL_BAICHUAN = "Baichuan2-53B"
LLM_MODEL_QIANWEN = "qwen-turbo"

"""
  百川公司大模型
"""
chat_model_baichuan_dict = {
    "BAICHUAN_API_KEY": "####",
    "BAICHUAN_SECRET_KEY": "######",
    "DEFAULT_API_BASE": "https://api.baichuan-ai.com/v1/chat/completions"
}

"""
 阿里通义千问大模型key
"""
DASHSCOPE_API_KEY = "#########"


WEB_SERVER_NAME = "127.0.0.1"
WEB_SERVER_PORT = 8080
