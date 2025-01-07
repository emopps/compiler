from utils import call_init_offset


# 记录过程信息，包括过程名，父过程名，过程所含变量表，所含常量表，过程嵌套深度
class ProcedureInfo:
    def __init__(self, name: str, level: int):
        """
        初始化 ProcedureInfo 对象。

        :param name: 过程名
        :param level: 过程嵌套深度
        """
        # 父过程名，初始为空
        self.father = ""
        # 过程名
        self.name = name
        # 常量字典，用于存储过程中的常量
        self.const_dict = dict()
        # 变量字典，用于存储过程中的变量
        self.var_dict = dict()
        # 基地址偏移量，调用 call_init_offset 函数获取
        self.base_offset = call_init_offset
        # 变量偏移计数器，初始化为基地址偏移量
        self.var_offset_counter = self.base_offset
        # 过程嵌套深度
        self.level = level
        # 过程地址，初始化为 -1
        self.address = -1

    def add_const(self, name: str, value: int):
        """
        向常量字典中添加一个常量。

        :param name: 常量名
        :param value: 常量值
        """
        # 如果常量名已存在，则打印错误信息并退出程序
        if name in self.const_dict:
            print("Error: redefinition in procedure " + self.name + ' of const ' + name)
            exit(-1)
        # 将常量名和常量值添加到常量字典中
        self.const_dict[name] = value

    def add_var(self, name: str):
        """
        向变量字典中添加一个变量。

        :param name: 变量名
        """
        # 如果变量名已存在，则打印错误信息并退出程序
        if name in self.var_dict:
            print("Error: redefinition in procedure " + self.name + ' of var ' + name)
            exit(-1)
        # 将变量名和变量偏移量添加到变量字典中
        self.var_dict[name] = (0, self.var_offset_counter)
        # 变量偏移计数器加 1
        self.var_offset_counter += 1

    def __str__(self):
        """
        返回 ProcedureInfo 对象的字符串表示。

        :return: ProcedureInfo 对象的字符串表示
        """
        return str(dict({
            'father': self.father,
            'name': self.name,
            'const_dict': self.const_dict,
            'var_dict': self.var_dict,
            'level': self.level
        }))

    def __repr__(self):
        """
        返回 ProcedureInfo 对象的字符串表示。

        :return: ProcedureInfo 对象的字符串表示
        """
        return self.__str__()


class Procedure:
    def __init__(self):
        """
        初始化 Procedure 对象。
        """
        # 过程字典，用于存储所有过程
        self.procedure_dict = dict()
        # 当前过程，初始化为一个空的 ProcedureInfo 对象
        self.current_procedure = ProcedureInfo("", 0)

    # 添加一个过程，构造新过程对象，切换过程上下文
    def add_procedure(self, procedure_name: str, level: int):
        """
        添加一个过程，并切换当前过程上下文。

        :param procedure_name: 过程名
        :param level: 过程嵌套深度
        """
        # 获取当前过程的名称
        father = self.current_procedure.name
        # 创建一个新的 ProcedureInfo 对象，并将其添加到过程字典中
        self.procedure_dict[procedure_name] = ProcedureInfo(procedure_name, level)
        # 切换当前过程为新创建的过程
        self.current_procedure = self.procedure_dict[procedure_name]
        # 设置新过程的父过程为当前过程的名称
        self.current_procedure.father = father

    # 当前过程新增const数据
    def add_const(self, name: str, value: int):
        """
        向当前过程的常量字典中添加一个常量。

        :param name: 常量名
        :param value: 常量值
        """
        self.current_procedure.add_const(name, value)

    # 当前过程新增var数据
    def add_var(self, name: str):
        """
        向当前过程的变量字典中添加一个变量。

        :param name: 变量名
        """
        self.current_procedure.add_var(name)

    # 按照父亲边寻找var或const, 找到var记为1, 找到const记为0
    # level差 (value, offset) 1/0
    def find_by_name(self, key: str) -> tuple[int, tuple[int, int], int]:
        """
        根据名称查找变量或常量。

        :param key: 要查找的名称
        :return: 一个元组，包含层级差、变量或常量的偏移量和类型（1表示变量，0表示常量）
        """
        # 从当前过程开始查找
        target_procedure = self.current_procedure
        while True:
            # 如果在当前过程的变量字典中找到，则返回层级差、变量的偏移量和类型1
            if key in target_procedure.var_dict:
                return [self.current_procedure.level - target_procedure.level, target_procedure.var_dict[key], 1]
            # 如果在当前过程的常量字典中找到，则返回层级差、常量的值和类型0
            if key in target_procedure.const_dict:
                return [self.current_procedure.level - target_procedure.level, target_procedure.const_dict[key], 0]
            # 如果当前过程没有父过程，则返回None
            if target_procedure.father == "":
                return None
            # 否则，切换到父过程继续查找
            else:
                target_procedure = self.procedure_dict[target_procedure.father]

    def __repr__(self):
        """
        返回 Procedure 对象的字符串表示。

        :return: Procedure 对象的字符串表示
        """
        return str(dict({
            'procedure_dict': self.procedure_dict,
            'current_procedure': self.current_procedure
        }))

    def __str__(self):
        """
        返回 Procedure 对象的字符串表示。

        :return: Procedure 对象的字符串表示
        """
        return self.__repr__()
