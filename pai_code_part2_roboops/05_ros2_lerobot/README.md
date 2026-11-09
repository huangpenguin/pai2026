# 第 5 回｜ROS 采集、模仿学习与 VLA 扩展

本回有“课堂主线”“讲师共享扩展”“上游示例”三种材料，分别保留自己的目录和环境，不把它们拼成一个可直接连续运行的脚本。

中文说明、翻译与代码可同步；日语原版教学资料及课件截图仅保留在 Mac 本地。

## 1. 课堂主线：CRANE+ → rosbag → ACT → Gazebo

来源：13.pdf · PDF 第 6、32、36–37 页。

1. [physicalai_teleop](physicalai_teleop/README.md)：遥操作与示范采集；核心代码 [teleop_keyboard.py](physicalai_teleop/physicalai_teleop/teleop_keyboard.py)。
2. [pai_training](pai_training/README.md)：数据转换、可视化、训练、推理与离线调试。

| 阶段 | 主线代码／配置 |
|---|---|
| rosbag 转 LeRobotDataset | [rosbag2lerobot.py](pai_training/scripts/rosbag2lerobot.py)、[conversion_config.yaml](pai_training/configs/conversion_config.yaml) |
| 特征与训练配置 | [crane_features.py](pai_training/configs/crane_features.py)、[train_config.yaml](pai_training/configs/train_config.yaml) |
| ACT 训练 | [train.py](pai_training/scripts/train.py) |
| 查看数据 | [visualize_dataset.py](pai_training/scripts/visualize_dataset.py) |
| 策略部署 | [infer.py](pai_training/scripts/infer.py) |
| 离线拟合检查 | [debug_policy.py](pai_training/scripts/debug_policy.py) |

课程用 `clone --recursive` 获取的 [LeRobot 子模块源码](pai_training/lerobot/README.md) 已补齐。其 gitlink 固定为 `768e36660d1408c71118a2760f831c037fbfa17d`，不是当前 LeRobot 主分支。上游部分测试数据与权重使用 Git LFS；此源码快照保留原指针，不下载这些大文件，也不据此宣称上游完整测试可离线运行。`pai_training` 原说明使用 **LeRobotDataset v2.1**；保持该项目的配置与依赖一起阅读，不将新版本命令直接混入旧版工程。

课程实际运行是在相应 ROS 2 Humble／Gazebo 环境中，使用工作空间构建遥操作包，并以 pai_training 的 Pixi 项目管理学习侧依赖。归档只包含源码，不代表依赖已安装、数据已采集或模型已训练。

## 2. 讲师共享的可选扩展

来源：13.pdf · PDF 第 57 页底部 Mac 本地课程共享目录：`pai_code_part2_roboops/05_ros2_lerobot/optional/`。本次实际读取到以下材料：

| 材料 | 本地入口 | 作用与环境 |
|---|---|---|
| ROS 2 × SmolVLA 完整项目 | [smolvla_ros2/README.md](optional/smolvla_ros2/README.md) | Franka FR3 推红色方块：采集、转换、微调、HTTP 推理、执行与评估；原说明分别提供容器、Colab GPU、Mac MPS 路径 |
| SmolVLA 微调 notebook | Mac 本地：`pai_code_part2_roboops/05_ros2_lerobot/optional/smolvla_ros2/vla_lecture/notebooks/smolvla_finetune.ipynb` | 来自上述共享项目，训练自己的数据 |
| SmolVLA 推理服务 notebook | Mac 本地：`pai_code_part2_roboops/05_ros2_lerobot/optional/smolvla_ros2/vla_lecture/notebooks/smolvla_server.ipynb` | 来自上述共享项目，Colab 推理服务路径 |
| LIBERO × SmolVLA 推理 | Mac 本地：`pai_code_part2_roboops/05_ros2_lerobot/optional/course_drive/libero-smolvla_inf_only.ipynb` | 独立 notebook，以内容为准，不与 FR3/CRANE+ 控制接口混用 |
| G1 强化学习 | Mac 本地：`pai_code_part2_roboops/05_ros2_lerobot/optional/course_drive/G1+RL.ipynb` | mjlab／PPO，原 notebook 标注 Colab T4 GPU；是讲师后附扩展，不意味着原课件表格当时已经附有此 notebook |

Mac 本地：`pai_code_part2_roboops/05_ros2_lerobot/optional/original_archives/smolvla_ros2.zip`也保留了。解压时仅略去 `.DS_Store` 与 `__MACOSX` 元数据，程序、notebook、配置与图片原样保留，shell 脚本的可执行权限也保留。

**版本边界**：SmolVLA/FR3 项目的说明使用 LeRobotDataset v3.0，与上面的旧版 ACT 项目不是相同版本。原项目中 `YOUR_ORG`、`YOUR_HF_USERNAME`、数据集 ID、模型路径等仍是需要读者按实际环境配置的占位符；没有在整理时替你登录、上传或启动服务。

## 3. 课件链接的上游示例

来源同为 13.pdf · PDF 第 57 页，但以下来自 **Hugging Face 上游**，不冒充课程讲师原版：

- [training-act.ipynb](optional/upstream_notebooks/training-act.ipynb)
- [training-smolvla.ipynb](optional/upstream_notebooks/training-smolvla.ipynb)
- [上游许可证](optional/upstream_notebooks/LICENSE)

已固定下载时的 huggingface/notebooks commit，记录于 sources.lock。这两个小示例会自行获取 LeRobot／模型／数据；它们不是旧 pai_training 环境兼容性的验证结果。

## 4. 明确尚缺的一项

课件另提到 `5_ros2_2_lerobot_diffusion.ipynb`（Optional PushT），但名称没有直接下载链接。共享目录现有文件、精确 Drive 搜索及公开精确搜索均未找到该课程原文件，因此没有用另一个 notebook 冒名补齐。

可以继续阅读 [Diffusion Policy 原项目](https://github.com/real-stanford/diffusion_policy)及 [diffusion_pusht 模型](https://huggingface.co/lerobot/diffusion_pusht)，它们是方法／模型入口，不是上述课程 notebook。

π0.5、Isaac Lab、unitree_rl_lab、mjlab 等完整框架及模型权重未另行下载；来源与课件定位见 [SOURCES](../SOURCES.md)。

知识说明见 [第 12 章](../../notes_zh_sumed_up/12_ros_data_lerobot.md)，测验见 Mac 本地：`homework/12.ipynb`。
