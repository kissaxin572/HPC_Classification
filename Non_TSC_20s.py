# 导入必要的库
import pandas as pd  # 用于数据处理和分析
import numpy as np  # 用于数值计算
import matplotlib.pyplot as plt  # 用于绘图
import seaborn as sns  # 用于统计数据可视化
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score  # 用于数据集划分和模型选择
from sklearn.preprocessing import StandardScaler  # 用于特征标准化
from sklearn.linear_model import LogisticRegression  # 逻辑回归模型
from sklearn.svm import SVC  # 支持向量机模型
from sklearn.neighbors import KNeighborsClassifier  # K近邻分类器
from sklearn.ensemble import RandomForestClassifier  # 随机森林分类器
from sklearn.tree import DecisionTreeClassifier  # 决策树分类器
from sklearn.naive_bayes import GaussianNB  # 高斯朴素贝叶斯分类器
from sklearn.metrics import (  # 各种评估指标
    classification_report,  # 分类报告
    confusion_matrix,  # 混淆矩阵
    roc_curve,  # ROC曲线
    auc,  # AUC值计算
    accuracy_score,  # 准确率
    precision_score,  # 精确率
    recall_score,  # 召回率
    f1_score,  # F1分数
    roc_auc_score  # ROC曲线下面积
)
import os  # 用于文件和目录操作

# 设置matplotlib绘图参数
plt.rcParams['font.family'] = 'Times New Roman'  # 设置字体为Times New Roman
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题


def load_and_preprocess_data(data_path):
    """加载并预处理数据
    
    该函数完成以下任务:
    1. 检查数据文件是否存在
    2. 加载CSV数据文件
    3. 分离特征和标签
    4. 划分训练集和测试集
    5. 对特征进行标准化处理
    
    Args:
        data_path: 数据集文件路径
        
    Returns:
        X_train: 训练集特征
        X_test: 测试集特征  
        y_train: 训练集标签
        y_test: 测试集标签
    """
    # 检查数据文件是否存在
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"数据文件不存在: {data_path}")
        
    # 加载数据
    data = pd.read_csv(data_path)
    X = data.iloc[:, :-1]  # 取除最后一列外的所有列作为特征
    y = data.iloc[:, -1]  # 取最后一列作为标签
    
    # 划分训练集和测试集,测试集占20%
    X_train, X_test, y_train, y_test = train_test_split(
        X, 
        y, 
        test_size=0.2,  # 测试集比例为20%
        random_state=42,  # 设置随机种子,确保结果可复现
        stratify=y  # 保持标签分布一致
    )
    
    # 标准化特征
    scaler = StandardScaler()  # 创建标准化对象
    X_train = scaler.fit_transform(X_train)  # 对训练集拟合和转换
    X_test = scaler.transform(X_test)  # 对测试集仅做转换
    
    return X_train, X_test, y_train, y_test


def plot_class_distribution(y_train, y_test, result_dir):
    """绘制训练集和测试集的类别分布饼图
    
    该函数完成以下任务:
    1. 统计训练集和测试集中各类别的样本数
    2. 计算样本总数
    3. 生成饼图标签
    4. 绘制并保存饼图
    
    Args:
        y_train: 训练集标签
        y_test: 测试集标签
        result_dir: 结果保存目录
    """
    # 统计各类别样本数
    train_counts = np.bincount(y_train)  # 统计训练集各类别数量
    test_counts = np.bincount(y_test)  # 统计测试集各类别数量
    
    # 计算样本总数
    total_train = len(y_train)
    total_test = len(y_test)
    
    # 生成饼图标签
    train_labels = [f'Class {i}\n({count} samples)' for i, count in enumerate(train_counts)]
    test_labels = [f'Class {i}\n({count} samples)' for i, count in enumerate(test_counts)]
    
    # 创建图形
    plt.figure(figsize=(15, 7))
    
    # 绘制训练集分布饼图
    plt.subplot(1, 2, 1)
    plt.pie(train_counts, labels=train_labels, autopct='%1.1f%%', startangle=90)
    plt.title(f'Training Set Distribution\nTotal: {total_train} samples')
    
    # 绘制测试集分布饼图
    plt.subplot(1, 2, 2)
    plt.pie(test_counts, labels=test_labels, autopct='%1.1f%%', startangle=90)
    plt.title(f'Test Set Distribution\nTotal: {total_test} samples')
    
    # 保存图形
    plt.savefig(os.path.join(result_dir, 'class_distribution.svg'), format='svg', bbox_inches='tight')
    plt.close()


def evaluate_and_visualize(model, X_test, y_test, model_name, result_dir):
    """评估模型性能并生成可视化结果
    
    该函数完成以下任务:
    1. 获取模型预测结果
    2. 计算各项评估指标
    3. 保存评估结果到文本文件
    4. 绘制混淆矩阵
    5. 将结果保存到CSV文件
    
    Args:
        model: 训练好的模型
        X_test: 测试集特征
        y_test: 测试集标签
        model_name: 模型名称
        result_dir: 结果保存目录
        
    Returns:
        accuracy, precision, recall, f1, auc: 各项评估指标
    """
    # 确保结果目录存在
    os.makedirs(result_dir, exist_ok=True)
    
    # 获取预测结果
    y_pred = model.predict(X_test)  # 预测类别
    y_prob = model.predict_proba(X_test)[:, 1]  # 预测概率
    
    # 计算评估指标
    accuracy = accuracy_score(y_test, y_pred)  # 准确率
    precision = precision_score(y_test, y_pred)  # 精确率
    recall = recall_score(y_test, y_pred)  # 召回率
    f1 = f1_score(y_test, y_pred)  # F1分数
    auc_score = roc_auc_score(y_test, y_prob)  # AUC值
    
    # 保存结果到文本文件
    results_file = os.path.join(result_dir, "model_results.txt")
    with open(results_file, 'a', encoding='utf-8') as f:
        f.write(f"\n{model_name} 评估结果:\n")
        f.write(f"Accuracy: {accuracy:.4f}\n")
        f.write(f"Precision: {precision:.4f}\n")
        f.write(f"Recall: {recall:.4f}\n")
        f.write(f"F1-Score: {f1:.4f}\n")
        f.write(f"AUC: {auc_score:.4f}\n")
    
    # 绘制混淆矩阵
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(
        cm, 
        annot=True,  # 显示数值
        fmt='d',  # 数值格式为整数
        cmap='Blues',  # 使用蓝色调色板
        xticklabels=["Benign", "Malware"],  # x轴标签
        yticklabels=["Benign", "Malware"]  # y轴标签
    )
    plt.title(f"Confusion Matrix - {model_name}")
    plt.xlabel("Predicted")
    plt.ylabel("True")
    
    # 保存混淆矩阵图
    cm_file = os.path.join(result_dir, f"confusion_matrix_{model_name}.png")
    plt.savefig(cm_file, bbox_inches='tight', dpi=300)
    plt.close()
    
    # 保存结果到CSV
    results_df = pd.DataFrame({
        "Model": [model_name],
        "Accuracy": [accuracy],
        "Precision": [precision],
        "Recall": [recall],
        "F1-Score": [f1],
        "AUC": [auc_score]
    })
    
    csv_file = os.path.join(result_dir, "model_evaluation_results.csv")
    # 如果CSV文件已存在且非空，则不写入表头
    header = not (os.path.exists(csv_file) and os.path.getsize(csv_file) > 0)
    results_df.to_csv(csv_file, mode='a', header=header, index=False)
    
    return accuracy, precision, recall, f1, auc_score


def train_and_evaluate_models(X_train, X_test, y_train, y_test, result_dir):
    """训练和评估多个机器学习模型
    
    该函数完成以下任务:
    1. 定义多个模型及其超参数搜索空间
    2. 对每个模型进行网格搜索找最优参数
    3. 使用最优参数训练模型
    4. 评估模型性能并可视化结果
    
    Args:
        X_train: 训练集特征
        X_test: 测试集特征
        y_train: 训练集标签
        y_test: 测试集标签
        result_dir: 结果保存目录
        
    Returns:
        metrics: 包含所有模型评估指标的列表
    """
    # 定义模型及其超参数网格
    models = {
        'Logistic Regression': (
            LogisticRegression(max_iter=500),
            {'C': [0.1, 1, 10]}  # 正则化参数
        ),
        'SVM': (
            SVC(probability=True),
            {
                'C': [0.1, 1, 10],  # 正则化参数
                'kernel': ['linear', 'rbf']  # 核函数类型
            }
        ),
        'KNN': (
            KNeighborsClassifier(),
            {'n_neighbors': [3, 5, 7]}  # 近邻数
        ),
        'Random Forest': (
            RandomForestClassifier(),
            {'n_estimators': [10, 50, 100]}  # 树的数量
        ),
        'Decision Tree': (
            DecisionTreeClassifier(),
            {'max_depth': [None, 10, 20]}  # 树的最大深度
        ),
        'Naive Bayes': (
            GaussianNB(),
            {}  # 朴素贝叶斯没有主要超参数需要调整
        )
    }
    
    metrics = []
    
    # 对每个模型进行训练和评估
    for model_name, (model, params) in models.items():
        print(f"\n训练 {model_name}...")
        
        # 网格搜索找最优参数
        grid_search = GridSearchCV(
            model,
            params,
            cv=5,  # 5折交叉验证
            scoring='accuracy',  # 使用准确率作为评估指标
            n_jobs=-1  # 使用所有CPU核心
        )
        grid_search.fit(X_train, y_train)
        
        # 使用最佳参数的模型进行评估
        best_model = grid_search.best_estimator_
        acc, prec, rec, f1, auc = evaluate_and_visualize(
            best_model, 
            X_test, 
            y_test, 
            model_name, 
            result_dir
        )
        
        metrics.append({
            "Model": model_name,
            "Accuracy": acc,
            "Precision": prec,
            "Recall": rec,
            "F1-Score": f1,
            "AUC": auc
        })
    
    return metrics


def plot_performance_comparison(metrics, result_dir):
    """绘制模型性能对比图
    
    该函数完成以下任务:
    1. 将评估指标转换为DataFrame
    2. 创建柱状图比较不同模型的性能
    3. 添加数值标签和图例
    4. 保存比较结果
    
    Args:
        metrics: 包含所有模型评估指标的列表
        result_dir: 结果保存目录
    """
    df = pd.DataFrame(metrics)
    df.set_index('Model', inplace=True)
    
    # 创建柱状图
    plt.figure(figsize=(14, 8))
    ax = df[['Accuracy', 'Precision', 'Recall', 'F1-Score', 'AUC']].plot(
        kind='bar',
        title="Model Performance Comparison",
        rot=0  # 横轴标签不旋转
    )
    
    plt.ylabel("Score")
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # 添加数值标签
    for container in ax.containers:
        ax.bar_label(container, fmt='%.2f')
    
    plt.tight_layout()
    plt.savefig(os.path.join(result_dir, "model_performance_comparison.png"))
    plt.close()


def process_dataset(data_path, result_dir):
    """处理单个数据集的完整流程
    
    该函数完成以下任务:
    1. 检查数据文件和目录权限
    2. 加载和预处理数据
    3. 绘制数据分布
    4. 训练和评估模型
    5. 绘制性能对比图
    
    Args:
        data_path: 数据集文件路径
        result_dir: 结果保存目录
    """
    try:
        # 检查数据文件是否存在
        if not os.path.exists(data_path):
            raise FileNotFoundError(f"数据文件不存在: {data_path}")
            
        # 创建结果目录
        os.makedirs(result_dir, exist_ok=True)
        
        # 检查是否有写入权限
        test_file = os.path.join(result_dir, "test_write.tmp")
        try:
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
        except Exception as e:
            raise PermissionError(f"无法写入结果目录 {result_dir}: {str(e)}")
        
        # 加载和预处理数据
        X_train, X_test, y_train, y_test = load_and_preprocess_data(data_path)
        
        # 绘制数据分布
        plot_class_distribution(y_train, y_test, result_dir)
        
        # 训练和评估模型
        metrics = train_and_evaluate_models(X_train, X_test, y_train, y_test, result_dir)
        
        # 绘制性能对比图
        plot_performance_comparison(metrics, result_dir)
        
    except Exception as e:
        print(f"处理数据集时出错: {str(e)}")
        raise


def main():
    """主函数,处理所有数据集
    
    按顺序处理四个不同的数据集:
    1. 时分复用 4s 数据集
    2. 时分复用 20s 数据集
    3. 非时分复用 4s 数据集 
    4. 非时分复用 20s 数据集
    """
    # 获取项目根目录的绝对路径
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    print("\n" + "="*50)
    print("开始处理时分复用 4s 数据集...")
    print("="*50)
    process_dataset(
        data_path=os.path.join(project_root, "Datasets", "Processed", "20s", "20_per_1_time", "4s.csv"),
        result_dir=os.path.join(project_root, "Results", '20s', "Time-division Multiplexing", "4s")
    )

    print("\n" + "="*50)
    print("开始处理时分复用 20s 数据集...")
    print("="*50)
    process_dataset(
        data_path=os.path.join(project_root, "Datasets", "Processed", "20s", "20_per_1_time", "20s.csv"),
        result_dir=os.path.join(project_root, "Results", '20s', "Time-division Multiplexing", "20s")
    )

    print("\n" + "="*50)
    print("开始处理非时分复用 4s 数据集...")
    print("="*50)
    process_dataset(
        data_path=os.path.join(project_root, "Datasets", "Processed", "20s", "4_per_5_times", "4s.csv"),
        result_dir=os.path.join(project_root, "Results", '20s', "Non Time-division Multiplexing", "4s")
    )
    
    print("\n" + "="*50)
    print("开始处理非时分复用 20s 数据集...")
    print("="*50)
    process_dataset(
        data_path=os.path.join(project_root, "Datasets", "Processed", "20s", "4_per_5_times", "20s.csv"),
        result_dir=os.path.join(project_root, "Results", '20s', "Non Time-division Multiplexing", "20s")
    )


if __name__ == "__main__":
    main()
