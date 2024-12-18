import os  # 导入操作系统模块,用于文件和目录操作
import csv  # 导入csv模块,用于读写CSV文件
import re  # 导入正则表达式模块,用于字符串处理
from tqdm import tqdm  # 导入tqdm模块,用于显示进度条

def extract_counter_value(line):
    """从性能计数器输出行中提取数值
    
    Args:
        line: 包含性能计数器数据的字符串行
        
    Returns:
        int: 提取的计数器值,如果无法提取则返回0
    """
    match = re.search(r'^\s*([0-9,]+|\<not counted\>)', line)  # 使用正则表达式匹配数值或<not counted>
    if match:
        value = match.group(1)  # 获取匹配的第一个分组
        if value == '<not counted>':  # 如果是<not counted>
            return 0  # 返回0
        return int(value.replace(',', ''))  # 移除逗号并转换为整数
    return 0  # 如果没有匹配则返回0

def process_files(file_paths):
    """处理多个性能计数器数据文件
    
    Args:
        file_paths: 性能计数器数据文件路径列表
        
    Returns:
        dict: 包含所有计数器名称和对应值的字典
    """
    counters = {}  # 初始化计数器字典
    for file_path in file_paths:  # 遍历每个文件
        with open(file_path, 'r') as f:  # 打开文件
            lines = f.readlines()  # 读取所有行
            for line in lines:  # 遍历每一行
                # 检查行中是否包含任意一个性能计数器名称
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
                    counters[counter_name] = value  # 存储计数器值
    return counters

def get_file_order(filename):
    """从文件名中提取排序所需的编号
    
    Args:
        filename: 文件名字符串
        
    Returns:
        tuple: 包含两个整数的元组,用于文件排序
    """
    parts = filename.split('_')  # 按下划线分割文件名
    return (int(parts[1]), int(parts[2].split('.')[0]))  # 返回两个数字作为排序依据

def main():
    """主函数,处理性能计数器数据并生成CSV文件"""
    # 获取项目根目录的绝对路径
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    
    # 使用os.path.join()构建完整的路径
    input_dirs = [os.path.join(project_root, 'Datasets', 'Original', '10s', '4_per_5_times', '2s', f'2s_{i}') for i in range(1, 6)]
    output_file = os.path.join(project_root, 'Datasets', 'Processed', '10s', '4_per_5_times', '2s.csv')

    # 创建输出目录(如果不存在)
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # 定义要处理的性能计数器特征列表
    features = [
        'branch-instructions', 'branch-misses', 'bus-cycles',
        'cache-misses', 'cache-references', 'cpu-cycles',
        'instructions', 'ref-cycles', 'L1-dcache-load-misses',
        'L1-dcache-loads', 'L1-dcache-stores', 'L1-icache-load-misses',
        'LLC-loads', 'LLC-stores', 'branch-load-misses',
        'dTLB-load-misses', 'dTLB-loads', 'dTLB-store-misses',
        'dTLB-stores', 'iTLB-load-misses'
    ]

    with open(output_file, 'w', newline='') as f:  # 打开输出文件
        writer = csv.writer(f)  # 创建CSV写入器
        writer.writerow(features + ['label'])  # 写入表头

        # 获取所有样本的所有文件
        sample_files = {}  # 初始化样本文件字典
        for input_dir in input_dirs:  # 遍历每个输入目录
            all_files = sorted(os.listdir(input_dir), key=get_file_order)  # 获取并排序目录中的文件
            for filename in all_files:  # 遍历每个文件
                if filename.endswith('.txt'):  # 只处理txt文件
                    parts = filename.split('_')  # 分割文件名
                    sample_name = f"{parts[0]}_{parts[1]}"  # 构建样本名称
                    if sample_name not in sample_files:  # 如果样本名称不在字典中
                        sample_files[sample_name] = {i: [] for i in range(1, 6)}  # 初始化该样本的文件列表
                    dir_num = int(input_dir.split('_')[-1])  # 获取目录编号
                    sample_files[sample_name][dir_num].append(os.path.join(input_dir, filename))  # 添加文件路径

        # 按样本编号排序处理
        for sample_name in sorted(sample_files.keys(), key=lambda x: (x[0], int(x.split('_')[1]))):
            is_malicious = 1 if sample_name.startswith('M_') else 0  # 判断是否为恶意样本
            
            # 处理每个样本在每个时间点的5个文件
            for dir_num in range(1, 6):  # 遍历5个目录
                counters = {}  # 初始化计数器字典
                files_to_process = sorted(sample_files[sample_name][dir_num], 
                                 key=lambda x: int(x.split('_')[-1].split('.')[0]))  # 排序要处理的文件
                for file in tqdm(files_to_process, desc=f"处理 {sample_name} 的 {dir_num} 目录文件"):  # 显示处理进度
                    file_counters = process_files([file])  # 处理单个文件
                    counters.update(file_counters)  # 更新计数器字典

                row = [counters.get(feature, 0) for feature in features]  # 构建数据行
                row.append(is_malicious)  # 添加标签
                writer.writerow(row)  # 写入CSV文件

if __name__ == '__main__':
    main()  # 运行主函数