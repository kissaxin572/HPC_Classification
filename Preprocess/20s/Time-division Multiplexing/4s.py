import os  # 导入操作系统模块，用于处理文件和目录
import csv  # 导入CSV模块，用于读写CSV文件
import re  # 导入正则表达式模块，用于字符串匹配和处理
from tqdm import tqdm  # 导入tqdm模块，用于显示进度条

def extract_counter_value(line):
    # 从给定的行中提取计数器的值
    match = re.search(r'^\s*([0-9,]+|\<not counted\>)', line)  # 匹配数字或<not counted>
    if match:
        value = match.group(1)  # 获取匹配的值
        if value == '<not counted>':
            return 0  # 如果值为<not counted>，返回0
        return int(value.replace(',', ''))  # 移除逗号并返回整数值
    return 0  # 如果没有匹配，返回0

def process_file(file_path):
    # 处理单个文件，提取性能计数器的值
    counters = {}  # 初始化一个字典来存储计数器值
    with open(file_path, 'r') as f:  # 打开文件
        lines = f.readlines()  # 读取所有行
        for line in lines:  # 遍历每一行
            # 检查行中是否包含任何计数器名称
            if any(counter in line for counter in [
                'branch-instructions', 'branch-misses', 'bus-cycles',
                'cache-misses', 'cache-references', 'cpu-cycles',
                'instructions', 'ref-cycles', 'L1-dcache-load-misses',
                'L1-dcache-loads', 'L1-dcache-stores', 'L1-icache-load-misses',
                'LLC-loads', 'LLC-stores', 'branch-load-misses',
                'dTLB-load-misses', 'dTLB-loads', 'dTLB-store-misses',
                'dTLB-stores', 'iTLB-load-misses'
            ]):
                value = extract_counter_value(line)  # 提取计数器值
                counter_name = line.split()[1]  # 获取计数器名称
                counters[counter_name] = value  # 将计数器名称和对应值存入字典
    return counters  # 返回计数器字典

def get_sample_order(filename):
    # 从文件名中提取编号，例如 'B_1.txt' 返回 (B, 1)
    parts = filename.split('_')
    sample_type = parts[0]  # B 或 M
    sample_num = int(parts[1].split('.')[0])  # 提取数字部分
    return (sample_type, sample_num)

def main():
    # 获取项目根目录的绝对路径
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    
    # 使用os.path.join()构建完整的路径
    input_dirs = [os.path.join(project_root, 'Datasets', 'Original', '20s', '20_per_1_time', '4s', f'4s_{i}') for i in range(1, 6)]
    output_file = os.path.join(project_root, 'Datasets', 'Processed', '20s', '20_per_1_time', '4s.csv')

    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    features = [
        'branch-instructions', 'branch-misses', 'bus-cycles',
        'cache-misses', 'cache-references', 'cpu-cycles',
        'instructions', 'ref-cycles', 'L1-dcache-load-misses',
        'L1-dcache-loads', 'L1-dcache-stores', 'L1-icache-load-misses',
        'LLC-loads', 'LLC-stores', 'branch-load-misses',
        'dTLB-load-misses', 'dTLB-loads', 'dTLB-store-misses',
        'dTLB-stores', 'iTLB-load-misses'
    ]

    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(features + ['label'])

        # 获取第一个目录中的所有文件并按照样本编号排序，用作基准顺序
        base_files = sorted(
            [f for f in os.listdir(input_dirs[0]) if f.endswith('.txt')],
            key=get_sample_order
        )

        # 按照基准顺序处理每个样本
        for filename in tqdm(base_files, desc="处理样本文件"):  # 添加进度条
            is_malicious = 1 if filename.startswith('M_') else 0
            sample_name = filename.split('.')[0]  # 获取不带扩展名的文件名
            
            # 处理该样本在所有时间点的数据
            for input_dir in input_dirs:
                file_path = os.path.join(input_dir, filename)
                counters = process_file(file_path)
                row = [counters.get(feature, 0) for feature in features]
                row.append(is_malicious)
                writer.writerow(row)

if __name__ == '__main__':
    main()  # 执行主函数 