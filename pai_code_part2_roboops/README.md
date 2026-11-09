# Physical AI 应用篇 1｜代码与演习导航

按课程第 **1–6 回**归档。这里同时收集原有分发材料、课件中的课程仓库和第 5 回共享 Drive 的补充资料；不再用 notebook 数量判断课程是否齐全。

中文导航、讲解与代码可同步；日语原版教学资料及课件截图仅保留在 Mac 本地。

## 按回次开始

| 回次 | 主题与入口 | 本地内容 | 对应资料 |
|---|---|---|---|
| 01 | [RoboOps 概览](01_robops_intro/README.md) | 概念导读与自学入口；课件未给独立课堂代码 | Mac 本地：`pdfs/8.pdf`、Mac 本地：`homework/8.ipynb`、[中文讲义](../notes_zh_sumed_up/08_robops_intro.md) |
| 02 | [PushT RoboOps 实践](02_robops_workshop/GUIDE_ZH.md) | 原 `1/` 完整项目：notebook、Python 脚本、测试、Docker、CI | 无对应 PDF；Mac 本地：`homework/9.ipynb`、[中文讲义](../notes_zh_sumed_up/09_robops_practice.md) |
| 03 | [系统与设备实验](03_systems_devices/README.md) | 原有学生版与解答版 notebook | Mac 本地：`pdfs/10.pdf`、Mac 本地：`homework/10.ipynb`、[中文讲义](../notes_zh_sumed_up/10_systems_devices.md) |
| 04 | [ROS 2 发布／订阅](04_ros2_pubsub/README.md) | 新收集课程仓库 `physicalai_pubsub` | Mac 本地：`pdfs/11.pdf`、Mac 本地：`pdfs/12.pdf`、Mac 本地：`homework/11.ipynb`、[中文讲义](../notes_zh_sumed_up/11_ros2_packages.md) |
| 05 | [采集、转换、学习与部署](05_ros2_lerobot/README.md) | 遥操作、ACT 训练、固定版本 LeRobot、SmolVLA ROS 2 项目、额外 notebooks | Mac 本地：`pdfs/13.pdf`、Mac 本地：`homework/12.ipynb`、[中文讲义](../notes_zh_sumed_up/12_ros_data_lerobot.md) |
| 06 | [Dora 与开源贡献](06_open_source/README.md) | 原有 Dora notebook＋新收集的课堂贡献练习仓库 | Mac 本地：`pdfs/14.pdf`、Mac 本地：`homework/13.ipynb`、[中文讲义](../notes_zh_sumed_up/13_open_source_robotics.md) |

**推荐顺序**：先读各回中文入口，再打开对应 notebook 或上游 README。第 5 回先做主线 ACT 的代码阅读，再选择 SmolVLA、LIBERO 或 G1 扩展；它们不是必须串行执行的一份大程序。

## 目录结构

```text
pai_code_part2_roboops/
├── README.md
├── SOURCES.md                  # 课件页码、来源、已收集／尚缺／只保留入口
├── sources.lock.json           # 仓库 commit、下载哈希、原文件迁移映射
├── 01_robops_intro/
├── 02_robops_workshop/          # 原 1/；完整项目与 CI 放回同一项目根目录
├── 03_systems_devices/notebooks/
├── 04_ros2_pubsub/physicalai_pubsub/
├── 05_ros2_lerobot/
│   ├── physicalai_teleop/
│   ├── pai_training/
│   │   └── lerobot/             # pai_training 原 gitlink 指定的版本
│   └── optional/
│       ├── course_drive/        # 讲师共享的两个独立 notebook
│       ├── smolvla_ros2/        # 讲师共享 ZIP 的解压项目
│       ├── original_archives/   # 共享 ZIP 原件
│       └── upstream_notebooks/  # HF 的 ACT、SmolVLA 示例与 LICENSE
├── 06_open_source/
│   ├── notebooks/
│   └── pai-2026-advance-oss-lecture/
└── shared/ros2_desktop_environment/
```

## 来源与版本

- 整理日期：2026-10-29。原有 4 个 notebook 和原项目文件按原字节保留，只调整了位置；原课件、习题、Part 1 和中文讲义未修改。
- GitHub 内容是固定 commit 的源码快照，不含 `.git` 历史；后续查更新请使用 [来源清单](SOURCES.md) 中的上游入口，而不是在快照中直接执行 `git pull`。
- `pai_training` 的旧版 LeRobot 与 SmolVLA 扩展／上游新示例各自使用自己的配置，不能共用一个环境后假定依赖自动兼容。
- 共享 [ROS 2 桌面环境源码](shared/ros2_desktop_environment/README.md) 只保存构建／启动文件，没有拉取 Docker 镜像。
- 数据集、权重、仿真运行时及大型可选框架不随这次源码归档下载；入口见 SOURCES。

## 尚缺的课程原文件

课件 `13.pdf · PDF 第 57 页` 明确提及 **`5_ros2_2_lerobot_diffusion.ipynb`**，但没有直接文件链接。本次核对了课件所链共享目录及可访问的精确搜索，未找到该原文件。已有 Diffusion Policy 框架与模型链接不能替代这个课程 notebook；以后取得原件时，应放入第 05 回，补更新来源记录。

## 操作边界

本次仅下载、移动、解压和静态核对源码，**没有执行 notebook、安装依赖、构建镜像、启动 ROS／服务、训练模型或提交作业／PR**。上游 README 中的命令保留原样；需要运行时先按各回说明选择 Colab、容器或宿主环境，并修改示例路径、账户占位符与设备配置。
