# 第 4 回｜ROS 2 包、发布与订阅

课程主仓库已收集到 [physicalai_pubsub](physicalai_pubsub/README.md)。先读 Mac 本地：`pai_code_part2_roboops/04_ros2_pubsub/physicalai_pubsub/README.ja.md`，再按以下入口读代码：

中文说明、翻译与代码可同步；日语原版教学资料及课件截图仅保留在 Mac 本地。

| 内容 | 本地入口 |
|---|---|
| 包依赖与元数据 | [package.xml](physicalai_pubsub/package.xml) |
| Python 节点入口注册 | [setup.py](physicalai_pubsub/setup.py) |
| 状态订阅 | [state_subscriber.py](physicalai_pubsub/physicalai_pubsub/state_subscriber.py) |
| 轨迹／动作发布 | [action_publisher.py](physicalai_pubsub/physicalai_pubsub/action_publisher.py) |

来源是 11.pdf（2026）· PDF 第 38、44 页；12.pdf（2025）· PDF 第 37、43 页也引用同一个仓库。此次保存的是上游固定 commit，并不是声称找到一份另外的“2025 历史代码”。版本见 [sources.lock.json](../sources.lock.json)。

运行依赖 ROS 2 Humble、课程 Gazebo/CRANE+ 环境、构建工具及已加载的工作空间。共享的 [环境源码](../shared/ros2_desktop_environment/README.md) 已另行归档。课程构建时把本包放入 ROS 工作空间 `src/`，按上游 README 使用 rosdep、colcon、source 和 `ros2 run`；本地归档目录本身不会自动变成已经构建好的 ROS 工作空间。

2026 课件先进入 `~/pai_ws/src` 再 clone；旧版在工作空间根目录 clone，后续 `rosdep --from-paths src` 会与之错位，应采用新版目录关系。这里仅记录，不执行构建或机械臂操作。

知识说明见 [第 11 章](../../notes_zh_sumed_up/11_ros2_packages.md)，测验见 Mac 本地：`homework/11.ipynb`。
