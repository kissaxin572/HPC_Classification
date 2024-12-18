# 基于硬件性能计数器的容器异常行为检测方法

## 目录
1. [项目概述](#1-项目概述)
2. [数据集说明](#2-数据集说明)
3. [项目结构](#3-项目结构)
4. [实现方法](#4-实现方法)
5. [评估指标](#5-评估指标)
6. [环境配置](#6-环境配置)
7. [项目运行](#7-项目运行)
8. [未来改进](#8-未来改进)

## 1. 项目概述

本项目实现了基于硬件性能计数器（High Performance Counters, HPC）的容器异常行为检测方法。通过采集容器运行时的HPC数据,使用机器学习和深度学习方法识别潜在的恶意行为。

主要特点:
- 支持两种分类方法:传统机器学习和深度学习时序分类
- 实现多种采样策略的数据处理
- 提供完整的模型训练、评估和可视化功能
- 支持GPU加速计算

## 2. 数据集说明

### 2.1 采样策略
- **时分复用采样(TDM)**
  - 采样方式: 每次采样20个硬件事件
  - 采样周期: 10s、20s、30s
  - 采样模式: 
    * 完整时长持续采样
    * 短时间采样重复5次
    * 100ms间隔采样
    * 10ms间隔采样

- **非时分复用采样(Non-TDM)**
  - 采样方式: 每次采样4个硬件事件，分5组采集
  - 采样周期: 10s、20s、30s
  - 采样模式:
    * 完整时长持续采样
    * 短时间采样重复5次
    * 100ms间隔采样
    * 10ms间隔采样

### 2.2 数据格式
- 输入文件格式: CSV
- 字段说明:
  * 样本ID（sample_id）: 唯一标识符
  * 时间间隔（timestamp_id）: 采样时间点
  * 标签（label）: 0(良性)或1(恶意)
  * HPC特征（hpc_features）: 20个硬件性能计数器指标

## 3. 项目结构
```
F:\WORKSPACE\CODE\HPC_CLASSIFICATION
├─Datasets
│  ├─Original
│  │  └─10s
│  │      ├─20_per_1_time
│  │      │  ├─10s
│  │      │  ├─10s_100ms
│  │      │  ├─10s_10ms
│  │      │  └─2s
│  │      │      ├─2s_1
│  │      │      ├─2s_2
│  │      │      ├─2s_3
│  │      │      ├─2s_4
│  │      │      └─2s_5
│  │      └─4_per_5_times
│  │          ├─10s
│  │          ├─10s_100ms
│  │          ├─10s_10ms
│  │          └─2s
│  │              ├─2s_1
│  │              ├─2s_2
│  │              ├─2s_3
│  │              ├─2s_4
│  │              └─2s_5
│  └─Processed
│      ├─10s
│      │  ├─20_per_1_time
│      │  └─4_per_5_times
│      ├─20s
│      │  ├─20_per_1_time
│      │  └─4_per_5_times
│      └─30s
│          ├─20_per_1_time
│          └─4_per_5_times
├─Preprocess
│  ├─10s
│  │  ├─Non Time-division Multiplexing
│  │  └─Time-division Multiplexing
│  ├─20s
│  │  ├─Non Time-division Multiplexing
│  │  └─Time-division Multiplexing
│  └─30s
│      ├─Non Time-division Multiplexing
│      └─Time-division Multiplexing
├─Results
│  ├─10s
│  │  ├─Non Time-division Multiplexing
│  │  │  ├─10s
│  │  │  ├─10s_100ms
│  │  │  ├─10s_10ms
│  │  │  └─2s
│  │  └─Time-division Multiplexing
│  │      ├─10s
│  │      ├─10s_100ms
│  │      ├─10s_10ms
│  │      └─2s
│  ├─20s
│  │  ├─Non Time-division Multiplexing
│  │  │  ├─20s
│  │  │  ├─20s_200ms
│  │  │  ├─20s_20ms
│  │  │  └─4s
│  │  └─Time-division Multiplexing
│  │      ├─20s
│  │      ├─20s_200ms
│  │      ├─20s_20ms
│  │      └─4s
│  └─30s
│      ├─Non Time-division Multiplexing
│      │  ├─30s
│      │  ├─30s_300ms
│      │  ├─30s_30ms
│      │  └─6s
│      └─Time-division Multiplexing
│          ├─30s
│          ├─30s_300ms
│          ├─30s_30ms
│          └─6s
└─Scripts
```

## 4. 实现方法

### 4.1 传统机器学习方法 (Non_TSC.py)

#### 4.1.1 主要特点
- 多模型支持:
  * 逻辑回归(Logistic Regression)
  * 支持向量机(Support Vector Machine)
  * K近邻(K-Nearest Neighbors)
  * 随机森林(Random Forest)
  * 决策树(Decision Tree)
  * 朴素贝叶斯(Naive Bayes)
- 超参数优化
- 可视化分析

#### 4.1.2 处理流程
1. 数据预处理
   - 特征标准化
   - 数据集划分(训练:测试=8:2)
2. 模型训练与优化
   - GridSearchCV参数优化
   - 5折交叉验证
3. 模型评估与可视化

### 4.2 深度学习时序分类方法 (TSC.py)

#### 4.2.1 主要特点
- 时序特征保留
- 深度学习模型:
  * LSTM
  * BiLSTM
  * BiLSTM+Attention
- GPU加速支持
- 训练过程监控

#### 4.2.2 处理流程
1. 数据预处理
   - 时序数据处理
   - 三集划分(训练:验证:测试=7:1:2)
2. 模型训练
   - 批量训练
   - 早停机制
3. 模型评估与可视化

## 5. 评估指标

- Accuracy: 分类准确率
- Precision: 精确率
- Recall: 召回率
- F1-Score: F1分数
- AUC: ROC曲线下面积

## 6. 环境配置

### 6.1 基础环境
- Python >= 3.8
- CUDA >= 11.0 (GPU加速)
- cuDNN >= 8.0

### 6.2 依赖安装

```bash
# 基础科学计算
pip install numpy==1.21.0
pip install pandas==1.3.0
pip install scipy==1.7.0

# 数据可视化
pip install matplotlib==3.4.2
pip install seaborn==0.11.1

# 机器学习相关
pip install scikit-learn==0.24.2
pip install xgboost==1.4.2
pip install lightgbm==3.2.1

# 深度学习相关
pip install torch==1.9.0+cu111  # CUDA 11.1版本
pip install torchvision==0.10.0+cu111
pip install tensorboard==2.5.0  # 用于训练可视化

# 数据处理和工具
pip install tqdm==4.61.1  # 进度条
pip install joblib==1.0.1  # 模型保存和加载
pip install pandas-profiling==3.0.0  # 数据分析报告
pip install optuna==2.8.0  # 超参数优化

# 指标计算和评估
pip install sklearn-metrics==0.4.1
pip install mlxtend==0.18.0  # 用于模型集成

# 其他工具
pip install PyYAML==5.4.1  # 配置文件解析
pip install click==8.0.1  # 命令行工具
```

### 6.3 环境检查

```python
# 运行以下代码检查环境配置
import torch
import numpy
import pandas
import sklearn

print(f"PyTorch版本: {torch.__version__}")
print(f"CUDA是否可用: {torch.cuda.is_available()}")
print(f"NumPy版本: {numpy.__version__}")
print(f"Pandas版本: {pandas.__version__}")
print(f"Scikit-learn版本: {sklearn.__version__}")
```

### 6.4 注意事项
- PyTorch版本需要与CUDA版本匹配
- 建议使用虚拟环境管理依赖
- 可以使用requirements.txt统一安装:
  ```bash
  pip install -r requirements.txt
  ```

## 7. 项目运行

1. 选择采样周期和运行脚本:
```bash
# 10秒采样周期
./run_10s.sh

# 20秒采样周期
./run_20s.sh

# 30秒采样周期
./run_30s.sh
```

2. 每个运行脚本会依次执行:
   - 数据采集(TDM和Non-TDM两种方式)
   - 数据预处理
   - 模型训练(传统机器学习和深度学习)
   - 结果评估和可视化

3. 结果保存在Results目录下对应的子目录中

## 8. 未来改进

### 8.1 模型优化
- 新增模型架构
- 参数搜索优化
- 模型集成方法

### 8.2 功能扩展
- 数据格式支持
- 增量学习
- 在线预测

### 8.3 性能提升
- 数据加载优化
- 训练加速
- 内存使用优化
>>>>>>> 86792b1 (Initial commit)
