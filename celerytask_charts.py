from celerytask_querysql import CommandHandler
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Table, SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.linecharts import SampleHorizontalLineChart
from reportlab.graphics.charts.legends import Legend
from reportlab.graphics.shapes import Drawing
import datetime
import time
import random
from celeryconfig import Config_Charts


__slots__ = ['Generate_Report']


# 注册字体
pdfmetrics.registerFont(
    TTFont(Config_Charts.typeface, Config_Charts.typefacefile))


def getLimitSteps(num):
    if not num:
        return 100, 10
    tmp = num / 2 * 3
    return tmp, round(tmp/10, 0)


class Graphs:

    def __init__(self):
        pass

    # 绘制标题 
    @staticmethod
    def draw_title(topic='日度报告'):
        style = getSampleStyleSheet()
        ct = style['Normal']
        ct.fontName = Config_Charts.typeface
        ct.fontSize = 18
        # 设置行距
        ct.leading = 50
        # 颜色
        ct.textColor = Config_Charts.chose_colors[62]
        # 居中 
        ct.alignment = 1
        # 添加标题并居中 
        title = Paragraph(topic, ct)
        return title

    # 绘制内容 
    @staticmethod
    def draw_text(represent='时间段统计每天用户访问量，扫描的次数，验伪的次数'):
        style = getSampleStyleSheet()
        # 常规字体(非粗体或斜体) 
        ct = style['Normal']
        # 使用的字体s 
        ct.fontName = Config_Charts.typeface
        ct.fontSize = 14
        # 设置自动换行 
        ct.wordWrap = 'CJK'
        # 居左对齐 
        ct.alignment = 0
        # 第一行开头空格 
        ct.firstLineIndent = 32
        # 设置行距 
        ct.leading = 30
        text = Paragraph(represent, ct)
        return text

    # 绘制表格 
    @staticmethod
    def draw_table(*args):
        col_width = 60
        style = [
            ('FONTNAME', (0, 0), (-1, -1), Config_Charts.typeface),  #  字体
            ('BACKGROUND', (0, 0), (-1, 0), '#d5dae6'),  #  设置第一行背景颜色
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  #  对齐
            ('VALIGN', (-1, 0), (-2, 0), 'MIDDLE'),  #  对齐 
            #  设置表格框线为grey色，线宽为0.5
            ('GRID', (0, 0), (-1, -1), 0.5, Config_Charts.chose_colors[61]),
        ]
        table = Table(args, colWidths=col_width, style=style)
        return table

    # 创建图表 
    @staticmethod
    def draw_bar(bar_data=[], ax=[], items=[], limit_step=(100, 10), draw_weight=500, draw_height=250):
        drawing = Drawing(draw_weight, draw_height)
        bc = VerticalBarChart()
        bc.x = 35
        bc.y = 100
        bc.height = 120
        bc.width = 350
        bc.data = bar_data
        bc.strokeColor = Config_Charts.chose_colors[15]
        bc.valueAxis.valueMin = 0
        bc.valueAxis.valueMax = limit_step[0]
        bc.valueAxis.valueStep = limit_step[1]
        bc.categoryAxis.labels.dx = 8
        bc.categoryAxis.labels.dy = -10
        bc.categoryAxis.labels.angle = 20
        bc.categoryAxis.categoryNames = ax
        bc.bars.strokeColor = Config_Charts.chose_colors[148]
        for index, item in enumerate(items):
            bc.bars[index].fillColor = item[0]
        # 图示 
        leg = Legend()
        leg.fontName = Config_Charts.typeface
        leg.alignment = 'right'
        leg.boxAnchor = 'ne'
        leg.x = 465
        leg.y = 220
        leg.dxTextSpace = 0
        leg.columnMaximum = 10
        leg.colorNamePairs = items
        drawing.add(leg)
        drawing.add(bc)
        return drawing

    @staticmethod
    def draw_line(line_data=[], ax=[], items=[], limit_step=(100, 10), draw_weight=500, draw_height=150):
        drawing = Drawing(draw_weight, draw_height)
        lc = SampleHorizontalLineChart()
        lc.x = 35
        lc.y = 100
        lc.height = 120
        lc.width = 350
        lc.data = line_data
        lc.strokeColor = Config_Charts.chose_colors[15]
        lc.valueAxis.valueMin = 0
        lc.valueAxis.valueMax = limit_step[0]
        lc.valueAxis.valueStep = limit_step[1]
        lc.categoryAxis.labels.dx = 8
        lc.categoryAxis.labels.dy = -10
        lc.categoryAxis.labels.angle = 20
        lc.categoryAxis.categoryNames = ax
        for index, item in enumerate(items):
            lc.lines[index].strokeColor = item[0]
        # 图示 
        leg = Legend()
        leg.fontName = Config_Charts.typeface
        leg.alignment = 'right'
        leg.boxAnchor = 'ne'
        leg.x = 465
        leg.y = 200
        leg.dxTextSpace = 0
        leg.columnMaximum = 10
        leg.colorNamePairs = items
        drawing.add(leg)
        drawing.add(lc)
        return drawing


class Generate_Report:

    def __init__(self, title, notes, pagesize=Config_Charts.pagesize):
        self._pagesize = pagesize  # 设置纸张的大小
        now = datetime.datetime.now()
        self._report_name = 'report%s.pdf' % now.strftime(
            '%Y%m%d%H%M%S')  # 报表的名称
        self.title = title   # 报表的题目
        self.notes = notes   # 类型是tuple , 题目下面的注释
        self.content = list()
        self.content.append(Graphs.draw_title(self.title))  #  添加标题  
        self.content.append(Graphs.draw_text(self.notes))  # 添加副标题

    def Template_1(self, g_data, desc=None, isdraw=False):
        max_num = 0
        for i in g_data:
            if len(i) > 4:  # 按照时间段
                text, t_data, b_data, ax_data, leg_items = i
            else:  # 按照天数
                text = desc
                t_data, b_data, ax_data, leg_items = i

            for ii in b_data:
                tmp = max(ii)
                if tmp > max_num:
                    max_num = tmp
            self.content.append(Graphs.draw_text(represent=text))  #  添加段落
            self.content.append(Graphs.draw_table(*t_data))  #  添加表格数据
            self.content.append(Graphs.draw_bar(
                b_data, ax_data, leg_items, getLimitSteps(max_num)))  # 添加直方图
            if len(b_data[0]) != 1:
                self.content.append(Graphs.draw_line(
                    b_data, ax_data, leg_items, getLimitSteps(max_num)))  # 添加折线图

        if isdraw:
            self.pdf()

    # 生成pdf
    def pdf(self):
        doc = SimpleDocTemplate(
            self._report_name, pagesize=self._pagesize)  #  生成pdf文件
        doc.build(self.content)

    # 获取报表的名称
    @property
    def report_name(self):
        return self._report_name


if __name__ == "__main__":
    # gr = Generate_Report('日度报表', '每天要自动发送的一个报表')
    # query_tuple = (
    #     {'2019-07-24': {'morning': 20, 'forenoon': 560,
    #                     'noon': 534, 'afternoon': 1109, 'evening': 1750}},
    #     {'2019-07-24': {'morning': 2, 'forenoon': 208,
    #                     'noon': 159, 'afternoon': 393, 'evening': 587}},
    #     {'2019-07-24': {'morning': 0, 'forenoon': 139,
    #                     'noon': 99, 'afternoon': 259, 'evening': 422}}
    # )
    # query_tuple = (
    #     {'2019-07-24': 3973, '2019-07-23': 3719, '2019-07-22': 3351},
    #     {'2019-07-24': 1349, '2019-07-23': 1335, '2019-07-22': 1072},
    #     {'2019-07-24': 919, '2019-07-23': 959, '2019-07-22': 699}
    # )
    # gr.pdf(query_tuple, '时间段排列', True)
    # query_tuple_byperiod = (
    #     {'2019-07-25': {'morning': 60, 'forenoon': 991, 'noon': 1205, 'afternoon': 1487, 'evening': 1924},
    #      '2019-07-24': {'morning': 20, 'forenoon': 560, 'noon': 534, 'afternoon': 1109, 'evening': 1750}},

    #     {'2019-07-25': {'morning': 12, 'forenoon': 395, 'noon': 376, 'afternoon': 302, 'evening': 655},
    #      '2019-07-24': {'morning': 2, 'forenoon': 208, 'noon': 159, 'afternoon': 393, 'evening': 587}},

    #     {'2019-07-25': {'morning': 8, 'forenoon': 270, 'noon': 270, 'afternoon': 203, 'evening': 449},
    #      '2019-07-24': {'morning': 0, 'forenoon': 139, 'noon': 99, 'afternoon': 259, 'evening': 422}})
    # gr.pdf(query_tuple_byperiod,'通过天来统计',True)

    content = list()  #  添加标题 
    # content.append(Graphs.draw_title())  # 添加段落 
    # content.append(Graphs.draw_text(represent='日期：'))  # 添加表格数据
    # content.append(Graphs.draw_text(represent='天气 晴朗 '))
    # content.append(Graphs.draw_text(represent='日报统计'))

    # data = [('兴趣', '2019-1', '2019-2', '2019-3', '2019-4', '2019-5', '2019-6'),
    #         ('开发', 50, 80, 60, 35, 40, 45),
    #         ('编程', 25, 60, 55, 45, 60, 80),
    #         ('敲代码', 30, 90, 75, 80, 50, 46)]
    # content.append(Graphs.draw_table(*data))  # 添加图表 

    # b_data = [(50, 80, 60, 35, 40, 45),
    #         (25, 60, 55, 45, 60, 80),
    #         (30, 90, 75, 80, 50, 46)]

    # ax_data = ['2019-1', '2019-2', '2019-3', '2019-4', '2019-5', '2019-6']
    # leg_items = [
    #     (Config_Charts.chose_colors[124], '开发'),
    #     (Config_Charts.chose_colors[62], '编程'),
    #     (Config_Charts.chose_colors[17], '敲代码')]
    # content.append(Graphs.draw_bar(b_data, ax_data, leg_items))  # 生成pdf文件

    b_data = [(50, 80, 60, 35, 40, 45),
              (25, 60, 55, 45, 60, 80),
              (30, 90, 75, 80, 50, 46)]

    ax_data = ['2019-1', '2019-2', '2019-3', '2019-4', '2019-5', '2019-6']
    # b_data = [(3413,), (2161,), (1331,)]
    # ax_data = ['2019-07-27']

    leg_items = [
        (Config_Charts.chose_colors[124], '开发'),
        (Config_Charts.chose_colors[62], '编程'),
        (Config_Charts.chose_colors[17], '敲代码')]
    content.append(Graphs.draw_line(b_data, ax_data, leg_items))  #  生成pdf文件
    doc = SimpleDocTemplate('123.pdf')  #  生成pdf文件
    doc.build(content)
