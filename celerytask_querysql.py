import time
import pymysql
import datetime
import random
import timeout_decorator
from functools import wraps
from dateutil.relativedelta import relativedelta
from celeryconfig import Config_Mysql, Config_Mysql_FalseCheck
from celeryconfig import Config_Mysql_ScanCode, Config_Mysql_UserView,Config_Charts

__slots__ = ['CommandHandler']


# 数据库装饰器  连接与关闭数据库 以及异常处理
def decorator_database(hostname, username, password, database) -> object:
    def outer(func):
        @wraps(func)
        def inner(*args, **kwargs):
            try:
                db = pymysql.connect(hostname, username, password, database)
            except Exception as e:
                return
            cur = db.cursor()
            res = None
            kwargs['db'] = db
            kwargs['cur'] = cur
            try:
                res = func(kwargs)
            except Exception as e:
                db.rollback()
            cur.close()
            db.close()
            return res
        return inner
    return outer
    
# 执行sql
@timeout_decorator.timeout(Config_Mysql.timeout)
def exec_sql(kwargs, sql):
    db = kwargs['db']
    cur = kwargs['cur']
    cur.execute(sql)
    res = cur.fetchall()
    return res

# 跨月时间


def extend_into_next_month() -> tuple:
    '''
        返回 本月的第几天,当前的年_月,上一个年_月
    '''
    now = datetime.datetime.now()
    cur_month_day = datetime.date.today().day  # 当月的第几天
    cur_month = now.strftime('%Y_%m')
    last_month = (now + relativedelta(months=-1)).strftime('%Y_%m')
    return now, cur_month_day, cur_month, last_month


# =================== 按照天数的统计 =======================

@decorator_database(hostname=Config_Mysql_UserView.hostname, username=Config_Mysql_UserView.username,
                    password=Config_Mysql_UserView.password, database=Config_Mysql_UserView.database)
def query_userview_byday(kwargs) -> dict:
    '''
        查询 userview 数量
        返回 字典  key 是时间，value 是统计数
    '''
    res_dict = {}
    now = datetime.datetime.now()
    try:
        for i in range(1, kwargs['day']+1):
            date = (now + datetime.timedelta(days=-i)).strftime('%Y-%m-%d')
            res = exec_sql(kwargs, Config_Mysql_UserView.sql_oneday.format(i))
            if res:
                res_dict[date] = res[0][0]
            else:
                res_dict[date] = 0
    except Exception as e:
        return {}
    return res_dict


@decorator_database(hostname=Config_Mysql_ScanCode.hostname, username=Config_Mysql_ScanCode.username,
                    password=Config_Mysql_ScanCode.password, database=Config_Mysql_ScanCode.database)
def query_scancode_byday(kwargs) -> dict:
    '''
        查询 扫描 数量
        返回 字典  key 是时间，value 是统计数
    '''
    res_dict = {}
    now, cur_month_day, cur_month, last_month = extend_into_next_month()
    try:
        for i in range(1, kwargs['day']+1):
            date = (now + datetime.timedelta(days=-i)).strftime('%Y-%m-%d')
            if i < cur_month_day:
                month = cur_month
            else:
                month = last_month
            res = exec_sql(
                kwargs, Config_Mysql_ScanCode.sql_oneday.format(month, i))
            if res:
                res_dict[date] = res[0][0]
            else:
                res_dict[date] = 0
    except Exception as e:
        return {}
    return res_dict


@decorator_database(hostname=Config_Mysql_FalseCheck.hostname, username=Config_Mysql_FalseCheck.username,
                    password=Config_Mysql_FalseCheck.password, database=Config_Mysql_FalseCheck.database)
def query_falsecheck_byday(kwargs) -> dict:
    '''
        查询 验伪 数量
        返回 字典  key 是时间，value 是统计数
    '''
    try:
        tables = exec_sql(kwargs, 'show tables;')
        if not tables:
            return
    except Exception as e:
        return
    res_dict = {}
    now, cur_month_day, cur_month, last_month = extend_into_next_month()
    try:
        for i in range(1, kwargs['day']+1):
            date = (now + datetime.timedelta(days=-i)).strftime('%Y-%m-%d')
            if i < cur_month_day:
                month = cur_month
            else:
                month = last_month
            query_table_sql = [Config_Mysql_FalseCheck.sql_oneday.format(table[0]+month, i)
                               for table in tables if '_' not in table[0] and 'decode' not in table[0]
                               and 'stream' not in table[0]]
            tmp = 0
            for sql in query_table_sql:
                try:
                    res = exec_sql(kwargs, sql)
                    if res:
                        tmp += res[0][0]
                except Exception as e:
                    pass
            res_dict[date] = tmp
    except Exception as e:
        return {}
    return res_dict

# 生成时间段 sql 语句


def query_byperiod_nogroupby(field, table, date) -> dict:
    sql_period = {
        Config_Mysql.sql_period_key[0]: Config_Mysql.morning_nogroupby % (table, field, date, field, date),
        Config_Mysql.sql_period_key[1]: Config_Mysql.forenoon_nogroupby % (table, field, date, field, date),
        Config_Mysql.sql_period_key[2]: Config_Mysql.noon_nogroupby % (table, field, date, field, date),
        Config_Mysql.sql_period_key[3]: Config_Mysql.afternoon_nogroupby % (table, field, date, field, date),
        Config_Mysql.sql_period_key[4]: Config_Mysql.evening_nogroupby % (table, field, date, field, date, field, date, field, date),
    }
    return sql_period

#  时间段的结果聚合


def polymerization_byperiod(res_dict):
    try:
        tmp_dict = {}
        tmp_list = sorted(res_dict)
        tmp_key = '%s~%s' % (tmp_list[0], tmp_list[-1])
        tmp_dict[tmp_key] = {}
        for _, item in res_dict.items():
            for key, value in item.items():
                if key not in tmp_dict[tmp_key].keys():
                    tmp_dict[tmp_key][key] = value
                else:
                    tmp_dict[tmp_key][key] += value
        return tmp_dict
    except Exception as e:
        return {}

# ====================== 时间段内的统计 ====================
@decorator_database(hostname=Config_Mysql_UserView.hostname, username=Config_Mysql_UserView.username,
                    password=Config_Mysql_UserView.password, database=Config_Mysql_UserView.database)
def query_userview_byperiod(kwargs) -> dict:
    now = datetime.datetime.now()
    res_dict = {}
    for i in range(1, kwargs['day']+1):
        date = (now + datetime.timedelta(days=-i)).strftime('%Y-%m-%d')
        sqls = query_byperiod_nogroupby(
            Config_Mysql_UserView.field_name_byperiod, Config_Mysql_UserView.table_name_byperiod, date)
        res_dict[date] = {}
        for key, sql in sqls.items():
            try:
                res = exec_sql(kwargs, sql)
                if res:
                    res_dict[date][key] = res[0][0]
            except Exception:
                pass
    if kwargs['polymerization']:
        res_dict = polymerization_byperiod(res_dict)
    return res_dict


@decorator_database(hostname=Config_Mysql_ScanCode.hostname, username=Config_Mysql_ScanCode.username,
                    password=Config_Mysql_ScanCode.password, database=Config_Mysql_ScanCode.database)
def query_scancode_byperiod(kwargs):
    res_dict = {}
    now, cur_month_day, cur_month, last_month = extend_into_next_month()

    for i in range(1, kwargs['day']+1):
        date = (now + datetime.timedelta(days=-i)).strftime('%Y-%m-%d')
        res_dict[date] = {}
        if i < cur_month_day:
            month = cur_month
        else:
            month = last_month
        sqls = query_byperiod_nogroupby(Config_Mysql_ScanCode.field_name_byperiod, '%s%s' % (
            Config_Mysql_ScanCode.table_name_byperiod, month), date)
        for key, sql in sqls.items():
            try:
                res = exec_sql(kwargs, sql)
                if res:
                    res_dict[date][key] = res[0][0]
            except Exception as e:
                pass
    if kwargs['polymerization']:
        res_dict = polymerization_byperiod(res_dict)
    return res_dict


@decorator_database(hostname=Config_Mysql_FalseCheck.hostname, username=Config_Mysql_FalseCheck.username,
                    password=Config_Mysql_FalseCheck.password, database=Config_Mysql_FalseCheck.database)
def query_falsecheck_byperiod(kwargs):
    try:
        tables = exec_sql(kwargs, 'show tables;')
        if not tables:
            return
    except Exception as e:
        return
    res_dict = {}
    now, cur_month_day, cur_month, last_month = extend_into_next_month()

    for i in range(1, kwargs['day']+1):
        date = (now + datetime.timedelta(days=-i)).strftime('%Y-%m-%d')
        if i < cur_month_day:
            month = cur_month
        else:
            month = last_month
        query_tables = [table[0]+month for table in tables if '_' not in table[0] and 'decode' not in table[0]
                        and 'stream' not in table[0]]
        res_dict[date] = {}
        for table in query_tables:
            sqls = query_byperiod_nogroupby(
                Config_Mysql_FalseCheck.field_name_byperiod, table, date)
            for key, sql in sqls.items():
                try:
                    res = exec_sql(kwargs, sql)
                    if res:
                        if key not in res_dict[date].keys():
                            res_dict[date][key] = res[0][0]
                        else:
                            res_dict[date][key] += res[0][0]
                except Exception as e:
                    pass
    if kwargs['polymerization']:
        res_dict = polymerization_byperiod(res_dict)
    return res_dict


# 代理执行
class CommandHandler:

    def __init__(self, *args, **kwargs):
        random.seed(time.time())

    def _count_byday(self, day=1):
        '''
            默认查询一天
            按照天查询  userview 扫描次数 验伪次数
        '''
        return query_userview_byday(day=day), query_scancode_byday(day=day), query_falsecheck_byday(day=day)

    def _count_byperiod(self, day=1, polymerization=False):
        return query_userview_byperiod(day=day, polymerization=polymerization),\
            query_scancode_byperiod(day=day, polymerization=polymerization),\
            query_falsecheck_byperiod(day=day, polymerization=polymerization)

    def __call__(self):
        pass


    def reorganize_count_byperiod(self, day=1, polymerization=False):

        us_dict, sc_dict, fc_dict = self._count_byperiod(day, polymerization)

        tmp_date = list(us_dict.keys())[::-1]
        us_list = list(us_dict.values())[::-1]
        sc_list = list(sc_dict.values())[::-1]
        fc_list = list(fc_dict.values())[::-1]

        res_list = []
        for us_dict in us_list:
            ax_data = list(us_dict.keys())
            b_data = []
            index = us_list.index(us_dict)
            b_data.append(list(us_dict.values())) 
            b_data.append(list(sc_list[index].values())) 
            b_data.append(list(fc_list[index].values())) 

            leg_items = [
                (Config_Charts.chose_colors[random.randint(
                    0, len(Config_Charts.chose_colors))], Config_Charts.showname[1]),
                (Config_Charts.chose_colors[random.randint(
                    0, len(Config_Charts.chose_colors))], Config_Charts.showname[2]),
                (Config_Charts.chose_colors[random.randint(0, len(Config_Charts.chose_colors))], Config_Charts.showname[3])]
            
            t_data = [tuple([Config_Charts.showname[0]]+ax_data),
                      tuple([Config_Charts.showname[1]]+list(b_data[0])),
                      tuple([Config_Charts.showname[2]]+list(b_data[1])),
                      tuple([Config_Charts.showname[3]]+list(b_data[2])),
                      ]
            res_list += [(tmp_date[index],t_data, b_data, ax_data, leg_items)]
        return res_list
    
    def reorganize_count_byday(self,day=1):

        us_dict, sc_dict, fc_dict = self._count_byday(day)
        if not us_dict or not sc_dict or not fc_dict:
            return 
        ax_data = list(us_dict.keys())[::-1]
        b_data = []
        b_data.append(list(us_dict.values())[::-1])
        b_data.append(list(sc_dict.values())[::-1])
        b_data.append(list(fc_dict.values())[::-1])

        leg_items = [
            (Config_Charts.chose_colors[random.randint(
                0, len(Config_Charts.chose_colors))], Config_Charts.showname[1]),
            (Config_Charts.chose_colors[random.randint(
                0, len(Config_Charts.chose_colors))], Config_Charts.showname[2]),
            (Config_Charts.chose_colors[random.randint(0, len(Config_Charts.chose_colors))], Config_Charts.showname[3])]

        t_data = [tuple([Config_Charts.showname[0]]+ax_data),
                  tuple([Config_Charts.showname[1]]+list(b_data[0])),
                  tuple([Config_Charts.showname[2]]+list(b_data[1])),
                  tuple([Config_Charts.showname[3]]+list(b_data[2])),
                  ]
        res_list = []
        res_list += [(t_data, b_data, ax_data, leg_items)]
        return res_list


if __name__ == "__main__":
    c = CommandHandler()
    res = c.reorganize_count_byperiod()
    print(res)
