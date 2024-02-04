from common.log import logger

"""
  大模型输出结构化处理
"""
class StructLLMOutput:
    def __init__(self):
        logger.info("--" * 30 + "StructOutput init " + "--" * 30)
    def out_json(self, info):
        if "result" in info:
            return info["result"]
        else:
            return "LLM out format is fail"


