from .Grammar import Grammar


def first_follow(G):
    """
    计算给定文法 G 的 First 集和 Follow 集。

    :param G: 一个 Grammar 对象，表示给定的文法
    :return: 一个包含 First 集和 Follow 集的元组
    """
    def union(set_1, set_2):
        """
        将 set_2 中的元素添加到 set_1 中，并返回是否有新元素添加。

        :param set_1: 第一个集合
        :param set_2: 第二个集合
        :return: 如果有新元素添加则返回 True，否则返回 False
        """
        set_1_len = len(set_1)
        set_1 |= set_2
        return set_1_len != len(set_1)
    
    # 初始化 First 集和 Follow 集
    first = {symbol: set() for symbol in G.symbols}
    first.update((terminal, {terminal}) for terminal in G.terminals)  # 将终结符的 First 集初始化为其自身
    follow = {symbol: set() for symbol in G.nonterminals}
    follow[G.start].add('.')  # 将开始符号的 Follow 集初始化为包含结束符 '.'
    
    # 迭代计算 First 集和 Follow 集
    while True:
        updated = False
        for head, bodies in G.grammar.items():
            for body in bodies:
                for symbol in body:
                    if symbol != '^':
                        # 将 symbol 的 First 集（除去空串）添加到 head 的 First 集中
                        updated |= union(first[head], first[symbol] - set('^'))
                        if '^' not in first[symbol]:
                            # 如果 symbol 的 First 集中不包含空串，则停止计算
                            break
                    else:
                        # 如果 symbol 是空串，则将空串添加到 head 的 First 集中
                        updated |= union(first[head], set('^'))
                else:
                    # 如果 body 中的所有符号的 First 集都包含空串，则将空串添加到 head 的 First 集中
                    updated |= union(first[head], set('^'))
                aux = follow[head]
                for symbol in reversed(body):
                    if symbol == '^':
                        continue
                    if symbol in follow:
                        # 将 aux 集（除去空串）添加到 symbol 的 Follow 集中
                        updated |= union(follow[symbol], aux - set('^'))
                    if '^' in first[symbol]:
                        # 如果 symbol 的 First 集中包含空串，则将 aux 集与 symbol 的 First 集合并
                        aux = aux | first[symbol]
                    else:
                        # 如果 symbol 的 First 集中不包含空串，则将 aux 集更新为 symbol 的 First 集
                        aux = first[symbol]
        if not updated:
            # 如果没有更新，则返回 First 集和 Follow 集
            return first, follow

class LR1Table:
    def __init__(self, G):
        """
        初始化LR1Table对象。

        :param G: 一个Grammar对象，表示给定的文法
        """
        # 扩展文法，添加一个新的开始符号和产生式
        self.G_prime = Grammar(f"{G.start}' -> {G.start}\n{G.grammar_str}")
        # 计算扩展文法中最长产生式的长度，用于格式化输出
        self.max_G_prime_len = len(max(self.G_prime.grammar, key=len))
        self.G_indexed = []

        # 遍历扩展文法中的每个产生式，将其规范化并添加到索引列表中
        for head, bodies in self.G_prime.grammar.items():
            for body in bodies:
                self.G_indexed.append([head, body])

        # 计算扩展文法的First集和Follow集
        self.first, self.follow = first_follow(self.G_prime)

        # 构建项目集规范族
        self.Collection = self.LR1_items(self.G_prime)

        # 构建LR1分析表
        # 终结符列表，包括结束符'.'
        self.action = sorted(list(self.G_prime.terminals)) + ['.']
        # 非终结符列表，不包括扩展后的开始符号
        self.goto = sorted(list(self.G_prime.nonterminals - {self.G_prime.start}))
        # 分析表的符号列表，包括终结符和非终结符
        self.parse_table_symbols = self.action + self.goto
        # 构建LR1分析表
        self.parse_table = self.LR1_construct_table()

    def construct_follow(self, s: tuple, extra: str) -> set:
        """
        计算给定字符串 s 的 Follow 集。

        :param s: 一个元组，表示需要计算 Follow 集的字符串
        :param extra: 一个字符串，表示额外的 Follow 集元素
        :return: 一个集合，表示 s 的 Follow 集
        """
        ret = set()
        flag = True
        # 遍历字符串 s 中的每个符号 x
        for x in s:
            # 将 x 的 First 集添加到 ret 中
            ret = ret | self.first[x]
            # 如果 x 的 First 集中不包含空串，则停止计算
            if '^' not in self.first[x]:
                flag = False
                break
        # 从 ret 中移除空串
        ret.discard('^')
        # 如果字符串 s 中的所有符号的 First 集都包含空串，则将 extra 添加到 ret 中
        if flag:
            ret = ret | {extra}
        return ret
    def LR1_CLOSURE(self, dict_of_trans: dict) -> dict:
        """
        计算给定项目集的闭包。

        :param dict_of_trans: 一个字典，表示项目集
        :return: 一个字典，表示项目集的闭包
        """
        ret = dict_of_trans  # 初始化返回的闭包为输入的项目集
        while True:  # 开始循环，直到闭包不再变化
            item_len = len(ret)  # 记录当前闭包的大小
            for head, bodies in dict_of_trans.copy().items():  # 遍历项目集中的每个项目
                for body in bodies.copy():  # 遍历项目的每个产生式
                    if '.' in body[:-1]:  # 如果产生式中存在点号，且点号不在最后一个位置
                        symbol_after_dot = body[body.index('.') + 1]  # 获取点号后面的符号
                        if symbol_after_dot in self.G_prime.nonterminals:  # 如果点号后面的符号是非终结符
                            symbol_need_first_loc = body.index('.') + 2  # 获取需要计算First集的符号的位置
                            if symbol_need_first_loc == len(body):  # 如果点号后面没有其他符号（即A -> ... .B）
                                # A -> ... .B
                                for G_body in self.G_prime.grammar[symbol_after_dot]:  # 遍历B的所有产生式
                                    ret.setdefault((symbol_after_dot, head[1]), set()).add(  # 将新的项目添加到闭包中
                                        ('.',) if G_body == ('^',) else ('.',) + G_body  # 如果产生式为空，则只添加点号，否则添加点号和产生式
                                    )
                            else:  # 如果点号后面还有其他符号（即A -> ... .BC）
                                # A -> ... .BC
                                for j in self.construct_follow(body[symbol_need_first_loc:], head[1]):  # 遍历BC的Follow集
                                    for G_body in self.G_prime.grammar[symbol_after_dot]:  # 遍历B的所有产生式
                                        ret.setdefault((symbol_after_dot, j), set()).add(  # 将新的项目添加到闭包中
                                            ('.',) if G_body == ('^',) else ('.',) + G_body  # 如果产生式为空，则只添加点号，否则添加点号和产生式
                                        )
            if item_len == len(ret):  # 如果闭包的大小没有变化，说明已经计算完毕
                break  # 跳出循环
        return ret  # 返回闭包
    def LR1_GOTO(self, state: dict, c: str) -> dict:
        """
        计算给定状态和符号的 GOTO 函数。

        :param state: 一个字典，表示当前状态
        :param c: 一个字符串，表示要计算 GOTO 的符号
        :return: 一个字典，表示 GOTO 函数的结果
        """
        goto = {}  # 初始化 GOTO 函数的结果为空字典

        for head, bodies in state.items():  # 遍历当前状态中的每个项目
            for body in bodies:  # 遍历项目的每个产生式
                if '.' in body[:-1]:  # 如果产生式中存在点号，且点号不在最后一个位置
                    dot_pos = body.index('.')  # 获取点号的位置
                    if body[dot_pos + 1] == c:  # 如果点号后面的符号是 c
                        replaced_dot_body = body[:dot_pos] + (c, '.') + body[dot_pos + 2:]  # 将点号移动到 c 后面
                        for C_head, C_bodies in self.LR1_CLOSURE({head: {replaced_dot_body}}).items():  # 计算闭包
                            goto.setdefault(C_head, set()).update(C_bodies)  # 将闭包中的项目添加到 GOTO 函数的结果中

        return goto  # 返回 GOTO 函数的结果
    def LR1_items(self, G_prime):
        """
        计算给定文法的项目集规范族。

        :param G_prime: 一个Grammar对象，表示给定的扩展文法
        :return: 一个列表，表示项目集规范族
        """
        # start_item == {("S'", '#'): {('.', 'S')}}
        start_item = {(G_prime.start, '.'): {('.', G_prime.start[:-1])}}
        # 求 I0 的闭包
        C = [self.LR1_CLOSURE(start_item)]
        while True:
            item_len = len(C)
            for item in C.copy():

                for X in G_prime.symbols:
                    goto = self.LR1_GOTO(item, X)
                    if goto and goto not in C:
                        C.append(goto)

            if item_len == len(C):
                return C
    def LR1_construct_table(self):
        """
        构建LR(1)分析表。

        :return: 一个字典，表示LR(1)分析表
        """
        # 初始化分析表，行索引为状态，列索引为符号
        parse_table = {r: {c: '' for c in self.parse_table_symbols} for r in range(len(self.Collection))}

        # 遍历项目集规范族中的每个状态
        for i, I in enumerate(self.Collection):
            # 遍历状态中的每个项目
            for head, bodies in I.items():
                # 遍历项目的每个产生式
                for body in bodies:
                    # CASE 2 a: 如果点号在产生式中且不在最后一个位置，并且点号后面的符号是终结符
                    if '.' in body[:-1]:  # CASE 2 a
                        symbol_after_dot = body[body.index('.') + 1]
                        if symbol_after_dot in self.G_prime.terminals:
                            # 计算GOTO函数，获取转移到的状态
                            s = f's{self.Collection.index(self.LR1_GOTO(I, symbol_after_dot))}'
                            # 如果转移状态不在当前状态的动作表中，则添加
                            if s not in parse_table[i][symbol_after_dot]:
                                if 'r' in parse_table[i][symbol_after_dot]:
                                    parse_table[i][symbol_after_dot] += '/'
                                parse_table[i][symbol_after_dot] += s

                    # CASE 2 b: 如果点号在产生式的最后一个位置，并且产生式的头部不是扩展后的开始符号
                    elif body[-1] == '.' and head[0] != self.G_prime.start:  # CASE 2 b
                        # 遍历扩展文法的产生式索引列表，找到与当前项目匹配的产生式
                        for j, (G_head, G_body) in enumerate(self.G_indexed):
                            if G_head == head[0] and (G_body == body[:-1] or G_body == ('^',) and body == ('.',)):
                                # 如果当前状态的动作表中已经有动作，则报错
                                if parse_table[i][head[1]]:
                                    exit(-1)
                                    parse_table[i][head[1]] += '/'
                                # 将归约动作添加到动作表中
                                parse_table[i][head[1]] += f'r{j}'
                                break

                    # CASE 2 c: 如果点号在产生式的最后一个位置，并且产生式的头部是扩展后的开始符号
                    else:  # CASE 2 c
                        # 将接受动作添加到动作表中
                        parse_table[i]['.'] = 'acc'

            # CASE 3: 对于每个非终结符，计算GOTO函数，将转移状态添加到转移表中
            for A in self.G_prime.nonterminals:  # CASE 3
                j = self.LR1_GOTO(I, A)
                if j in self.Collection:
                    parse_table[i][A] = self.Collection.index(j)
        return parse_table
    def print_info(self):
        """
        打印增强文法的信息，包括产生式、终结符、非终结符和符号集。

        :return: 无
        """
        print('AUGMENTED GRAMMAR:')

        # 遍历扩展文法的产生式索引列表，打印每个产生式的编号、头部和主体
        for i, (head, body) in enumerate(self.G_indexed):
            print(f'{i:>{len(str(len(self.G_indexed) - 1))}}: {head:>{self.max_G_prime_len}} -> {" ".join(body)}')

        print()
        # 打印终结符集合
        print('TERMINALS', self.G_prime.terminals)
        # 打印非终结符集合
        print('NONTERMINALS', self.G_prime.nonterminals)
        # 打印符号集合（终结符和非终结符）
        print('SYMBOLS', self.G_prime.symbols)
