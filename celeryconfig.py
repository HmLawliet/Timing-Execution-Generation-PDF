from reportlab.lib import colors
from reportlab.lib.pagesizes import A4

__slots__ = ['Config_Run','Config_Celery','Config_Mysql'
        ,'Config_Crontab','Config_Redis']

class Config_Run:
    worker = ' setsid celery worker -A celeryrun --loglevel=info >/dev/null 2>&1 & '
    beat = ' setsid celery beat -A celeryrun --loglevel=info >/dev/null 2>&1 & '
    monitor_beat = 'ps -ef | grep "celery beat" | grep -v grep |wc -l'
    monitor_worker = 'ps -ef | grep "celery worker" | grep -v grep |wc -l'
    monitor_defunct = 'ps -ef | grep defunct | grep -v grep | wc -l'
    kill_beat = 'ps -ef | grep "celery beat" | grep -v grep | awk \'{print $2}\' | xargs kill -15'
    kill_worker = 'ps -ef | grep "celery worker" | grep -v grep | awk \'{print $2}\' | xargs kill -15'
    kill_defunct = ' ps -ef | grep defunct | grep -v grep | awk \'{print $2}\' | xargs kill -15'


class Config_Celery:
    broker_url = 'redis://localhost/5'
    result_backend = 'redis://localhost/5'
    task_serializer = 'json'
    result_serializer = 'json'
    accept_content = ['json']
    timezone = 'Asia/Shanghai'
    enable_utc = True


class Config_Mysql:
    hostname = '数据库地址'
    username = '数据库用户'
    password = '数据库密码'
    database = '数据库名称'
    status_success = 1  # 成功状态
    status_error = 2   # 错误状态
    timeout = 300 #执行sql语句的总的超时时间 默认300s
    exec_sql = 'select id,`host`,`user`,`password`,`database`,sentence from sql_review_applications where confirmed = 2 and run = 0;'
    exec_count = 10
    update_sql = 'update sql_review_applications set run = %s ,run_time= "%s", run_duration= %s where id = "%s" ;'
    sql_period_key = ('morning','forenoon','noon','afternoon','evening',)
    field_name_byperiod = 'date'
    morning_nogroupby = 'select count(1) as count from %s where %s >= "%s 06:30:00"\
         and %s <= "%s 08:00:00" ;'
    forenoon_nogroupby = 'select count(1) as count from %s where %s >= "%s 08:00:00"\
         and %s <= "%s 11:30:00" ;'
    noon_nogroupby = 'select count(1) as count from %s where %s >= "%s 11:30:00"\
         and %s <= "%s 14:00:00" ;'
    afternoon_nogroupby = 'select count(1) as count from %s where %s >= "%s 14:00:00"\
         and %s <= "%s 17:30:00" ;'
    evening_nogroupby = 'select count(1) as count from %s where (%s >= "%s 00:00:00" and %s <= "%s 06:30:00")\
          or (%s >= "%s 17:30:00" and %s <= "%s 23:59:59");'

    # morning = 'select %s,count(1) as count from %s where date >= "%s 06:30:00"\
    #      and date <= "%s 08:00:00" GROUP BY %s;'
    # forenoon = 'select %s,count(1) as count from %s where date >= "%s 08:00:00"\
    #      and date <= "%s 11:30:00" GROUP BY %s;'
    # noon = 'select %s,count(1) as count from %s where date >= "%s 11:30:00"\
    #      and date <= "%s 14:00:00" GROUP BY %s;'
    # afternoon = 'select %s,count(1) as count from %s where date >= "%s 14:00:00"\
    #      and date <= "%s 17:30:00" GROUP BY %s;'
    # evening = 'select %s,count(1) as count from %s where (date >= "%s 00:00:00" and date <= "%s 06:30:00")\
    #       or (date >= "%s 17:30:00" and date <= "%s 23:59:59") GROUP BY %s;'



class Config_Mysql_UserView(Config_Mysql):
    hostname = '47.100.242.190'
    username = 'test'
    password = '90Y803$0627$2HF80'
    database = 'antifake'
    sql_oneday = 'select count(1) as count from  ac_antifake_log where date_format(verify_time,"%Y-%m-%d") = date_format(SUBDATE(now(),{}),"%Y-%m-%d");'
    table_name_byperiod = 'ac_antifake_log'
    field_name_byperiod = 'verify_time'


class Config_Mysql_ScanCode(Config_Mysql):
    database = 'wpwl'
    sql_oneday = 'select count(1) as count from stream{} where date_format(date,"%Y-%m-%d") = date_format(SUBDATE(now(),{}),"%Y-%m-%d");'
    table_name_byperiod = 'stream'

class Config_Mysql_FalseCheck(Config_Mysql):
    database = 'wpwl'
    sql_oneday = 'select count(1) as count from {} where date_format(date,"%Y-%m-%d") = date_format(SUBDATE(now(),{}),"%Y-%m-%d");' 



class Config_Crontab:
    minute = 0  # 0分
    hour = 1  # 2点
    day_of_month = '1-31'


class Config_Charts:
    chose_colors = (
        colors.ReportLabBlueOLD,colors.ReportLabBlue,colors.ReportLabBluePCMYK,colors.ReportLabLightBlue,
        colors.ReportLabFidBlue,colors.ReportLabFidRed,colors.ReportLabGreen,colors.ReportLabLightGreen,
        colors.aliceblue,colors.aqua,colors.aquamarine,colors.azure,colors.beige,
        colors.bisque,colors.black,colors.blanchedalmond,colors.blue,colors.blueviolet,colors.brown,
        colors.burlywood,colors.cadetblue,colors.chartreuse,colors.chocolate,colors.coral,colors.cornflowerblue,
        colors.cornsilk,colors.crimson,colors.cyan,colors.darkblue,colors.darkcyan,colors.darkgoldenrod,
        colors.darkgray,colors.darkgrey,colors.darkgreen,colors.darkkhaki,colors.darkmagenta,colors.darkolivegreen,
        colors.darkorange,colors.darkorchid,colors.darkred,colors.darksalmon,colors.darkseagreen,colors.darkslateblue,
        colors.darkslategray,colors.darkslategrey,colors.darkturquoise,colors.darkviolet,colors.deeppink,
        colors.deepskyblue,colors.dimgray,colors.dimgrey,colors.dodgerblue,colors.firebrick,
        colors.forestgreen,colors.fuchsia,colors.gainsboro,colors.gold,colors.goldenrod,
        colors.gray,colors.green,colors.greenyellow,colors.honeydew,colors.hotpink,colors.indianred,colors.indigo,
        colors.ivory,colors.khaki,colors.lavender,colors.lavenderblush,colors.lawngreen,colors.lemonchiffon,
        colors.lightblue,colors.lightcoral,colors.lightcyan,colors.lightgoldenrodyellow,colors.lightgreen,
        colors.lightgrey,colors.lightpink,colors.lightsalmon,colors.lightseagreen,colors.lightskyblue,
        colors.lightslategray,colors.lightsteelblue,colors.lightyellow,colors.lime,colors.limegreen,colors.linen,
        colors.magenta,colors.maroon,colors.mediumaquamarine,colors.mediumblue,colors.mediumorchid,colors.mediumpurple,
        colors.mediumseagreen,colors.mediumslateblue,colors.mediumspringgreen,colors.mediumturquoise,
        colors.mediumvioletred,colors.midnightblue,colors.mintcream,colors.mistyrose,colors.moccasin,
        colors.navy,colors.oldlace,colors.olive,colors.olivedrab,colors.orange,colors.orangered,
        colors.orchid,colors.palegoldenrod,colors.palegreen,colors.paleturquoise,colors.palevioletred,
        colors.papayawhip,colors.peachpuff,colors.peru,colors.pink,colors.plum,colors.powderblue,colors.purple,
        colors.red,colors.rosybrown,colors.royalblue,colors.saddlebrown,colors.salmon,colors.sandybrown,
        colors.seagreen,colors.seashell,colors.sienna,colors.silver,colors.skyblue,colors.slateblue,
        colors.slategray,colors.slategrey,colors.snow,colors.springgreen,colors.steelblue,colors.tan,colors.teal,
        colors.thistle,colors.tomato,colors.turquoise,colors.violet,colors.wheat,
        colors.yellow,colors.yellowgreen,colors.fidblue,colors.fidred,colors.fidlightblue,
    )
    pagesize = A4
    typeface = 'SimSun'
    typefacefile = 'SimSun.ttf'
    showname = ('统计日期','访问次数','扫码次数','验伪次数')
    
if __name__ == "__main__":
    print(Config_Charts.chose_colors.index(colors.black))