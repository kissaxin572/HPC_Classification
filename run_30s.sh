#!/bin/bash

# 设置颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 检查是否在正确的目录下运行脚本
if [ ! -f "${SCRIPT_DIR}/Non_TSC_30s.py" ] || [ ! -f "${SCRIPT_DIR}/TSC_30s.py" ]; then
    echo -e "${RED}错误: 请在项目根目录下运行此脚本${NC}"
    exit 1
fi

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}开始执行容器异常行为检测${NC}"
echo -e "${GREEN}========================================${NC}"

# 检查必要目录是否存在
echo -e "${YELLOW}检查并创建必要的目录...${NC}"
mkdir -p "${SCRIPT_DIR}/Datasets/Processed/30s/"{20_per_1_time,4_per_5_times}
mkdir -p "${SCRIPT_DIR}/Results/30s/"{Time-division\ Multiplexing,Non\ Time-division\ Multiplexing}/{30s,30s_300ms,30s_30ms,6s}

# 检查原始数据目录是否存在
if [ ! -d "${SCRIPT_DIR}/Datasets/Original/30s" ]; then
    echo -e "${RED}错误: 原始数据目录不存在${NC}"
    exit 1
fi

# 1. 执行数据预处理 - 时分复用采样
echo -e "${YELLOW}开始处理时分复用采样数据...${NC}"
cd "${SCRIPT_DIR}/Preprocess/30s/Time-division Multiplexing" || exit 1
for script in 6s.py 30s.py 30s_300ms.py 30s_30ms.py; do
    if [ ! -f "$script" ]; then
        echo -e "${RED}错误: 预处理脚本不存在: $script${NC}"
        exit 1
    fi
    echo -e "${GREEN}执行 $script${NC}"
    python "$script"
    if [ $? -ne 0 ]; then
        echo -e "${RED}错误: $script 执行失败${NC}"
        exit 1
    fi
done
cd "${SCRIPT_DIR}" || exit 1

# 2. 执行数据预处理 - 非时分复用采样
echo -e "${YELLOW}开始处理非时分复用采样数据...${NC}"
cd "${SCRIPT_DIR}/Preprocess/30s/Non Time-division Multiplexing" || exit 1
for script in 6s.py 30s.py 30s_300ms.py 30s_30ms.py; do
    if [ ! -f "$script" ]; then
        echo -e "${RED}错误: 预处理脚本不存在: $script${NC}"
        exit 1
    fi
    echo -e "${GREEN}执行 $script${NC}"
    python "$script"
    if [ $? -ne 0 ]; then
        echo -e "${RED}错误: $script 执行失败${NC}"
        exit 1
    fi
done
cd "${SCRIPT_DIR}" || exit 1

# 检查预处理结果
echo -e "${YELLOW}检查预处理结果...${NC}"
required_files=(
    "${SCRIPT_DIR}/Datasets/Processed/30s/20_per_1_time/30s.csv"
    "${SCRIPT_DIR}/Datasets/Processed/30s/20_per_1_time/30s_300ms.csv"
    "${SCRIPT_DIR}/Datasets/Processed/30s/20_per_1_time/30s_30ms.csv"
    "${SCRIPT_DIR}/Datasets/Processed/30s/20_per_1_time/6s.csv"
    "${SCRIPT_DIR}/Datasets/Processed/30s/4_per_5_times/30s.csv"
    "${SCRIPT_DIR}/Datasets/Processed/30s/4_per_5_times/30s_300ms.csv"
    "${SCRIPT_DIR}/Datasets/Processed/30s/4_per_5_times/30s_30ms.csv"
    "${SCRIPT_DIR}/Datasets/Processed/30s/4_per_5_times/6s.csv"
)

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo -e "${RED}错误: 预处理结果文件不存在: $file${NC}"
        exit 1
    fi
done

# 3. 执行传统机器学习分类
echo -e "${YELLOW}开始执行传统机器学习分类...${NC}"
cd "${SCRIPT_DIR}" || exit 1
python Non_TSC_30s.py
if [ $? -ne 0 ]; then
    echo -e "${RED}错误: Non_TSC_30s.py 执行失败${NC}"
    exit 1
fi
echo -e "${GREEN}传统机器学习分类完成${NC}"

# 4. 执行深度学习时序分类
echo -e "${YELLOW}开始执行深度学习时序分类...${NC}"
python TSC_30s.py
if [ $? -ne 0 ]; then
    echo -e "${RED}错误: TSC_30s.py 执行失败${NC}"
    exit 1
fi
echo -e "${GREEN}深度学习时序分类完成${NC}"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}所有任务执行完成！${NC}"
echo -e "${GREEN}结果已保存到 Results 目录${NC}"
echo -e "${GREEN}========================================${NC}"

# 显示结果文件统计
echo -e "${YELLOW}生成结果统计:${NC}"
echo "时分复用结果文件数量:"
find "${SCRIPT_DIR}/Results/30s/Time-division Multiplexing" -type f | wc -l
echo "非时分复用结果文件数量:"
find "${SCRIPT_DIR}/Results/30s/Non Time-division Multiplexing" -type f | wc -l 