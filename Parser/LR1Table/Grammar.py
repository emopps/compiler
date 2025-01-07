class Grammar:
    def __init__(self, grammar_str):
        """
        初始化Grammar对象。

        :param grammar_str: 包含语法规则的字符串
        """
        # 去除空行并将字符串重新组合
        self.grammar_str = '\r'.join(filter(None, grammar_str.splitlines()))
        # 存储语法规则的字典
        self.grammar = {}
        # 存储起始符号
        self.start = None
        # 存储终结符的集合
        self.terminals = set()
        # 存储非终结符的集合
        self.nonterminals = set()

        # 遍历每一行语法规则
        for production in list(filter(None, grammar_str.splitlines())):
            # 分割产生式的头部和主体
            head, _, bodies = production.partition(' -> ')
            # 检查产生式头部是否为大写（非终结符）
            if not head.isupper():
                raise ValueError(f'\'{head} -> {bodies}\': Head \'{head}\' is not capitalized to be treated as a nonterminal.')
            # 如果起始符号尚未设置，则设置为当前产生式的头部
            if not self.start:
                self.start = head
            # 在语法字典中为当前非终结符创建一个空列表
            self.grammar.setdefault(head, [])
            # 将当前非终结符添加到非终结符集合中
            self.nonterminals.add(head)
            # 将产生式主体分割成多个产生式
            bodies = [tuple(body.split()) for body in ' '.join(bodies.split()).split('|')]

            # 遍历每个产生式
            for body in bodies:
                # 检查空符号是否在产生式中（除了空产生式）
                if '^' in body and body != ('^',):
                    raise ValueError(f'\'{head} -> {" ".join(body)}\': Null symbol \'^\' is not allowed here.')
                # 将产生式添加到当前非终结符的产生式列表中
                self.grammar[head].append(body)
                # 遍历产生式中的每个符号
                for symbol in body:
                    # 如果符号是小写（终结符）且不是空符号，则添加到终结符集合中
                    if not symbol.isupper() and symbol != '^':
                        self.terminals.add(symbol)
                    # 如果符号是大写（非终结符），则添加到非终结符集合中
                    elif symbol.isupper():
                        self.nonterminals.add(symbol)
        # 计算所有符号的集合（终结符和非终结符）
        self.symbols = self.terminals | self.nonterminals
