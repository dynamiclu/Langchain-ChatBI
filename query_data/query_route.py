from common.log import logger
from query_data.db import selectMysql

class QueryRoute:

    def __init__(self):
        logger.info("--" * 10 + "queryRoute init " + "--" * 10)

    def verify_query(self, out_dict: dict):
        if out_dict is None:
            out_dict = {"data_indicators": "pv", "operator_type": "detail", "time_type": "day",
                        "dimensions": [{"enName": "name"}, {"enName": "id"}], "filters": [{"enName": "name", "val": "一汽"}],
                        "filter_type": "eq", "date_range": "2024-01-01,2024-02-01", "compare_type": "无"}
        indicators_code = out_dict["data_indicators"]
        dim_code_list = out_dict["dimensions"]
        dim_code = ""
        index = 1
        if dim_code_list:
            for line in dim_code_list:
                if index == 1:
                    dim_code = line["enName"]
                else:
                    dim_code += "," + line["enName"]
                index = index + 1

        SQL_like = """
            SELECT query_info,datasource_info,datasource_type
            FROM query_route
            WHERE indicators_code = '%s'
            AND dim_code_list like '%s'
            AND dim_query_type = 0
        """ % (indicators_code, "%"+dim_code+"%")

        SQL_eq = """
            SELECT query_info,datasource_info,datasource_type
            FROM query_route
            WHERE indicators_code = '%s'
            AND dim_code_list =  '%s' 
            AND dim_query_type = 1
        """ % (indicators_code, dim_code)
        # print("SQL_like:", SQL_like)
        # print("SQL_eq:", SQL_eq)
        result_like = selectMysql(SQL_like)
        result_eq = selectMysql(SQL_eq)
        if (result_like and len(result_like) > 0) or (result_eq and len(result_eq) > 0):
            if result_like:
                return result_like[0][0], result_like[0][1], result_like[0][2]
            elif result_eq:
                return result_eq[0][0], result_like[0][1], result_like[0][2]
        else:
            return None


if __name__ == "__main__":

    qr = QueryRoute()
    sql = qr.verify_query(None)
    print("sql:", sql)





