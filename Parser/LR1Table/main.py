from Parser.LR1Table.GenTable import GenLR1Table, GenTableXml
from utils import grammar_file
import os


def main(grammar_file_):
    action, goto, lr1_table = GenLR1Table(grammar_file_)
    GenTableXml(action, goto, lr1_table)


if __name__ == "__main__":
    main(grammar_file)
