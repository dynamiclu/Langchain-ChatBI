from common.log import logger
from common.dict import *

"""
  大模型输出结构化处理
 input: 
 {
        "data_indicators": "pv", 
        "operator_type": "求和", 
        "time_type": "半年", 
        "dimension": "一汽红旗", 
        "filter": "一汽红旗", 
        "filter_type": "范围", 
        "date_range": "2023-07-01,2023-12-31", 
        "compare_type": "无"
 }
 output:
 {"data_indicators": "pv", "operator_type": "101", "time_type": "day",
     "dimensions": [{"enName": "name"}, {"enName": "id"}], "filters": [{"enName": "name", "val": "一汽红旗"}],
     "filter_type": "eq", "date_range": "2023-02-01,2023-02-25", "compare_type": "无"}
                        
"""
obj_dict = Dict()

def out_json_data(info):
    out_json = {}
    if "data_indicators" in info:
        out_json["data_indicators"] = obj_dict.__value__(FILE_DICT_TYPE, str(info["data_indicators"]))
    if "operator_type" in info:
        out_json["operator_type"] = obj_dict.__value__(FILE_OPERATOR_TYPE, str(info["operator_type"]))
    if "time_type" in info:
        out_json["time_type"] = obj_dict.__value__(FILE_DICT_TYPE, str(info["time_type"]))
    if "dimension" in info:
        out_json["dimensions"] = [{"enName": "name"}]
    if "filter" in info:
        out_json["filters"] = [{"enName": "name", "val": info["filter"]}]
    if "filter_type" in info:
        out_json["filter_type"] = obj_dict.__value__(FILE_DICT_TYPE, str(info["filter_type"]))
    if "date_range" in info:
        out_json["date_range"] = info["date_range"]
    if "compare_type" in info:
        out_json["compare_type"] = info["compare_type"]
    return out_json

"""
输出echart格式
option = {
                xAxis: {
                type: 'category',
                data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            },
            yAxis: {
                type: 'value'
            },
            series: [{
                data: [820, 932, 901, 934, 1290, 1330, 1320],
                type: 'line'
        }]
    };
"""
def out_echart_data(json_data):
    name_list = []
    val_list = []
    if json_data:
        for obj in json_data:
            name_list.append(obj["name"])
            val_list.append(int(obj["value"]))

    option = """
        {
            xAxis: {
                type: 'category',
                data: %s
            },
            yAxis: {
                type: 'value'
            },
            series: [{
                data: %s,
                type: 'line'
            }]
        }""" % (name_list, val_list)
    return option

