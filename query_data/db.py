import sys
import os
import pymysql

initSQL = """
    use demo;
    CREATE TABLE `query_route` (
        `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键',
        `indicators_code` varchar(100) NOT NULL COMMENT '指标编码',
        `indicators_name` varchar(200) NOT NULL COMMENT '指标名称',
        `dim_code_list` varchar(200) NOT NULL COMMENT '维度编码列表',
        `dim_query_type` tinyint DEFAULT '0' COMMENT '维度匹配类型，0:任意组合、1:等匹配',
        `indicators_operator_type` varchar(200) DEFAULT '101' COMMENT '指标支持操作类型，101:明细、102:求和、103:平均值、104:最大值、105：最小值',
        `query_info` text NOT NULL COMMENT '查询信息',
        `datasource_info` varchar(2048) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '数据源信息',
        `datasource_type` tinyint DEFAULT '0' COMMENT '数据源类型，0:数据表、1:接口、2: 现成SQL',
        PRIMARY KEY (`id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=DYNAMIC COMMENT='查询路由表';
    
    CREATE TABLE `website_data` (
        `dt` varchar(100) NOT NULL COMMENT '日期',
        `id` varchar(100) NOT NULL COMMENT '网站ID',
        `name` varchar(100) NOT NULL COMMENT '网站名',
        `pv` bigint NOT NULL COMMENT 'PV',
        `uv` bigint NOT NULL COMMENT 'UV'
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=DYNAMIC COMMENT='网站测试数据';
    
    INSERT INTO query_route(id, indicators_code, indicators_name, dim_code_list, dim_query_type, indicators_operator_type, query_info, datasource_info, datasource_type) VALUES(1, 'pv', '曝光量', 'name,id,dt', 0, '101', 'website_data', '{"driverName":"com.mysql.cj.jdbc.Driver","jdbcUrl":"jdbc:mysql://127.0.0.1:3306/demo?allowMultiQueries=true&useUnicode=true&characterEncoding=utf8&autoReconnect=true&zeroDateTimeBehavior=convertToNull&useSSL=false&serverTimezone=Asia/Shanghai","username":"root","password":""}', 0);
    INSERT INTO query_route(id, indicators_code, indicators_name, dim_code_list, dim_query_type, indicators_operator_type, query_info, datasource_info, datasource_type) VALUES(2, 'uv', '用户数', 'name,id', 1, '101', 'website_data', '{"driverName":"com.mysql.cj.jdbc.Driver","jdbcUrl":"jdbc:mysql://127.0.0.1:3306/demo?allowMultiQueries=true&useUnicode=true&characterEncoding=utf8&autoReconnect=true&zeroDateTimeBehavior=convertToNull&useSSL=false&serverTimezone=Asia/Shanghai","username":"root","password":""}', 0);
    INSERT INTO website_data(dt, id, name, pv, uv) VALUES('2023-02-22', '11', '微博', 333333, 33333);
    INSERT INTO website_data(dt, id, name, pv, uv) VALUES('2023-02-22', '12', '京东', 105933, 45533);
    INSERT INTO website_data(dt, id, name, pv, uv) VALUES('2023-02-23', '12', '京东', 444444, 34444);
    INSERT INTO website_data(dt, id, name, pv, uv) VALUES('2023-02-22', '13', '淘宝', 333555, 55555);
    INSERT INTO website_data(dt, id, name, pv, uv) VALUES('2023-02-23', '13', '淘宝', 145555, 32355);
    INSERT INTO website_data(dt, id, name, pv, uv) VALUES('2023-02-23', '11', '微博', 445333, 32333);
"""

def selectMysql(sql):
    conn = pymysql.connect(
        host='127.0.0.1',
        port=3306,
        database='demo',
        user='root',
        password='####'
    )
    try:
        cursor = conn.cursor()
        cursor.execute(sql)

        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

