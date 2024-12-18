import os  # 导入操作系统模块，用于文件和目录操作
import pandas as pd  # 导入pandas库，用于数据处理和分析
import numpy as np  # 导入numpy库，用于数值计算
import re  # 导入正则表达式模块，用于字符串处理
from tqdm import tqdm  # 导入tqdm库，用于显示进度条

def parse_hpc_file(file_path):
    # 提取文件名中的信息
    filename = os.path.basename(file_path)  # 获取文件名
    x, y, z = filename.split('_')  # 将文件名按'_'分割为x, y, z
    z = z.split('.')[0]  # 去掉文件扩展名
    
    # 读取文件内容
    data = []  # 初始化数据列表
    current_time = None  # 当前时间初始化为None
    current_values = {}  # 当前值初始化为空字典
    
    with open(file_path, 'r') as f:  # 打开文件
        for line in f:  # 遍历文件中的每一行
            if line.startswith('#') or not line.strip():  # 跳过注释行和空行
                continue
                
            parts = line.strip().split()  # 去除行首尾空白并分割成部分
            if len(parts) < 3:  # 如果分割后的部分少于3，跳过该行
                continue
            
            # 处理<not counted>的情况
            if '<not counted>' in line:  # 检查是否包含<not counted>
                time = float(parts[0])  # 获取时间
                value = 0  # 设置值为0
                event = parts[3]  # 获取事件名称
            else:
                time = float(parts[0])  # 获取时间
                value = parts[1]  # 获取值
                event = parts[2]  # 获取事件名称
            
            # 转换数值
            if value != 0:  # 如果值不为0
                try:
                    value = int(value.replace(',', ''))  # 尝试将值转换为整数
                except ValueError:  # 如果转换失败
                    value = 0  # 设置值为0
                
            if current_time != time:  # 如果当前时间与读取的时间不同
                if current_time is not None:  # 如果当前时间不为None
                    data.append([current_time, current_values.copy()])  # 将当前时间和当前值添加到数据列表
                current_time = time  # 更新当前时间
                current_values = {}  # 重置当前值为一个空字典
                
            current_values[event] = value  # 更新当前值字典中的事件值
            
        if current_time is not None:  # 如果当前时间不为None
            data.append([current_time, current_values.copy()])  # 将最后的时间和当前值添加到数据列表
            
    return x, y, z, data  # 返回提取的信息和数据

def process_folder(input_dirs, output_file):
    """处理文件夹中的所有HPC数据文件并生成CSV"""
    hpc_events = [  # 定义HPC事件列表
        "branch-instructions", "branch-misses", "bus-cycles", "cache-misses",
        "cache-references", "cpu-cycles", "instructions", "ref-cycles",
        "L1-dcache-load-misses", "L1-dcache-loads", "L1-dcache-stores",
        "L1-icache-load-misses", "LLC-loads", "LLC-stores", "branch-load-misses",
        "dTLB-load-misses", "dTLB-loads", "dTLB-store-misses", "dTLB-stores",
        "iTLB-load-misses"
    ]
    
    all_data = {}  # 初始化所有数据字典
    files_by_id = {}  # 初始化按ID分组的文件字典
    
    # 收集和分组文件
    files = sorted([file for file in os.listdir(input_dirs) if file.endswith('.txt')], key=lambda f: (f.split('_')[0], int(f.split('_')[1])))  # 获取所有.txt文件并按照自然序排列
    
    for file in tqdm(files, desc="收集文件"):  # 显示进度条
        x, y = file.split('_')[:2]  # 获取文件名中的x和y
        id_key = f"{x}_{y}"  # 创建ID键
        if id_key not in files_by_id:  # 如果ID键不在字典中
            files_by_id[id_key] = {}  # 初始化该ID键的字典
        z = file.split('_')[2].split('.')[0]  # 获取z值
        files_by_id[id_key][z] = file  # 将文件添加到对应的ID键下
    
    # 处理每个分组
    for id_key in files_by_id.keys():  # 按照自然顺序排序ID键
        z_files = files_by_id[id_key]  # 获取对应的文件
        x, y = id_key.split('_')  # 分割ID键为x和y
        all_data[id_key] = [{} for _ in range(100)]  # 初始化该ID键的100个时间点的数据
        
        # 按照原始文件夹中的文件排列的顺序处理文件
        for file in tqdm(z_files.values(), desc=f"处理 {id_key} 的文件"):  # 显示进度条
            file_path = os.path.join(input_dirs, file)  # 获取文件的完整路径
            _, _, _, data = parse_hpc_file(file_path)  # 解析HPC文件
            
            for time_idx in range(100):  # 遍历时间索引从0到99
                if time_idx < len(data):  # 如果时间索引在数据范围内
                    time, values = data[time_idx]  # 获取对应的时间和数值
                    all_data[id_key][time_idx].update(values)  # 更新该时间点的值
                else:
                    all_data[id_key][time_idx] = {event: 0 for event in hpc_events}  # 用0填充不足100的时间点
    
    # 转换为DataFrame格式
    rows = []  # 初始化行列表
    for id_key, time_series in all_data.items():  # 遍历所有数据
        x, y = id_key.split('_')  # 分割ID键为x和y
        for time_idx, values in enumerate(time_series):  # 遍历时间序列
            row = {  # 创建一行数据
                'sample_id': id_key,  # ID
                'timestamp_id': time_idx + 1,  # 时间戳ID
                'label': 1 if x == 'M' else 0  # 分类
            }
            
            for event in hpc_events:  # 遍历所有HPC事件
                row[event] = values.get(event, 0)  # 获取事件值，默认为0
                
            rows.append(row)  # 将行添加到行列表
    
    # 创建DataFrame
    df = pd.DataFrame(rows)  # 将行列表转换为DataFrame
    columns = ['sample_id', 'timestamp_id', 'label'] + hpc_events  # 定义列顺序
    df = df[columns]  # 重新排列DataFrame的列顺序
    
    # 排序数据
    def extract_number(id_str):  # 定义提取数字的函数
        return int(id_str.split('_')[1])  # 从ID字符串中提取数字
    
    df['sort_key'] = df['sample_id'].apply(lambda x: (x.startswith('M'), extract_number(x)))  # 创建排序键
    df_sorted = df.sort_values(['sort_key', 'timestamp_id'])  # 按排序键和时间戳排序
    df_sorted = df_sorted.drop('sort_key', axis=1)  # 删除排序键列
    
    # 保存排序后的数据
    df_sorted.to_csv(output_file, index=False)  # 将排序后的数据保存为CSV文件
    
    return df_sorted  # 返回排序后的DataFrame

def main():
    """主函数"""
    # 获取项目根目录的绝对路径
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    
    # 使用os.path.join()构建完整的路径
    input_dirs = os.path.join(project_root, 'Datasets', 'Original', '30s', '4_per_5_times', '30s_300ms')
    output_file = os.path.join(project_root, 'Datasets', 'Processed', '30s', '4_per_5_times', '30s_300ms.csv')

    # 创建输出目录(如果不存在)
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # 处理数据并保存排序后的文件
    print("正在处理和排序HPC数据...")  # 打印处理信息
    df_sorted = process_folder(input_dirs, output_file)  # 处理文件夹中的数据
    print(f"已生成排序后的文件: {output_file}")  # 打印生成文件的信息

if __name__ == "__main__":
    main()  # 运行主函数