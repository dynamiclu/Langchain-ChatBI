from query_data.query_route import QueryRoute
from query_data.db import selectMysql
from common.log import logger
import json
import requests

query_route = QueryRoute()

def exe_query(out_dict):
    result_data = []
    if out_dict:
        out_dict_result, datasource_info, datasource_type = query_route.verify_query(out_dict)
        if out_dict_result:
            if datasource_type == 0:
                out_dict["table_name"] = out_dict_result
                sql_query = sql_assemble(out_dict)
                list_data = selectMysql(sql_query)
                for row in list_data:
                    result = {
                        "name": row[0],
                        "value": int(row[1])
                    }
                    result_data.append(result)
            elif datasource_type == 1:
                out_dict["url"] = out_dict_result
                result_data = url_get_data(out_dict, datasource_info)

    return result_data

def url_get_data(out_dict, datasource_info):
    # req_params_map = {
    #
    # }
    req_params_map = datasource_info
    try:
        json_data = json.dumps(req_params_map)
        res = requests.post(
            url=out_dict["url"],
            headers={
                "Content-Type": "application/json",
            },
            data=json_data,
            timeout=60
        )
        res_json = json.loads(res.text)
        if res.status_code == 200:
            return res_json["data"], res.status_code
        else:
            return res_json["msg"], res.status_code
    except Exception as e:
        logger.error(e)
        return "query  fail, wait a second! ", 500

def sql_assemble(out_dict: dict):
    if out_dict is None:
        out_dict = {'data_indicators': 'pv', 'operator_type': 'sum', 'time_type': 'quarter', 'dimensions': [{'enName': 'name'}], 'filters': [{'enName': 'name', 'val': '一汽大众'}], 'filter_type': '=', 'date_range': '2023-04-01,2023-06-30', 'compare_type': '无', 'table_name': 'brand_data'}
    data_indicators = out_dict["data_indicators"]
    operator_type = out_dict["operator_type"]
    time_type = out_dict["time_type"]
    dimensions = out_dict["dimensions"]
    filters = out_dict["filters"]
    filter_type = out_dict["filter_type"]
    date_range = out_dict["date_range"]
    table_name = out_dict["table_name"]
    # compare_type = out_dict["compare_type"]
    group_by_sql, dim_sql, dim_group = "", "", ""
    condition = "1=1 "
    if dimensions:
        for line in dimensions:
            dim_sql = line["enName"] + " as name"
            dim_group = line["enName"]
    if filters:
        for fi in filters:
            key = fi["enName"]
            val = fi["val"]
            condition += " and " + filters_join(key, val, filter_type)
    if date_range:
        if "," in date_range:
            begin_date = date_range.split(",")[0]
            end_date = date_range.split(",")[1]
            condition += time_type_format(begin_date, end_date, time_type)
        else:
            condition += time_type_format_eq(date_range, time_type)

    operator_type_sql = ""
    if operator_type:
        if operator_type == "sum":
            operator_type_sql = "sum(%s) as value" % data_indicators
            group_by_sql = "group by %s" % dim_group
        elif operator_type == "avg":
            operator_type_sql = "avg(%s) as value" % data_indicators
            group_by_sql = "group by %s" % dim_group
        elif operator_type == "max":
            operator_type_sql = "max(%s) as value" % data_indicators
            group_by_sql = "group by %s" % dim_group
        elif operator_type == "min":
            operator_type_sql = "min(%s) as value" % data_indicators
            group_by_sql = "group by %s" % dim_group
        else:
            operator_type_sql = data_indicators

    SQL = """
            SELECT %s,%s
            FROM %s
            WHERE %s
            %s
            """ % (dim_sql, operator_type_sql, table_name, condition, group_by_sql)
    return SQL


def filters_join(key: str, val: str, filter_type: str):
    filter_sql = ""
    if filter_type:
        if filter_type == "=":
            filter_sql = " " + key + " like '%"+val+"%'"
            # filter_sql = " %s = '%s' " % (key, val)
        if filter_type == ">":
            filter_sql = " %s > '%s' " % (key, val)
        if filter_type == ">=":
            filter_sql = " %s >= '%s' " % (key, val)
        if filter_type == "in":
            filter_sql = " %s in('%s')" % (key, val)
        if filter_type == "like":
            filter_sql = " %s like '%s'" % (key, val)
        if filter_type == "<":
            filter_sql = " %s < '%s'" % (key, val)
        if filter_type == "<=":
            filter_sql = " %s <= '%s'" % (key, val)
    return filter_sql


def time_type_format(begin_date: str, end_date: str, time_type: str):
    condition = ""
    if time_type:
        if time_type == "day" or time_type == "quarter" or time_type == "week":
            condition = " and dt >= '%s' and  dt <= '%s' " % (begin_date, end_date)
        elif time_type == "month":
            condition = " and DATE_FORMAT(dt, '%Y-%m') >= DATE_FORMAT('" + begin_date + "', '%Y-%m')  and DATE_FORMAT(dt, '%Y-%m') <= DATE_FORMAT('" + end_date + "', '%Y-%m')  "
    return condition


def time_type_format_eq(date_range: str, time_type: str):
    condition = ""
    if time_type:
        if time_type == "day":
            condition = "dt = '%s'  """ % date_range
        elif time_type == "month":
            condition = " DATE_FORMAT(dt, '%Y-%m') =  DATE_FORMAT('" + date_range + "', '%Y-%m') "
    return condition


if __name__ == "__main__":
    sql = sql_assemble(None)
    print("sql=", sql)
