#!/bin/bash

# 环境变量定义
readonly RESULT_PATH="/home/ubuntu20/Workspace/Datasets/Original/10s/20_per_1_time"  # 结果保存路径
readonly ELF_PATH_CONTAINER="/Datasets/malwares/Valid_ELF_20200405"  # 容器内ELF文件路径
readonly ELF_PATH_LOCAL="/home/ubuntu20/Workspace/Datasets/malwares/virus"  # 本地ELF文件路径
readonly PURE_ELF_PATH="/home/ubuntu20/Workspace/Datasets/malwares/pure_Valid_ELF_20200405"  # 纯净ELF文件路径
readonly BENIGN_PATH="/home/ubuntu20/Workspace/Datasets/Benign_Software.txt"  # 良性软件列表路径
readonly IMAGE_NAME="pure_ubuntu20"  # Docker镜像名称
readonly CONTAINER_NAME="base"  # Docker容器名称
# 定义需要收集的所有硬件性能计数器事件,包括分支指令、缓存访问、TLB等
readonly EVENTS="branch-instructions,branch-misses,bus-cycles,cache-misses,cache-references,cpu-cycles,instructions,ref-cycles,L1-dcache-load-misses,L1-dcache-loads,L1-dcache-stores,L1-icache-load-misses,LLC-loads,LLC-stores,branch-load-misses,dTLB-load-misses,dTLB-loads,dTLB-store-misses,dTLB-stores,iTLB-load-misses"

# 文件索引计数器,用于生成唯一的输出文件名
file_index=1

# 从纯净ELF文件目录获取所有恶意软件样本文件列表
mapfile -t elf_files < <(ls "$PURE_ELF_PATH")
log_msg "已获取ELF文件列表"

# 从文本文件中读取良性软件列表
benign_files=()
while IFS= read -r line || [[ -n "$line" ]]; do
    benign_files+=("$line")
done < "$BENIGN_PATH"
log_msg "已获取良性软件列表"

# 日志输出函数,输出带时间戳的日志信息
log_msg() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# 删除Docker容器的函数,停止并删除指定名称的容器
delete_container() {
    docker stop "$CONTAINER_NAME"
    docker rm "$CONTAINER_NAME"
    log_msg "已删除容器 ${CONTAINER_NAME}"
}

# 在Docker容器中执行文件并收集性能计数器数据的核心函数
get_data() {
    local interval_cmd="$1"  # 采样间隔参数,如 -I 100 表示每100ms采样一次
    local output_file="$2"   # 性能计数器数据的输出文件路径
    local exec_file="$3"     # 要在容器中执行的文件路径
    local duration_time="$4"  # 执行和采集数据的持续时间(秒)
    
    # 创建新的Docker容器,挂载本地恶意软件目录到容器内
    docker run -d --name "$CONTAINER_NAME" -v "${ELF_PATH_LOCAL}:${ELF_PATH_CONTAINER}" "$IMAGE_NAME"
    log_msg "已创建容器 ${CONTAINER_NAME}"
    
    # 获取新创建容器的ID,用于perf命令中的容器标识
    local container_id
    container_id=$(docker inspect --format '{{.Id}}' "$CONTAINER_NAME")
    log_msg "容器 ${CONTAINER_NAME} 的ID为 ${container_id}"
    
    # 构建perf命令的参数,为每个性能计数器事件添加容器ID前缀
    local perf_cmd
    local group_args
    group_args=$(printf ',docker/%s' "$container_id"{1..20})
    group_args=${group_args:1}  # 移除开头的逗号
    
    # 根据是否指定采样间隔构建完整的perf命令
    if [[ -n "$interval_cmd" ]]; then
        perf_cmd="timeout --signal=SIGINT ${duration_time}s perf stat -e $EVENTS $interval_cmd -G $group_args -o $output_file"
    else
        perf_cmd="timeout --signal=SIGINT ${duration_time}s perf stat -e $EVENTS -G $group_args -o $output_file"
    fi
    
    log_msg "执行命令: $perf_cmd"
    eval "$perf_cmd &"  # 在后台执行perf命令,开始收集性能计数器数据
    local perf_pid=$!  # 记录perf命令的进程ID
    
    # 在容器中执行目标文件
    docker exec -d "$CONTAINER_NAME" "$exec_file"
    
    # 等待perf命令执行完成,即等待数据收集结束
    wait "$perf_pid"
    log_msg "等待 ${duration_time}秒"
    
    ((file_index++))
    
    # 清理:删除使用过的容器
    delete_container
}

# 运行恶意软件样本并收集数据的函数
run_ELF() {
    local interval_cmd="$1"   # 采样间隔参数
    local duration_time="$2"  # 执行持续时间
    local path="$3"          # 结果保存路径
    file_index=1
    
    # 遍历所有恶意软件样本
    for file in "${elf_files[@]}"; do
        # 将样本从纯净目录复制到本地目录
        cp "${PURE_ELF_PATH}/${file}" "${ELF_PATH_LOCAL}/${file}"
        log_msg "已将ELF文件 ${file} 从 ${PURE_ELF_PATH} 复制到 ${ELF_PATH_LOCAL}"
        log_msg "开始运行恶意软件 ${file}. 保存路径:${RESULT_PATH}/M_${file_index}.txt 间隔:${interval_cmd} 持续时间:${duration_time}"
        
        # 执行样本并收集数据
        get_data "${interval_cmd}" "${path}/M_${file_index}.txt" "${ELF_PATH_CONTAINER}/$file" "${duration_time}"
        
        # 清理:删除本地样本文件
        rm -f "${ELF_PATH_LOCAL}/${file}"
        log_msg "已从 ${ELF_PATH_LOCAL} 删除ELF文件 ${file}"
    done
}

# 运行良性软件样本并收集数据的函数
run_benign() {
    local interval_cmd="$1"   # 采样间隔参数
    local duration_time="$2"  # 执行持续时间
    local path="$3"          # 结果保存路径
    file_index=1
    
    # 遍历所有良性软件命令
    for file in "${benign_files[@]}"; do
        log_msg "开始运行良性软件 ${file}. 保存路径:${RESULT_PATH}/B_${file_index}.txt 间隔:${interval_cmd} 持续时间:${duration_time}"
        get_data "${interval_cmd}" "${path}/B_${file_index}.txt" "/bin/bash -c '${file}'" "${duration_time}"
    done
}

# 执行一次完整实验的函数,包括运行所有恶意和良性软件样本
run_experiment() {
    local name="$1"           # 实验名称,用于创建结果目录
    local interval_cmd="$2"   # 采样间隔参数
    local duration_time="$3"  # 执行持续时间
    local result_path="${RESULT_PATH}/${name}"
    
    # 创建保存结果的目录
    mkdir -p "$result_path"
    log_msg "创建目录 ${result_path}"
    
    # 依次运行恶意和良性软件样本
    run_ELF "$interval_cmd" "$duration_time" "$result_path"
    run_benign "$interval_cmd" "$duration_time" "$result_path"
}

# 主函数:执行四组不同参数的实验
main() {
    # 禁用NMI watchdog以避免干扰性能计数器
    echo 0 > /proc/sys/kernel/nmi_watchdog
    
    # 创建本地临时目录用于存放样本文件
    mkdir -p "$ELF_PATH_LOCAL"
    
    # 实验1: 10秒持续时间,不分段采样
    log_msg "开始第一组实验. 持续时间:10s 无间隔"
    run_experiment "10s" "" "10"
    log_msg "完成第一组实验"
    
    # 实验2: 2秒持续时间,重复5次
    log_msg "开始第二组实验. 持续时间:2s 无间隔 重复:5次"
    for i in {1..5}; do
        log_msg "第二组实验第${i}次"
        run_experiment "2s/2s_${i}" "" "2"
    done
    log_msg "完成第二组实验"
    
    # 实验3: 10秒持续时间,100ms间隔采样
    log_msg "开始第三组实验. 持续时间:10s 间隔:100ms"
    run_experiment "10s_100ms" "-I 100" "10"
    log_msg "完成第三组实验"
    
    # 实验4: 10秒持续时间,10ms间隔采样
    log_msg "开始第四组实验. 持续时间:10s 间隔:10ms"
    run_experiment "10s_10ms" "-I 10" "10"
    log_msg "完成第四组实验"
}

# 调用主函数
main
