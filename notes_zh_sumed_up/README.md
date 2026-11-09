# 具身智能讲座｜中文知识资料

讲义按知识联系归纳技术内容，合并连续与重复知识，保留源 PDF 文件名及页码范围，便于回查。每道习题后紧接参考答案与全部选项的详细解析；答案依据题干、课件及原理推导，不冒充官方答案。

中文讲义、中文习题与推导答案、翻译及代码可同步；日语原版教学资料和课件截图仅保留在 Mac 本地。

## 章节与原始资料

| 章 | 中文主题 | 中文讲义 | 源课件 | 源习题 |
|---|---|---|---|---|
| 01 | Physical AI、经典机器人与学习型策略 | [01_physical_ai_robotics.md](01_physical_ai_robotics.md) | Mac 本地：`pdfs/1.pdf` | Mac 本地：`homework/1.ipynb` |
| 02 | 机器人构型、运动学与闭环控制 | [02_robotics_basics.md](02_robotics_basics.md) | Mac 本地：`pdfs/2.pdf` | Mac 本地：`homework/2.ipynb` |
| 03 | 模仿学习、动作分布、扩散与流模型 | [03_imitation_learning.md](03_imitation_learning.md) | Mac 本地：`pdfs/3.pdf` | Mac 本地：`homework/3.ipynb` |
| 04 | 强化学习、仿真与策略微调 | [04_reinforcement_learning.md](04_reinforcement_learning.md) | Mac 本地：`pdfs/4.pdf` | Mac 本地：`homework/4.ipynb` |
| 05 | 架构、规模扩展与世界模型 | [05_scaling_architectures.md](05_scaling_architectures.md) | Mac 本地：`pdfs/5.pdf` | Mac 本地：`homework/5.ipynb` |
| 06 | 真实世界数据采集与整理 | [06_real_world_data.md](06_real_world_data.md) | Mac 本地：`pdfs/6.pdf` | Mac 本地：`homework/6.ipynb` |
| 07 | 策略部署与系统运行 | [07_policy_deployment.md](07_policy_deployment.md) | Mac 本地：`pdfs/7_1.pdf`、`pdfs/7_2.pdf` | Mac 本地：`homework/7.ipynb` |
| 08 | 机器人系统工程、MLOps 与 RoboOps | [08_robops_intro.md](08_robops_intro.md) | Mac 本地：`pdfs/8.pdf` | Mac 本地：`homework/8.ipynb` |
| 09 | 可复现环境、数据验证与策略评估 | [09_robops_practice.md](09_robops_practice.md) | 无对应 PDF；依据习题拓展 | Mac 本地：`homework/9.ipynb` |
| 10 | 内存、通信、虚拟化与设备管理 | [10_systems_devices.md](10_systems_devices.md) | Mac 本地：`pdfs/10.pdf` | Mac 本地：`homework/10.ipynb` |
| 11 | 软件包与 ROS 2 通信 | [11_ros2_packages.md](11_ros2_packages.md) | Mac 本地：`pdfs/11.pdf`、`pdfs/12.pdf`（11 为 2026 主版，12 为 2025 旧版） | Mac 本地：`homework/11.ipynb` |
| 12 | ROS 数据采集、rosbag2 与 LeRobot | [12_ros_data_lerobot.md](12_ros_data_lerobot.md) | Mac 本地：`pdfs/13.pdf` | Mac 本地：`homework/12.ipynb` |
| 13 | OSS、OSHW、Dora 与开源贡献 | [13_open_source_robotics.md](13_open_source_robotics.md) | Mac 本地：`pdfs/14.pdf` | Mac 本地：`homework/13.ipynb` |

## 阅读顺序与标记

建议按 01–13 阅读：01–02 建立机器人系统与控制基础；03–05 理解学习方法、模型架构和规模扩展；06–07 串联数据与部署；08–09 理解工程反馈和实验复现；10–12 进入系统、ROS 通信及学习数据管线；13 了解开源技术与协作。

- **补充解释**：为理解原理新增的推导、例子或前置知识。
- **依据习题拓展**：第 9 章没有对应课件，按习题主题编写独立讲义。
- **勘误／版本差异**：重要出入在对应知识点简短说明。
- **操作说明与代码块**：保留命令并解释前提、参数和预期结果，仅供学习。

第 7 章合并 `7_1.pdf` 与 `7_2.pdf`。第 11 章以 2026 版为主，在同章纳入 2025 旧版补充，标明重复位置和独有技术内容。

## 文件结构

```text
pai2026/
├── pdfs/                    # 原始课件，仅 Mac 本地
├── homework/                # 日文原始习题，仅 Mac 本地
└── notes_zh_sumed_up/      # 中文讲义、习题与答案，可同步
    ├── README.md
    ├── 01_physical_ai_robotics.md
    ├── ...                  # 每章一个知识文件，共 13 章
    └── assets/               # 原课件图，仅 Mac 本地
        ├── 01/              # 第 1 章原图
        ├── 02/              # 第 2 章原图
        └── ...
```

原始资料通过上表关联，不移动或重复存储。课件图仅在 Mac 本地保留，正文用本地路径提示；公式使用 LaTeX，流程可用 Mermaid，阅读器需支持相应语法。安装、启动、训练与机器人操作命令仅作为学习材料，整理过程没有执行这些课程操作。
