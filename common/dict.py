import sys
from common.log import *
from configs.config import *

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

config_dict = {
    "operator_type": APP_BOOT_PATH+"/knowledge/data/operator_type.csv",
    "dict_type": APP_BOOT_PATH+"/knowledge/data/dict_type.csv"
}

FILE_OPERATOR_TYPE = "operator_type"
FILE_DICT_TYPE = "dict_type"

dict_operator_type = {}
dict_type = {}

def init_dict(file_path: str, dict_name: str, key: int, val: int):
    try:
        with open(file_path, "r") as f:
            for line in f:
                line = line.strip().split(",")
                if dict_name == FILE_OPERATOR_TYPE:
                    dict_operator_type[str(line[key])] = str(line[val])
                elif dict_name == FILE_DICT_TYPE:
                    dict_type[str(line[key])] = str(line[val])
    except FileNotFoundError:
        logger.error(" %s File not found !" % file_path)
    except Exception as e:
        logger.error("Error:", e)


class Dict:
    def __init__(self) -> object:
        logger.info("--" * 10 + "Dict init start " + "--" * 10)
        self.__init_dict__()
        logger.info("--" * 10 + "Dict init end " + "--" * 10)

    @staticmethod
    def __init_dict__():
        init_dict(config_dict[FILE_OPERATOR_TYPE], FILE_OPERATOR_TYPE, 1, 0)
        init_dict(config_dict[FILE_DICT_TYPE], FILE_DICT_TYPE, 1, 0)

    @staticmethod
    def __value__(dict_name: str, val: str):
        if dict_name == FILE_OPERATOR_TYPE:
            if val in dict_operator_type:
                return dict_operator_type[val]
        elif dict_name == FILE_DICT_TYPE:
            if val in dict_type:
                return dict_type[val]
        return ""


if __name__ == "__main__":
    dict_obj = Dict()
