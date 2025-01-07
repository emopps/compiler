from .Grammar import Grammar
from .LR1Table import LR1Table
import sys
from .LR1TablePrintxml import LR1TableXml


def GenLR1Table(grammar_file):
    """
    生成LR(1)分析表。

    :param grammar_file: 语法文件的路径
    :return: 生成的LR(1)分析表，包括action表、goto表和parse_table
    """
    # 从语法文件中读取语法规则，创建Grammar对象
    G = Grammar(open(grammar_file).read())
    # 使用Grammar对象创建LR1Table对象
    lr1_parser = LR1Table(G)
    # 获取LR1Table对象的action表
    action_ = lr1_parser.action
    # 获取LR1Table对象的goto表
    goto_ = lr1_parser.goto
    # 获取LR1Table对象的parse_table
    lr1_table_ = lr1_parser.parse_table
    # 返回生成的LR(1)分析表
    return action_, goto_, lr1_table_

def GenTableXml(action_, goto_, lr1_table_):
    """
    生成LR(1)分析表的XML表示。

    :param action_: LR(1)分析表的action表
    :param goto_: LR(1)分析表的goto表
    :param lr1_table_: LR(1)分析表的parse_table
    :return: 无
    """
    # 创建LR1TableXml对象，传入action表、goto表和parse_table
    w = LR1TableXml(action_, goto_, lr1_table_)
