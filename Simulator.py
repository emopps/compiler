from Simulator.Machine import Machine
# import Machine
import os
from utils import parser_output_dir

# 定义你要执行的文件
parser_output_file_ = os.path.join(r'c:\Users\Lenovo\Downloads\编译原理课程设计\Parser\ParserOutput', "PL0_code.out")

def main(parser_output_file):
    code = list(filter(lambda x: x != "", open(parser_output_file).read().split('\n')))
    s = Machine(code)
    s.run()

if __name__ == '__main__':
    main(parser_output_file_)
