# Notebook 中文版

本目录包含 `ntbk_jp/` 中 8 个日文 notebook 的简体中文版。中文版在翻译说明文字的基础上，对 VLA 数据流、action chunking、FK/IK、GMM 与 Diffusion Policy、MDP/PPO、ROS bag 时间同步、LeRobotDataset、kNN 标签审计、LoRA、shape 契约和 rollout 评估补充了教学性解释。

## 文件映射与建议顺序

| 日文源文件 | 中文文件 | 主题 |
|---|---|---|
| `第1回 演習資料.ipynb` | `第1讲 练习资料.ipynb` | VLA、SmolVLA、LIBERO 与 action chunk 推理 |
| `第2回 演習資料.ipynb` | `第2讲 练习资料.ipynb` | 坐标系、FK/IK、末端执行器、site/body 与四元数 |
| `第3回 演習資料.ipynb` | `第3讲 练习资料.ipynb` | BC、多峰性、GMM、score、扩散过程与 Diffusion Policy |
| `第4回 演習資料.ipynb` | `第4讲 练习资料.ipynb` | MDP、奖励、域随机化、PPO、并行环境与曲线诊断 |
| `第6回 演習資料 完成版.ipynb` | `第6讲 练习资料（完整版）.ipynb` | ROS bag 同步、LeRobotDataset、数据清洗与标签审计（参考实现） |
| `第6回 演習資料 穴埋め版.ipynb` | `第6讲 练习资料（填空版）.ipynb` | 同上，保留原始 5 个 TODO 的练习版 |
| `最終課題(Basic).ipynb` | `最终课题（基础版）.ipynb` | PyTorch 简化 SmolVLA、Flow Matching、训练与提交 |
| `最終課題(Advanced).ipynb` | `最终课题（进阶版）.ipynb` | LeRobot、LoRA、权重合并、baseline 与跨 suite 评估 |

建议学习顺序为：第 1 讲 → 第 2 讲 → 第 3 讲 → 第 4 讲 → 第 6 讲 → 最终课题基础版 → 最终课题进阶版。第 6 讲可先看完整版，再用填空版练习；最终课题进阶版依赖基础版产生的 Drive 缓存和模型理解。

## 运行负载与 GPU 要求

| 中文 notebook | 预计负载 | Colab GPU |
|---|---|---|
| 第 1 讲 | 下载 LeRobot、模型和数据；包含 LIBERO rollout | T4 或更高，约 16GB 显存 |
| 第 2 讲 | MuJoCo Panda 渲染、FK/IK 和视频 | CPU 可运行；Colab EGL 渲染更稳妥 |
| 第 3 讲 | robosuite/robomimic 数据下载、图像重渲染和训练 | GPU 强烈建议；完整数据与训练耗时较长 |
| 第 4 讲 | MuJoCo Warp、4096/2048 并行环境和 PPO | 必须 NVIDIA GPU；T4 可运行短演示，平滑步态需更久训练 |
| 第 6 讲 | 约 65MB 数据准备；可选 checkpoint、rollout 和小型训练 | Step 1–5 以 CPU 为主；Step 6 需要 T4 GPU |
| 最终课题基础版 | 约 6GB assets、VLM 下载、从零训练与 rollout | 必须 T4 或更高；不把完整训练作为本轮验收 |
| 最终课题进阶版 | 预训练模型、LoRA 训练、合并和 4-suite 评估 | 必须 T4 或更高；网络/Drive/大模型开销高 |

第 4 讲继续标记为 NVIDIA GPU 训练课程：MuJoCo Warp 使用 CUDA，训练阶段需要 NVIDIA GPU；macOS 仅适合评估。参见 [MJLab 官方 README](https://github.com/mujocolab/mjlab/blob/main/README.md)。

## 统一术语

| 中文 | English / 缩写 | 说明 |
|---|---|---|
| 视觉-语言-动作 | Vision-Language-Action (VLA) | 图像、语言与机器人动作的联合策略 |
| 视觉-语言模型 | Vision-Language Model (VLM) | 为 Action head 提供条件表示 |
| 行为克隆 | Behavioral Cloning (BC) | 从专家示范监督学习动作 |
| 动作块 | action chunk | 一次预测多个未来时间步的动作 |
| 末端执行器 | end effector (EE) | 机械臂末端的位姿与工具 |
| 正向/逆向运动学 | forward/inverse kinematics (FK/IK) | 关节角与末端位姿之间的映射 |
| 高斯混合模型 | Gaussian Mixture Model (GMM) | 用多个高斯成分表示动作分布 |
| 得分函数 | score function | 对数密度关于输入的梯度 |
| 马尔可夫决策过程 | Markov Decision Process (MDP) | RL 的观测、动作、奖励和转移定义 |
| 近端策略优化 | Proximal Policy Optimization (PPO) | 带 clipping 的策略梯度算法 |
| 低秩适配 | Low-Rank Adaptation (LoRA) | 只训练低秩权重差分 |
| 领域随机化 | domain randomization (DR) | 注入仿真随机性以提高 sim2real 鲁棒性 |

## 中文版扩写声明

中文版的目标不只是逐句替换文字，还在不改变程序契约的前提下补充必要的教学解释。扩写仅进入现有 Markdown cell（没有新增代码 cell）；原有输出、图表、视频、widget、execution count、cell metadata 和 Colab metadata 均保持不变。所有模型 ID、数据集 ID、URL、路径、环境变量、CLI 参数、配置键、正则、JSON 键、英文任务指令与变量名都按程序契约保留。第 6 讲完整版与填空版分别从各自源文件生成，不互相覆盖，因此仍保留原始差异。

## 验证矩阵

| 检查项 | 本轮状态 | 说明 |
|---|---|---|
| 源文件 SHA-256 | 已记录并在生成时强校验 | 8 个 `ntbk_jp/*.ipynb` 的摘要写入生成脚本；源文件未修改 |
| JSON 解析与 `nbformat.validate` | 已静态执行 | 当前环境未安装 `nbformat`，使用等价的 JSON + nbformat-v4 结构兜底检查；安装后可直接重跑脚本调用 `nbformat.validate` |
| cell ID / 类型 / metadata / outputs / attachments / execution count | 已静态执行 | 按 cell ID 与对应日文源文件逐项比较 |
| Python 语法与代码 token | 已静态执行 | 去除 IPython magic 和 shell 行后解析；注释、docstring、白名单 reader-facing 字符串除外，其余 token 保持一致 |
| 日文残留报告 | 已静态执行 | 中文 Markdown 与代码注释/字符串无未翻译日文；源 outputs 保留的历史文本单独计入允许范围 |
| 第 2 讲 CPU 完整运行 | 本轮未动态运行 | 依赖下载、MuJoCo 渲染和运行时环境未在本轮重跑 |
| 第 1 讲模型加载/单次推理 | 本轮未动态运行 | 需要 Colab GPU、网络和 Hugging Face 资源 |
| 第 3 讲安装、导入、玩具 BC/GMM/Diffusion | 本轮未动态运行 | 需要网络、GPU 和较长的训练/数据准备时间 |
| 第 4 讲 16 环境 smoke test | 本轮未动态运行 | 需要 NVIDIA GPU 与 CUDA/JIT；源 notebook 的既有说明未改写为本轮结果 |
| 第 6 讲数据准备与非 GPU 核心步骤 | 本轮未动态运行 | 需要发布数据与网络；填空版不执行依赖 TODO 答案的步骤 |
| 最终课题运行时检查/轻量初始化 | 本轮未动态运行 | 6GB assets、模型下载、Drive 和第三方资源未在本轮强制验证 |
| 8 本端到端运行 | 未宣称 | 重型 CUDA、网络、Drive 和第三方资源边界如上，不能表述为完整端到端实跑 |

本轮不创建 `pyproject.toml`、`uv.lock`、`.venv` 或本地 Jupyter kernel，不做 Apple MPS/本地路径适配，也不抽取 Python 主项目。
