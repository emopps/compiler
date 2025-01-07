# 导入 os 模块，用于文件和目录操作
import os
# 从 Lexer.GenToken 模块中导入 gen_token 函数
from Lexer.GenToken import gen_token
# 从 utils 模块中导入 lexer_input_dir 和 lexer_output_dir 变量
from utils import lexer_input_dir, lexer_output_dir

def main():
    """
    主函数，用于处理输入文件并生成词法单元。
    """
    # 遍历 lexer_input_dir 目录下的所有文件
    for file in os.listdir(lexer_input_dir):
        # 打开输入文件
        with open(lexer_input_dir + "./" + file, "r") as input_file:
            # 构建输出文件的路径，将输入文件的扩展名替换为 .out
            output_file = lexer_output_dir + "./" + file.split(".")[0] + ".out"
            # 如果输出文件已经存在，则删除它
            if os.path.exists(output_file):
                os.remove(output_file)
            # 读取输入文件的第一行
            line = input_file.readline()
            # 循环处理输入文件的每一行
            while line:
                # 调用 gen_token 函数处理当前行，并将结果写入输出文件
                gen_token(line, output_file)
                # 读取输入文件的下一行
                line = input_file.readline()
        # 打印提示信息，表示词法单元已被接受
        print("LEXEME ACCEPTED!")
        # 关闭输入文件
        input_file.close()
    # 打印提示信息，表示词法分析器已成功完成
    print("LEXER DONE SUCCESSFULLY!")

# 如果当前脚本是主程序，则调用 main 函数
if __name__ == "__main__":
    main()
