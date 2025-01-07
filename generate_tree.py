import os

def generate_tree(directory, prefix=""):
    for item in os.listdir(directory):
        path = os.path.join(directory, item)
        if os.path.isdir(path):
            print(f"{prefix}├── {item}")
            generate_tree(path, prefix + "│   ")
        else:
            print(f"{prefix}├── {item}")

if __name__ == "__main__":
    target_directory = r"C:\Users\Lenovo\Downloads\编译原理课程设计"  # 修改为目标目录
    generate_tree(target_directory)