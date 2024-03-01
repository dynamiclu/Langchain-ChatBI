from query_data.query_route import QueryRoute
from query_data.db import selectMysql

query_route = QueryRoute()

def exe_query(out_dict):
    result_data = []
    if out_dict:
        out_dict_result = query_route.verify_query(out_dict)
        if out_dict_result:
            out_dict["table_name"] = out_dict_result
            sql_query = sql_assemble(out_dict)
            print("sql_query:", sql_query)
            list_data = selectMysql(sql_query)
            for row in list_data:
                result = {
                    "name": row[0],
                    "value": row[1]
                }
                result_data.append(result)
    return result_data


def sql_assemble(out_dict: str):
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
            FROM test_data.%s
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
    print("sql=",sql)
