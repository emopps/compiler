from Parser.LR1Table.LR1Table import LR1Table
from Parser.LR1Table.Grammar import Grammar
from .Procedure import Procedure
from utils import grammar_file


class LR1Parser:
    def __init__(self, grammar_file_):
        """
        初始化LR1Parser对象。

        :param grammar_file_: 语法文件的路径
        """
        # 记录过程调用
        # self.procedure = Procedure.Procedure()
        self.procedure = Procedure()
        self.procedure.add_procedure("_global", 0)
        # LR1分析对象
        self.lr1_table = LR1Table(Grammar(open(grammar_file).read()))
        # LR1分析表
        self.parse_table = self.lr1_table.parse_table
        # 记录生成的地址
        self.global_address_counter = 0
        # 状态栈
        self.state_stack = [0]
        # 符号栈
        self.symbol_stack = []
        # 输入栈
        self.readable_stack = []

    def process_const(self, generative):
        """
        处理常量的规约。

        :param generative: 当前使用的产生式
        """
        if generative == 'CONST -> CONST_ ;':
            # pop掉[const ;], 规约为CONST, 栈顶为[], 分析完毕
            self.symbol_stack = self.symbol_stack[:-2]
        elif generative == 'CONST_ -> CONST_ , CONST_DEF':
            # pop掉[, id], 规约为CONST_, 栈顶为[const]
            self.symbol_stack = self.symbol_stack[:-2]
        elif generative == 'CONST_ -> const CONST_DEF':
            # pop掉[id], 规约为CONST_, 栈顶为[const]
            self.symbol_stack = self.symbol_stack[:-1]
        elif generative == 'CONST_DEF -> ID = UINT':
            # pop掉[= num], 规约为CONST_DEF, 栈顶为[const id]
            self.procedure.add_const(self.symbol_stack[-3][2], self.symbol_stack[-1][2])
            self.symbol_stack = self.symbol_stack[:-2]
    def process_var(self, generative):
        """
        处理变量的规约。

        :param generative: 当前使用的产生式
        """
        if generative == 'VARIABLE -> VARIABLE_ ;':
            # pop掉[var ;], 规约为VARIABLE, 栈顶为[], 分析完毕
            self.symbol_stack = self.symbol_stack[:-2]
        elif generative == 'VARIABLE_ -> var ID':
            # pop掉[id], 规约为VARIABLE_, 栈顶为[var]
            self.procedure.add_var(self.symbol_stack[-1][2])
            self.symbol_stack = self.symbol_stack[:-1]
        elif generative == 'VARIABLE_ -> VARIABLE_ , ID':
            # pop掉[, id], 规约为VARIABLE_, 栈顶为[var]
            self.procedure.add_var(self.symbol_stack[-1][2])
            self.symbol_stack = self.symbol_stack[:-2]
    def process_procedure(self, generative):
        """
        处理过程的规约。

        :param generative: 当前使用的产生式
        """
        if generative == 'PROCEDURE -> PROCEDURE_':
            # pop掉[begin end], 栈顶为[]
            self.symbol_stack = self.symbol_stack[:-2]
        elif generative == 'PROCEDURE -> ^':
            pass
        elif generative == 'PROCEDURE_ -> PROCEDURE_ PROC_HEAD SUBPROG ;':
            self.symbol_stack = self.symbol_stack[:-1]
        elif generative == 'PROCEDURE_ -> PROC_HEAD SUBPROG ;':
            # pop掉[;], 栈顶为[begin end]
            self.symbol_stack = self.symbol_stack[:-1]
        elif generative == "PROC_HEAD -> procedure ID ;":
            # pop掉[procedure id ;], 栈顶为[]
            self.procedure.add_procedure(self.symbol_stack[-2][2],
                                         self.procedure.current_procedure.level + 1)
            self.symbol_stack = self.symbol_stack[:-3]
    def process_assign(self, generative, logger):
        """
        处理赋值语句的规约。

        :param generative: 当前使用的产生式
        :param logger: 日志记录器
        """
        if generative == 'ASSIGN -> ID := EXPR':
            # 赋值语句右边的值通过规约计算出, 将其赋给变量
            ret = self.procedure.find_by_name(self.symbol_stack[-3][2])
            if not ret[2]:
                print("ERROR: Assign to CONST number!")
                exit(-1)
            # ret[0]是嵌套深度, ret[1][1]是offset
            logger.insert('STO', ret[0], ret[1][1])
            # pop掉[id := num], 栈顶为[] (注: begin体内除最后一条语句外都要加; 最后一条可加可不加，走的是不同的规约路线)
            self.symbol_stack = self.symbol_stack[:-3]
    def process_comp(self, generative):
        """
        处理复合语句的规约。

        :param generative: 当前使用的产生式
        """
        # 读取到一个begin后, 把begin pop掉, 规约为状态COMP_BEGIN, 之后每遇到一条带;的语句,
        # 就通过第三条产生式规约为COMP_BEGIN, 直到遇到一条不带;的语句, 就通过第一条产生式规约为COMP
        # 如果;之后是end, 则所用产生式为 STATEMENT -> ^
        if generative == 'COMP -> COMP_BEGIN end':
            # pop掉[end], 栈顶为[]
            self.symbol_stack = self.symbol_stack[:-1]
        elif generative == 'COMP_BEGIN -> begin STATEMENT':
            # pop掉[begin], 栈顶为[]
            self.symbol_stack = self.symbol_stack[:-1]
        elif generative == 'COMP_BEGIN -> COMP_BEGIN ; STATEMENT':
            # pop掉[;], 栈顶为[]
            self.symbol_stack = self.symbol_stack[:-1]
    def process_factor(self, generative, logger):
        """
        处理因子的规约。

        :param generative: 当前使用的产生式
        :param logger: 日志记录器
        """
        if generative == 'FACTOR -> ID':
            # 查找变量名对应的信息
            ret = self.procedure.find_by_name(self.symbol_stack[-1][2])
            if ret is None:
                # 如果找不到变量，输出错误信息并退出
                print("ERROR: Can't find variable ", self.symbol_stack[-1][2])
                exit(-1)
            if ret[2] == 0:
                # 如果是常量，插入LIT指令
                logger.insert('LIT', 0, ret[1])
            else:
                # 如果是变量，插入LOD指令
                logger.insert("LOD", ret[0], ret[1][1])
        elif generative == 'FACTOR -> UINT':
            # 如果是无符号整数，插入LIT指令
            logger.insert('LIT', 0, self.symbol_stack[-1][2])
        elif generative == 'FACTOR -> ( EXPR )':
            # 去除括号，只留下表达式
            tmp = self.symbol_stack[-2]
            self.symbol_stack = self.symbol_stack[:-3]
            self.symbol_stack.append(tmp)
    def process_item(self, generative, logger):
        """
        处理项的规约。

        :param generative: 当前使用的产生式
        :param logger: 日志记录器
        """
        if generative == 'ITEM -> FACTOR':
            pass
        elif generative == 'ITEM -> ITEM MUL_DIV FACTOR':
            if self.symbol_stack[-2][0] == 'TIMES':
                logger.insert('OPR', 0, 4)
            elif self.symbol_stack[-2][0] == 'DIVIDE':
                logger.insert('OPR', 0, 5)
            # pop掉[*or/ num], 栈顶为[num]
            self.symbol_stack = self.symbol_stack[:-2]
    def process_expr(self, generative, logger):
        """
        处理表达式的规约。

        :param generative: 当前使用的产生式
        :param logger: 日志记录器
        """
        # 如果产生式为 'EXPR -> EXPR PLUS_MINUS ITEM'
        if generative == 'EXPR -> EXPR PLUS_MINUS ITEM':
            # 如果符号栈的倒数第二个元素是 'MINUS'
            if self.symbol_stack[-2][0] == 'MINUS':
                # 在日志中插入 'OPR'，层级差为 0，操作码为 3
                logger.insert('OPR', 0, 3)
            # 否则
            else:
                # 在日志中插入 'OPR'，层级差为 0，操作码为 2
                logger.insert('OPR', 0, 2)
            # 弹出符号栈的倒数第二个和最后一个元素，栈顶变为 'num'
            self.symbol_stack = self.symbol_stack[:-2]
        # 如果产生式为 'EXPR -> PLUS_MINUS ITEM'
        elif generative == 'EXPR -> PLUS_MINUS ITEM':
            # 如果符号栈的倒数第二个元素是 'MINUS'
            if self.symbol_stack[-2][0] == 'MINUS':
                # 在日志中插入 'OPR'，层级差为 0，操作码为 1
                logger.insert('OPR', 0, 1)
            # 弹出符号栈的倒数第二个元素，栈顶变为 'num'
            self.symbol_stack = self.symbol_stack[:-1]
        # 如果产生式为 'EXPR -> ITEM'
        elif generative == 'EXPR -> ITEM':
            pass

    def process_call(self, generative, logger):
        """
        处理过程调用的规约。

        :param generative: 当前使用的产生式
        :param logger: 日志记录器
        """
        # 如果产生式为 'CALL -> call ID'
        if generative == 'CALL -> call ID':
            # 获取当前过程
            cur_p = self.procedure.current_procedure
            # 循环查找合适的过程调用
            while True:
                # 获取当前过程的所有子过程
                childen_procedures = [self.procedure.procedure_dict[x] for x in
                                      self.procedure.procedure_dict.keys() if
                                      self.procedure.procedure_dict[x].father == cur_p.name]
                # 查找与当前符号栈顶元素匹配的子过程
                target_p = [p for p in childen_procedures if p.name == self.symbol_stack[-1][2]]
                # 如果没有找到匹配的子过程
                if len(target_p) == 0:
                    # 如果当前过程没有父过程，则报错并退出
                    if cur_p.father == "":
                        # 寻找到根路径都没有找到合适的调用
                        print("ERROR: Wrong procedure call!")
                        exit(-1)
                    # 去父目录寻找有无过程名可以调用
                    cur_p = self.procedure.procedure_dict[cur_p.father]
                # 如果找到匹配的子过程
                else:
                    # 获取匹配的子过程
                    target_p = target_p[0]
                    # 在日志中插入 'CALL'，层级差为当前过程层级减去目标过程层级，目标过程地址
                    logger.insert('CALL', self.procedure.current_procedure.level + 1 - target_p.level, target_p.address)
                    break
            # 弹出符号栈的倒数第二个和最后一个元素，栈顶变为 []
            self.symbol_stack = self.symbol_stack[:-2]
    def process_read(self, generative, logger):
        """
        处理读操作的规约。

        :param generative: 当前使用的产生式
        :param logger: 日志记录器
        """
        # 如果产生式为 'READ -> READ_BEGIN )'
        if generative == 'READ -> READ_BEGIN )':
            # 弹出符号栈的最后一个元素，栈顶变为 '('
            self.symbol_stack = self.symbol_stack[:-1]
        # 如果产生式为 'READ_BEGIN -> read ( ID'
        elif generative == 'READ_BEGIN -> read ( ID':
            # 在日志中插入 'OPR'，层级差为 0，操作码为 16
            logger.insert('OPR', 0, 16)
            # 根据名称查找变量或常量
            ret = self.procedure.find_by_name(self.symbol_stack[-1][2])
            # 如果找到的是常量，则报错并退出
            if ret[2] == 0:
                print("ERROR: Assign to CONST number!")
                exit(-1)
            # 如果找到的是变量，则在日志中插入 'STO'，层级差为 ret[0]，变量的偏移量为 ret[1][1]
            else:
                logger.insert('STO', ret[0], ret[1][1])
            # 弹出符号栈的倒数第三个、倒数第二个和最后一个元素，栈顶变为 []
            self.symbol_stack = self.symbol_stack[:-3]
        # 如果产生式为 'READ_BEGIN -> READ_BEGIN , ID'
        elif generative == 'READ_BEGIN -> READ_BEGIN , ID':
            # 在日志中插入 'OPR'，层级差为 0，操作码为 16
            logger.insert('OPR', 0, 16)
            # 根据名称查找变量或常量
            ret = self.procedure.find_by_name(self.symbol_stack[-1][2])
            # 如果找到的是常量，则报错并退出
            if ret[2] == 0:
                print("ERROR: Assign to CONST number!")
                exit(-1)
            # 如果找到的是变量，则在日志中插入 'STO'，层级差为 ret[0]，变量的偏移量为 ret[1][1]
            else:
                logger.insert('STO', ret[0], ret[1][1])
            # 弹出符号栈的倒数第二个和最后一个元素，栈顶变为 []
            self.symbol_stack = self.symbol_stack[:-2]
    def process_write(self, generative, logger):
        """
        处理写操作的规约。

        :param generative: 当前使用的产生式
        :param logger: 日志记录器
        """
        pass # function body is omitted
        # 如果产生式为 'WRITE -> WRITE_BEGIN )'
        if generative == 'WRITE -> WRITE_BEGIN )':
            # 弹出符号栈的最后一个元素，栈顶变为 '('
            self.symbol_stack = self.symbol_stack[:-1]
        # 如果产生式为 'WRITE_BEGIN -> write ( ID'
        elif generative == 'WRITE_BEGIN -> write ( ID':
            # 根据名称查找变量或常量
            ret = self.procedure.find_by_name(self.symbol_stack[-1][2])
            # 如果没有找到，则报错并退出
            if ret is None:
                print("ERROR: Can't find variable ", self.symbol_stack[-1][2])
                exit(-1)
            # 如果找到的是常量
            if ret[2] == 0:
                # 在日志中插入 'LIT'，层级差为 0，常量的值为 ret[1]
                logger.insert('LIT', 0, ret[1])
                # 在日志中插入 'OPR'，层级差为 0，操作码为 14
                logger.insert('OPR', 0, 14)
            # 如果找到的是变量
            else:
                # 在日志中插入 'LOD'，层级差为 ret[0]，变量的偏移量为 ret[1][1]
                logger.insert('LOD', ret[0], ret[1][1])
                # 在日志中插入 'OPR'，层级差为 0，操作码为 14
                logger.insert('OPR', 0, 14)
            # 弹出符号栈的倒数第三个、倒数第二个和最后一个元素，栈顶变为 []
            self.symbol_stack = self.symbol_stack[:-3]
        # 如果产生式为 'WRITE_BEGIN -> WRITE_BEGIN , ID'
        elif generative == 'WRITE_BEGIN -> WRITE_BEGIN , ID':
            # 根据名称查找变量或常量
            ret = self.procedure.find_by_name(self.symbol_stack[-1][2])
            # 如果没有找到，则报错并退出
            if ret is None:
                print("ERROR: Can't find variable ", self.symbol_stack[-1][2])
                exit(-1)
            # 如果找到的是常量
            if ret[2] == 0:
                # 在日志中插入 'LIT'，层级差为 0，常量的值为 ret[1]
                logger.insert('LIT', 0, ret[1])
                # 在日志中插入 'OPR'，层级差为 0，操作码为 14
                logger.insert('OPR', 0, 14)
            # 如果找到的是变量
            else:
                # 在日志中插入 'LOD'，层级差为 ret[0]，变量的偏移量为 ret[1][1]
                logger.insert('LOD', ret[0], ret[1][1])
                # 在日志中插入 'OPR'，层级差为 0，操作码为 14
                logger.insert('OPR', 0, 14)
            # 弹出符号栈的倒数第二个和最后一个元素，栈顶变为 []
            self.symbol_stack = self.symbol_stack[:-2]
    def process_cond(self, generative, logger):
        """
        处理条件语句的生成式。

        :param generative: 当前使用的生成式
        :param logger: 日志记录器
        """
        # 如果生成式是'COND -> if CONDITION then M_COND STATEMENT'
        if generative == 'COND -> if CONDITION then M_COND STATEMENT':
            # 获取符号栈的最后一个元素
            ret = self.symbol_stack[-1]
            # 将日志中对应命令的行号设置为当前日志总行数
            logger.commands[int(ret[2]) - 1].num = logger.total_line
            # 弹出符号栈的最后四个元素
            self.symbol_stack = self.symbol_stack[:-4]
        # 如果生成式是'M_COND -> ^'
        elif generative == 'M_COND -> ^':
            # 在日志中插入'JPC'命令，目标行号为当前日志总行数加2
            logger.insert('JPC', 0, logger.total_line + 2)
            # 在日志中插入'JMP'命令，目标行号为-1
            logger.insert('JMP', 0, -1)
            # 在符号栈中添加一个元素，内容为['NUMBER', 'JMP', 当前日志总行数的字符串表示]
            self.symbol_stack.append(['NUMBER', 'JMP', str(logger.total_line)])
        # 如果生成式是'CONDITION -> EXPR REL EXPR'
        elif generative == 'CONDITION -> EXPR REL EXPR':
            # 如果符号栈的倒数第二个元素是'EQUAL'
            if self.symbol_stack[-2][0] == 'EQUAL':
                # 在日志中插入'OPR'命令，操作码为8
                logger.insert('OPR', 0, 8)
            # 如果符号栈的倒数第二个元素是'NEQUAL'
            elif self.symbol_stack[-2][0] == 'NEQUAL':
                # 在日志中插入'OPR'命令，操作码为9
                logger.insert('OPR', 0, 9)
            # 如果符号栈的倒数第二个元素是'LESS'
            elif self.symbol_stack[-2][0] == 'LESS':
                # 在日志中插入'OPR'命令，操作码为10
                logger.insert('OPR', 0, 10)
            # 如果符号栈的倒数第二个元素是'LESS_OR_EQUAL'
            elif self.symbol_stack[-2][0] == 'LESS_OR_EQUAL':
                # 在日志中插入'OPR'命令，操作码为13
                logger.insert('OPR', 0, 13)
            # 如果符号栈的倒数第二个元素是'GREATER'
            elif self.symbol_stack[-2][0] == 'GREATER':
                # 在日志中插入'OPR'命令，操作码为12
                logger.insert('OPR', 0, 12)
            # 如果符号栈的倒数第二个元素是'GREATER_OR_EQUAL'
            elif self.symbol_stack[-2][0] == 'GREATER_OR_EQUAL':
                # 在日志中插入'OPR'命令，操作码为11
                logger.insert('OPR', 0, 11)
            # 弹出符号栈的倒数第二个元素
            self.symbol_stack = self.symbol_stack[:-2]
        # 如果生成式是'CONDITION -> odd EXPR'
        elif generative == 'CONDITION -> odd EXPR':
            # 在日志中插入'OPR'命令，操作码为6
            logger.insert('OPR', 0, 6)
            # 弹出符号栈的最后一个元素
            self.symbol_stack = self.symbol_stack[:-1]
    def process_while(self, generative, logger):
        """
        处理while循环的生成式。

        :param generative: 当前使用的生成式
        :param logger: 日志记录器
        """
        # 如果生成式是'WHILE -> while M_WHILE_FORE CONDITION do M_WHILE_TAIL STATEMENT'
        if generative == 'WHILE -> while M_WHILE_FORE CONDITION do M_WHILE_TAIL STATEMENT':
            # 在日志中插入'JMP'命令，目标行号为符号栈倒数第四个元素的行号
            logger.insert('JMP', 0, self.symbol_stack[-4][2])
            # 将日志中对应命令的行号设置为当前日志总行数
            logger.commands[int(self.symbol_stack[-1][2]) - 1].num = logger.total_line
            # 弹出符号栈的最后五个元素
            self.symbol_stack = self.symbol_stack[:-5]
        # 如果生成式是'M_WHILE_FORE -> ^'
        elif generative == 'M_WHILE_FORE -> ^':
            # 在符号栈中添加一个元素，内容为['NUMBER', 'while_head', 当前日志总行数的字符串表示]
            self.symbol_stack.append(['NUMBER', 'while_head', str(logger.total_line)])
        # 如果生成式是'M_WHILE_TAIL -> ^'
        elif generative == 'M_WHILE_TAIL -> ^':
            # 在日志中插入'JPC'命令，目标行号为当前日志总行数加2
            logger.insert('JPC', 0, logger.total_line + 2)
            # 在日志中插入'JMP'命令，目标行号为-1
            logger.insert('JMP', 0, -1)
            # 在符号栈中添加一个元素，内容为['NUMBER', 'while_tail JMP', 当前日志总行数的字符串表示]
            self.symbol_stack.append(['NUMBER', 'while_tail JMP', str(logger.total_line)])
    def process_generative(self, generative, token, logger):
        """
        处理产生式的规约。

        :param generative: 当前使用的产生式
        :param token: 当前的词法单元
        :param logger: 日志记录器
        """
        # 如果产生式是常量定义的一部分
        if generative in [
            'CONST -> CONST_ ;',
            'CONST_ -> const CONST_DEF',
            'CONST_ -> CONST_ , CONST_DEF',
            'CONST_DEF -> ID = UINT'
        ]:
            # 处理常量
            self.process_const(generative)

        # 如果产生式是变量定义的一部分
        elif generative in [
            'VARIABLE -> VARIABLE_ ;',
            'VARIABLE -> ^',
            'VARIABLE_ -> var ID',
            'VARIABLE_ -> VARIABLE_ , ID'
        ]:
            # 处理变量
            self.process_var(generative)

        # 如果产生式是过程定义的一部分
        elif generative in [
            'PROCEDURE -> PROCEDURE_',
            'PROCEDURE -> ^',
            'PROCEDURE_ -> PROCEDURE_ PROC_HEAD SUBPROG ;',
            'PROCEDURE_ -> PROC_HEAD SUBPROG ;',
            'PROC_HEAD -> procedure ID ;'
        ]:
            # 处理过程
            self.process_procedure(generative)

        # 如果产生式是子过程的一部分
        elif generative in [
            'SUBPROG -> CONST VARIABLE PROCEDURE M_STATEMENT STATEMENT'
        ]:
            # 如果当前过程有父过程，则返回父过程
            if self.procedure.current_procedure.father != "":
                self.procedure.current_procedure = self.procedure.procedure_dict[
                    self.procedure.current_procedure.father]
            # 在日志中插入'OPR'命令，操作码为0
            logger.insert('OPR', 0, 0)

        # 如果产生式是赋值语句
        elif generative in [
            'ASSIGN -> ID := EXPR'
        ]:
            # 处理赋值语句
            self.process_assign(generative, logger)

        # 如果产生式是复合语句
        elif generative in [
            'COMP -> COMP_BEGIN end',
            'COMP_BEGIN -> begin STATEMENT',
            'COMP_BEGIN -> COMP_BEGIN ; STATEMENT'
        ]:
            # 处理复合语句
            self.process_comp(generative)

        # 如果产生式是因子
        elif generative in [
            'FACTOR -> ID',
            'FACTOR -> UINT',
            'FACTOR -> ( EXPR )'
        ]:
            # 处理因子
            self.process_factor(generative, logger)

        # 如果产生式是项
        elif generative in [
            'ITEM -> FACTOR',
            'ITEM -> ITEM MUL_DIV FACTOR'
        ]:
            # 处理项
            self.process_item(generative, logger)

        # 如果产生式是表达式
        elif generative in [
            'EXPR -> PLUS_MINUS ITEM',
            'EXPR -> EXPR PLUS_MINUS ITEM',
            'EXPR -> ITEM'
        ]:
            # 处理表达式
            self.process_expr(generative, logger)

        # 如果产生式是过程调用
        elif generative in ['CALL -> call ID']:
            # 处理过程调用
            self.process_call(generative, logger)

        # 如果产生式是读操作
        elif generative in [
            'READ -> READ_BEGIN )',
            'READ_BEGIN -> read ( ID',
            'READ_BEGIN -> READ_BEGIN , ID'
        ]:
            # 处理读操作
            self.process_read(generative, logger)

        # 如果产生式是写操作
        elif generative in [
            'WRITE -> WRITE_BEGIN )',
            'WRITE_BEGIN -> write ( ID',
            'WRITE_BEGIN -> WRITE_BEGIN , ID'
        ]:
            # 处理写操作
            self.process_write(generative, logger)

        # 如果产生式是条件语句
        elif generative in [
            'COND -> if CONDITION then M_COND STATEMENT',
            'M_COND -> ^',
            'CONDITION -> EXPR REL EXPR',
            'CONDITION -> odd EXPR'
        ]:
            # 处理条件语句
            self.process_cond(generative, logger)

        # 如果产生式是while循环
        elif generative in [
            'WHILE -> while M_WHILE_FORE CONDITION do M_WHILE_TAIL STATEMENT',
            'M_WHILE_FORE -> ^',
            'M_WHILE_TAIL -> ^'
        ]:
            # 处理while循环
            self.process_while(generative, logger)

        # 如果产生式是M_STATEMENT
        elif generative in [
            'M_STATEMENT -> ^'
        ]:
            # 基准的base_offset == 3，因为至少需要有2个空间来完成临时变量的计算，至少还要一个空间来保存返回地址
            volume = self.procedure.current_procedure.base_offset + len(self.procedure.current_procedure.var_dict)
            self.procedure.current_procedure.address = logger.total_line
            logger.insert('INI', 0, volume)

    # param:  待入栈的符号，需要和状态栈栈顶以及lr1_table确定下一步的动作
    # token_: 下一个待分析的词法单元的token
    def process_token(self, param, token_, logger_):
        """
        处理输入的token。

        :param param: 待入栈的符号
        :param token_: 下一个待分析的词法单元的token
        :param logger_: 日志记录器
        :return: 如果语法分析成功，返回True；否则，打印错误信息并退出程序
        """
        # 获取当前状态栈顶和param对应的动作
        cmd = str(self.parse_table[self.state_stack[-1]][param])
        # 如果动作是'acc'，表示语法分析成功
        if cmd == 'acc':
            print("SYNTAX ACCEPTED!")
            return True
        # 如果动作为空，表示语法错误
        if not cmd:
            print("ERROR:  ", token_, "  ", cmd)
            exit(-1)
        # 移入操作
        elif cmd[0] == 's':
            # 将状态和符号入栈
            self.state_stack.append(int(cmd[1:]))
            self.readable_stack.append(param)
            self.symbol_stack.append(token_)
        # 规约操作
        elif cmd[0] == 'r':
            # 获取产生式的左部和右部
            gl = self.lr1_table.G_indexed[int(cmd[1:])][0]
            gr = self.lr1_table.G_indexed[int(cmd[1:])][1]
            # 所用产生式
            generative = gl + " -> " + " ".join(gr)
            # 处理规约
            self.process_generative(generative, token_, logger_)
            # 如果右部不是空串，将状态栈和符号栈出栈
            if gr[0] != '^':
                self.state_stack = self.state_stack[0:len(self.state_stack) - len(gr)]
                self.readable_stack = self.readable_stack[0:len(self.readable_stack) - len(gr)]
            # 处理规约后的符号
            self.process_token(gl, token_, logger_)
            # 继续处理param
            self.process_token(param, token_, logger_)
        # goto操作
        else:
            # 将状态入栈
            self.state_stack.append(int(cmd))
            self.readable_stack.append(token_[1])
