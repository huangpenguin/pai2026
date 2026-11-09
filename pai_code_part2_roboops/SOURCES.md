# 代码来源与课件定位

整理日期：2026-10-29。页码均指 **PDF 实际页码**，可能与课件页脚印刷编号不同。课件正文和超链接注释都已核对，不能仅靠可见文字找到的链接判断是否提供教材。

中文说明、翻译与代码可同步；日语原版教学资料及课件截图仅保留在 Mac 本地。

## 六回材料状态

| 回次 | 课件证据 | 已归档的课堂材料 | 状态 |
|---|---|---|---|
| 01 | 8.pdf 全文；扩展入口第39、58页 | [导读](01_robops_intro/README.md) | 课件未给独立课堂代码，不人为补造原版 notebook |
| 02 | 10.pdf 第2、52、60、93、104页回顾 | [原PushT项目](02_robops_workshop/GUIDE_ZH.md) | 已有，原 `1/`，按回次重编 |
| 03 | 10.pdf 第4、87–93页 | [学生版和解答版](03_systems_devices/README.md) | 已有，两个版本原样保留 |
| 04 | 11.pdf（2026）第38、44页；12.pdf（2025）第37、43页 | [physicalai_pubsub](04_ros2_pubsub/README.md) | 新收集固定 commit；不是另行取得2025历史版本 |
| 05 | 13.pdf 第6、32、36–37页 | [遥操作与ACT主线](05_ros2_lerobot/README.md) | 新收集2个课程仓库及指定的LeRobot子模块 |
| 05扩展 | 13.pdf 第57页 | [共享Drive项目和notebook](05_ros2_lerobot/README.md#2-讲师共享的可选扩展)、[HF上游示例](05_ros2_lerobot/optional/upstream_notebooks/) | 均已实际下载；讲师材料与上游示例分开 |
| 06 | 14.pdf 第17、20、48页 | [Dora notebook与贡献练习](06_open_source/README.md) | notebook原本已有，另补课程仓库 |

原课件的第3回与第6回独立 notebook 都没有直接下载链接，但本地已有相符原件，因此它们不是当前缺件。

**尚缺的原版**：13.pdf 第57页提到 `5_ros2_2_lerobot_diffusion.ipynb`，没有直链；课件共享目录列举、精确Drive检索和公开精确检索均未找到。暂不将Diffusion Policy框架或另一个notebook当作这份原件。

## 这次归档的 GitHub 源码

均通过上游公开仓库元数据获取默认分支 commit，再按该 commit 下载源码；未执行项目脚本，不含 `.git` 历史。完整SHA和归档哈希在 [sources.lock.json](sources.lock.json)。

| 来源 | 本地位置 | 固定 commit | 上游提交日期 |
|---|---|---|---|
| [matsuolab/physicalai_pubsub](https://github.com/matsuolab/physicalai_pubsub) | [04_ros2_pubsub/physicalai_pubsub](04_ros2_pubsub/physicalai_pubsub/) | `746761b81b8f` | 2025-05-24T08:24:24Z |
| [matsuolab/physicalai_teleop](https://github.com/matsuolab/physicalai_teleop) | [05_ros2_lerobot/physicalai_teleop](05_ros2_lerobot/physicalai_teleop/) | `0ef2a00fd6d7` | 2025-06-09T16:24:21Z |
| [matsuolab/pai_training](https://github.com/matsuolab/pai_training) | [05_ros2_lerobot/pai_training](05_ros2_lerobot/pai_training/) | `b4d6b5459066` | 2025-06-06T18:07:39Z |
| [matsuolab/pai-2026-advance-oss-lecture](https://github.com/matsuolab/pai-2026-advance-oss-lecture) | [06_open_source/pai-2026-advance-oss-lecture](06_open_source/pai-2026-advance-oss-lecture/) | `15056919ab43` | 2026-10-13T09:15:16Z |
| [AI-Robot-Book-Humble/docker-ros2-desktop-ai-robot-book-humble](https://github.com/AI-Robot-Book-Humble/docker-ros2-desktop-ai-robot-book-humble) | [shared/ros2_desktop_environment/docker-ros2-desktop-ai-robot-book-humble](shared/ros2_desktop_environment/docker-ros2-desktop-ai-robot-book-humble/) | `d107b8162288` | 2025-02-09T10:54:36Z |

`pai_training` 的 `.gitmodules` 指向 huggingface/lerobot，而Git树中真正的gitlink固定为 `768e36660d1408c71118a2760f831c037fbfa17d`。已将该版本源码放在 [pai_training/lerobot](05_ros2_lerobot/pai_training/lerobot/)，不是只留一个空子目录，也没有将最新版LeRobot替换进去。

课件引用的两个HF notebook另按下载时的固定commit取得，放在 [upstream_notebooks](05_ros2_lerobot/optional/upstream_notebooks/)，并保留对应LICENSE。不能据此把当前示例视作旧ACT项目的兼容版本。

## 第5回共享Drive：实际找回的文件

入口是课件13.pdf第57页底部“共有ドライブ”的 Mac 本地课程共享目录：`pai_code_part2_roboops/05_ros2_lerobot/optional/`。本次通过Google Drive工具列出目录和子目录并获取原始文件：

| Drive原文件 | 本地归档 | 来源修改时间 |
|---|---|---|
| Mac 本地：`pai_code_part2_roboops/05_ros2_lerobot/optional/course_drive/G1+RL.ipynb` | Mac 本地：`pai_code_part2_roboops/05_ros2_lerobot/optional/course_drive/G1+RL.ipynb` | 2026-10-01T12:26:00.366Z |
| Mac 本地：`pai_code_part2_roboops/05_ros2_lerobot/optional/course_drive/libero-smolvla_inf_only.ipynb` | Mac 本地：`pai_code_part2_roboops/05_ros2_lerobot/optional/course_drive/libero-smolvla_inf_only.ipynb` | 2026-09-28T12:45:19.319Z |
| Mac 本地：`pai_code_part2_roboops/05_ros2_lerobot/optional/original_archives/smolvla_ros2.zip` | Mac 本地：`pai_code_part2_roboops/05_ros2_lerobot/optional/original_archives/smolvla_ros2.zip` | 2026-09-28T14:28:47.487Z |

`smolvla_ros2.zip` 来自子文件夹“第五回（smolvla ver）”。原ZIP与[解压项目](05_ros2_lerobot/optional/smolvla_ros2/)均保留；解压只略去Finder元数据。解压项目含ROS2包、转换代码、Mac推理服务器、Colab微调与推理notebook。`G1+RL.ipynb` 是共享目录中的后附材料；原PDF表格当时对G1写“无notebook”，两种来源的状态分开记录。

## 课件里的其他入口与参考资料

下表来自课件实际链接或明确提及的入口，**不表示每个链接的当前功能都已运行验证**。表中环境源码和课程指定的 LeRobot 版本已在前文归档；其余大型框架、硬件设计、模型权重和数据集仅保留入口。它们不是另外几回遗漏的课堂 notebook。

| 回次 | PDF定位 | 项目／入口 | 用途 |
|---|---|---|---|
| 1 | 8.pdf 第39页 | [DENSO ROS driver](https://github.com/DENSORobot/denso_robot_ros) | 厂家 ROS 驱动示例，不是课堂 clone 任务。 |
| 1 | 8.pdf 第58页 | [Robot System Quest](https://mertcookimg.github.io/robot-system-quest/) | 浏览器自学 ROS 教材，不是 PushT 课程仓库。 |
| 3 | 10.pdf 第25、61、98页 | [AiroPi](https://github.com/airoa-org/airopi-share) | 参考实现或架构案例，不是课件指定下载执行的课程项目。 |
| 3 | 10.pdf 第7、79、98页 | [yubi-core](https://github.com/airoa-org/yubi-core) | 参考实现或架构案例，不是课件指定下载执行的课程项目。 |
| 3 | 10.pdf 第105页 | [RVL/PNG codec reference](https://github.com/ros-perception/image_transport_plugins/blob/noetic-devel/compressed_depth_image_transport/src/codec.cpp) | 参考实现或架构案例，不是课件指定下载执行的课程项目。 |
| 3 | 10.pdf 第101页 | [Latency Numbers Every Programmer Should Know](https://gist.github.com/jboner/2841832) | 参考实现或架构案例，不是课件指定下载执行的课程项目。 |
| 4 | 11.pdf 第38页 | Mac 本地：`pai_code_part2_roboops/04_ros2_pubsub/physicalai_pubsub/README.ja.md` | README.md显示文字的实际注释URL。 |
| 5 | 13.pdf 第6页 | [ROS演习环境](https://github.com/AI-Robot-Book-Humble/docker-ros2-desktop-ai-robot-book-humble) | 课程环境源码参考，勿与课程练习项目混同。 |
| 5 | 13.pdf 第6页 | [上游VNC环境](https://github.com/Tiryoh/docker-ros2-desktop-vnc) | 课程环境源码参考，勿与课程练习项目混同。 |
| 5 | 13.pdf 第6、31、32页 | [LeRobot](https://github.com/huggingface/lerobot) | 课堂实际依赖，由pai_training子模块版本确定，而非任意最新main。 |
| 5 | 13.pdf 第57页 | [Diffusion Policy](https://github.com/real-stanford/diffusion_policy) | 可选扩展框架；不是本次ROS2主线课程仓库。 |
| 5 | 13.pdf 第57页 | [OpenPI](https://github.com/Physical-Intelligence/openpi) | 可选扩展框架；不是本次ROS2主线课程仓库。 |
| 5 | 13.pdf 第57页 | [Isaac Lab](https://github.com/isaac-sim/IsaacLab) | 可选扩展框架；不是本次ROS2主线课程仓库。 |
| 5 | 13.pdf 第57页 | [Unitree RL Lab](https://github.com/unitreerobotics/unitree_rl_lab) | 可选扩展框架；不是本次ROS2主线课程仓库。 |
| 5 | 13.pdf 第57页 | [mjlab](https://github.com/mujocolab/mjlab) | 可选扩展框架；不是本次ROS2主线课程仓库。 |
| 5 | 13.pdf 第18页 | [CRANE+ ROS wrapper](https://github.com/rt-net/crane_plus) | 硬件ROS接口示例。 |
| 5 | 13.pdf 第18页 | [RealSense ROS wrapper](https://github.com/IntelRealSense/realsense-ros) | 硬件ROS接口示例。 |
| 6 | 14.pdf 第24、37页 | [LeRobot PR #987](https://github.com/huggingface/lerobot/pull/987) | 课堂阅读贡献案例；第37页特别要求读第三个PR的往来。 |
| 6 | 14.pdf 第24、37页 | [LeRobot PR #3410](https://github.com/huggingface/lerobot/pull/3410) | 课堂阅读贡献案例；第37页特别要求读第三个PR的往来。 |
| 6 | 14.pdf 第24、37页 | [LeRobot PR #3656](https://github.com/huggingface/lerobot/pull/3656) | 课堂阅读贡献案例；第37页特别要求读第三个PR的往来。 |
| 6 | 14.pdf 第15、16、17、51页 | [Dora](https://github.com/dora-rs/dora) | 框架或生态案例；作为扩展阅读入口，不当作另一份课堂代码归档。 |
| 6 | 14.pdf 第22、23、24、51页 | [LeRobot](https://github.com/huggingface/lerobot) | 框架或生态案例；作为扩展阅读入口，不当作另一份课堂代码归档。 |
| 6 | 14.pdf 第18、51页 | [OpenArm](https://github.com/enactic/openarm) | 框架或生态案例；作为扩展阅读入口，不当作另一份课堂代码归档。 |
| 6 | 14.pdf 第51页 | [OpenArm data collection](https://github.com/enactic/dora-openarm-data-collection) | 框架或生态案例；作为扩展阅读入口，不当作另一份课堂代码归档。 |
| 6 | 14.pdf 第51页 | [MuJoCo](https://github.com/google-deepmind/mujoco) | 框架或生态案例；作为扩展阅读入口，不当作另一份课堂代码归档。 |
| 6 | 14.pdf 第25、51页 | [mjlab](https://github.com/mujocolab/mjlab) | 框架或生态案例；作为扩展阅读入口，不当作另一份课堂代码归档。 |
| 6 | 14.pdf 第26、27页 | [legged_gym](https://github.com/leggedrobotics/legged_gym) | 框架或生态案例；作为扩展阅读入口，不当作另一份课堂代码归档。 |
| 6 | 14.pdf 第31页 | [OpenVLA](https://github.com/openvla/openvla) | 框架或生态案例；作为扩展阅读入口，不当作另一份课堂代码归档。 |
| 6 | 14.pdf 第31、32、51页 | [OpenPI](https://github.com/Physical-Intelligence/openpi) | 框架或生态案例；作为扩展阅读入口，不当作另一份课堂代码归档。 |
| 6 | 14.pdf 第41、51页 | [SO-ARM100](https://github.com/TheRobotStudio/SO-ARM100) | 社区/开源硬件案例，非课程必需代码。 |
| 6 | 14.pdf 第41页 | [XLeRobot](https://github.com/Vector-Wangel/XLeRobot) | 社区/开源硬件案例，非课程必需代码。 |
| 6 | 14.pdf 第42、51页 | [mevius](https://github.com/haraduka/mevius) | 社区/开源硬件案例，非课程必需代码。 |
| 6 | 14.pdf 第43、51页 | [Open Duck Mini](https://github.com/apirrone/Open_Duck_Mini) | 社区/开源硬件案例，非课程必需代码。 |
| 6 | 14.pdf 第43、51页 | [yubi-hw](https://github.com/Toyota/yubi-hw) | 社区/开源硬件案例，非课程必需代码。 |
| 6 | 14.pdf 第51页 | [jsk-ros-pkg organization](https://github.com/jsk-ros-pkg) | 社区/开源硬件案例，非课程必需代码。 |

SmolVLA共享项目还依赖 [franka_description 的2.9.0版本](https://github.com/frankaemika/franka_description/tree/2.9.0)，这是其原README中的环境／模型资源依赖，未作为额外课程仓库归档。原README里的 `YOUR_ORG` 等是模板占位符，不是已验证存在的下载地址。

## 迁移关系与保留方式

| 原Part2路径 | 当前路径 |
|---|---|
| `1/` | `02_robops_workshop/` |
| 外层 `.github/`、`.dockerignore` | `02_robops_workshop/` 内同名路径 |
| 第3回学生版、答案版 | `03_systems_devices/notebooks/`，原文件名不变 |
| 第6回notebook | `06_open_source/notebooks/`，原文件名不变 |

原Part2的 `.gitignore` 保留，并向第2回项目复制同一内容。原项目README、源码、配置、notebook内容与执行输出未改写。上游仓库及共享资料的许可证文件按原样保存；未附明确许可证的来源也没有自行补造授权。

本次未执行课程安装、镜像构建、服务启动、训练、数据上传或PR提交。归档可供本地阅读，不代表各硬件／软件环境已运行验证。
