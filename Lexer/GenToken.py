# 导入正则表达式模块
import re

# 定义正则表达式，用于匹配赋值操作符 :=
ASSIGN = r"(?P<ASSIGN>(:=){1})"
# 定义正则表达式，用于匹配加法操作符 +
PLUS = r"(?P<PLUS>(\+){1})"
# 定义正则表达式，用于匹配减法操作符 -
MINUS = r"(?P<MINUS>(\-))"
# 定义正则表达式，用于匹配乘法操作符 *
TIMES = r"(?P<TIMES>(\*))"
# 定义正则表达式，用于匹配除法操作符 /
DIVIDE = r"(?P<DIVIDE>(\/))"
# 定义正则表达式，用于匹配不等号 #
NEQUAL = r"(?P<NEQUAL>(#))"
# 定义正则表达式，用于匹配小于等于号 <=
LESS_OR_EQUAL = r"(?P<LESS_OR_EQUAL>(<={1}))"
# 定义正则表达式，用于匹配大于等于号 >=
GREATER_OR_EQUAL = r"(?P<GREATER_OR_EQUAL>(>={1}))"
# 定义正则表达式，用于匹配小于号 <
LESS = r"(?P<LESS>(<{1}))"
# 定义正则表达式，用于匹配大于号 >
GREATER = r"(?P<GREATER>(>{1}))"
# 定义正则表达式，用于匹配等号 =
EQUAL = r"(?P<EQUAL>(=){1})"

# 定义正则表达式，用于匹配左括号 (
LEFT_PARENTHESES = r"(?P<LEFT_PARENTHESES>(\())"
# 定义正则表达式，用于匹配右括号 )
RIGHT_PARENTHESES = r"(?P<RIGHT_PARENTHESES>(\)))"
# 定义正则表达式，用于匹配分号 ;
SEMICOLON = r"(?P<SEMICOLON>(;))"
# 定义正则表达式，用于匹配逗号 ,
COMMA = r"(?P<COMMA>(,))"
# 定义正则表达式，用于匹配点号 .
DOT = r"(?P<DOT>(\.))"

# 定义正则表达式，用于匹配关键字 const
CONST = r"(?P<CONST>(const))"
# 定义正则表达式，用于匹配关键字 var
VAR = r"(?P<VAR>(var))"
# 定义正则表达式，用于匹配关键字 procedure
PROCEDURE = r"(?P<PROCEDURE>(procedure))"
# 定义正则表达式，用于匹配关键字 begin
BEGIN = r"(?P<BEGIN>(begin))"
# 定义正则表达式，用于匹配关键字 end
END = r"(?P<END>(end))"
# 定义正则表达式，用于匹配关键字 odd
ODD = r"(?P<ODD>(odd))"
# 定义正则表达式，用于匹配关键字 if
IF = r"(?P<IF>(if))"
# 定义正则表达式，用于匹配关键字 then
THEN = r"(?P<THEN>(then))"
# 定义正则表达式，用于匹配关键字 call
CALL = r"(?P<CALL>(call))"
# 定义正则表达式，用于匹配关键字 while
WHILE = r"(?P<WHILE>(while))"
# 定义正则表达式，用于匹配关键字 do
DO = r"(?P<DO>(do))"
# 定义正则表达式，用于匹配关键字 read
READ = r"(?P<READ>(read))"
# 定义正则表达式，用于匹配关键字 write
WRITE = r"(?P<WRITE>(write))"

# 定义正则表达式，用于匹配标识符，即以字母开头，后跟字母或数字的字符串
IDENTIFIER = r"(?P<IDENTIFIER>([a-zA-Z][a-zA-Z0-9]*))"
# 定义正则表达式，用于匹配数字，即一个或多个数字的字符串
NUMBER = r"(?P<NUMBER>([0-9]+))"

# 将所有正则表达式组合成一个列表
PATTERNS = [ASSIGN, PLUS, MINUS, TIMES, DIVIDE, GREATER_OR_EQUAL, LESS_OR_EQUAL, EQUAL, NEQUAL, LESS, GREATER,
            LEFT_PARENTHESES, RIGHT_PARENTHESES, SEMICOLON, COMMA, DOT, CONST, VAR, PROCEDURE, BEGIN,
            END, ODD, IF, THEN, CALL, WHILE, DO, READ, WRITE, IDENTIFIER, NUMBER]

# 使用正则表达式模块的 compile 函数将所有正则表达式编译成一个模式对象
patterns = re.compile("|".join(PATTERNS))

# 定义一个字典，用于将词素类型映射到其对应的字符串值
# 除了 IDENTIFIER 和 NUMBER，其他词素类型的值都与正则表达式的命名捕获组一致
mapping = dict()
mapping["ASSIGN"] = ":="
mapping["PLUS"] = "+"
mapping["MINUS"] = "-"
mapping["TIMES"] = "*"
mapping["DIVIDE"] = "/"
mapping["EQUAL"] = "="
mapping["NEQUAL"] = "#"
mapping["LESS"] = "<"
mapping["LESS_OR_EQUAL"] = "<="
mapping["GREATER"] = ">"
mapping["GREATER_OR_EQUAL"] = ">="
mapping["LEFT_PARENTHESES"] = "("
mapping["RIGHT_PARENTHESES"] = ")"
mapping["SEMICOLON"] = ";"
mapping["COMMA"] = ","
mapping["DOT"] = "."
mapping["CONST"] = "const"
mapping["VAR"] = "var"
mapping["PROCEDURE"] = "procedure"
mapping["BEGIN"] = "begin"
mapping["END"] = "end"
mapping["ODD"] = "odd"
mapping["IF"] = "if"
mapping["THEN"] = "then"
mapping["CALL"] = "call"
mapping["WHILE"] = "while"
mapping["DO"] = "do"
mapping["READ"] = "read"
mapping["WRITE"] = "write"
mapping["IDENTIFIER"] = "id"
mapping["NUMBER"] = "num"

# 定义一个 Token 类，用于表示词法单元
class Token:
    def __init__(self, token_type, token_value, attach):
        """
        初始化 Token 对象。

        :param token_type: 词法单元的类型
        :param token_value: 词法单元的值
        :param attach: 附加信息，对于标识符和数字，附加信息为其字符串表示；对于其他词法单元，附加信息为 -1
        """
        self.token_key = token_type
        self.token_value = token_value
        self.attach = attach

    def __str__(self):
        """
        返回 Token 对象的字符串表示。

        :return: 字符串，格式为 "{type: %s id: %s num: %s}"，其中 %s 分别表示词法单元的类型、值和附加信息
        """
        return "{type: %s id: %s num: %s}" % (self.token_key, self.token_value, self.attach)

# 定义一个生成器函数，用于从输入文本中提取词法单元
def line_get_token(txt):
    """
    从输入文本中提取词法单元。

    :param txt: 输入文本
    :return: 生成器，每次迭代返回一个包含词法单元类型、值和附加信息的列表
    """
    # 使用正则表达式的 finditer 方法在输入文本中查找所有匹配的词法单元
    for match in re.finditer(patterns, txt):
        # 获取匹配的词法单元的类型
        type_ = match.lastgroup
        # 根据词素类型映射字典获取词法单元的值
        value_ = mapping[type_]
        # 如果词法单元的值为 "id" 或 "num"，则附加信息为匹配的字符串；否则附加信息为 -1
        if value_ in ["id", "num"]:
            attach_ = match.group()
        else:
            attach_ = "-1"
        # 使用 yield 关键字返回一个包含词法单元类型、值和附加信息的列表
        yield [type_, value_, attach_]

# 定义一个函数，用于将词法单元写入到输出文件中
def gen_token(txt, the_output_file):
    """
    将输入文本中的词法单元写入到输出文件中。

    :param txt: 输入文本
    :param the_output_file: 输出文件的路径
    """
    # 以追加模式打开输出文件，如果文件不存在则创建
    with open(the_output_file, "a+") as f:
        for token in line_get_token(txt):
            f.write(str(token))
            f.write("\n")
    f.close()
