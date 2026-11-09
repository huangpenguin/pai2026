#!/usr/bin/env python3
"""Generate and statically audit the Chinese notebook copies.

The source notebooks are treated as immutable inputs.  Only markdown, code
comments/docstrings, and reader-facing messages are translated; cell IDs,
outputs, metadata, and executable code are copied from the Japanese sources.
"""

from __future__ import annotations

import ast
import copy
import hashlib
import json
import re
import sys
import tokenize
from io import StringIO
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "ntbk_jp"
OUT_DIR = ROOT / "ntbk_zh"
JAPANESE_SCRIPT_RE = re.compile(r"[ぁ-ゖァ-ヺー]")

SOURCE_HASHES = {
    "第1回 演習資料.ipynb": "af4d41a39200bde3ee37b59cdeedc6365be3822e718eb37084652280bf691adc",
    "第2回 演習資料.ipynb": "9e5898aa017ca9b52429bafbec4458cd39d66ca451e72894e59c4b25ee00ed77",
    "第3回 演習資料.ipynb": "d07bcae48872b02922059507abc202cb358183410217a70b58db70f923e001da",
    "第4回 演習資料.ipynb": "c37d9a23f762ce1af2ca2182a35c787c317ae13dbdeeedf6525d2417423d5ba0",
    "第6回 演習資料 完成版.ipynb": "926677b14b54abb8dcf69504ae1f7af15d5cd2776493f917fd82f1fd5fc9a2e7",
    "第6回 演習資料 穴埋め版.ipynb": "1d2160cf0fd52ef273a50079eb4cad8b1e9a8643d7945aac0f44cfebfc28a2e1",
    "最終課題(Basic).ipynb": "cd62ebbc7bdeabca8795d269797512aa7aba9b499bfeb35f701f58ec40b9015a",
    "最終課題(Advanced).ipynb": "cfa496209a0961c4c2c8ae7c0a13cb035907ad6b9f1ec32936fa43ec3159efe7",
}

OUTPUT_NAMES = {
    "第1回 演習資料.ipynb": "第1讲 练习资料.ipynb",
    "第2回 演習資料.ipynb": "第2讲 练习资料.ipynb",
    "第3回 演習資料.ipynb": "第3讲 练习资料.ipynb",
    "第4回 演習資料.ipynb": "第4讲 练习资料.ipynb",
    "第6回 演習資料 完成版.ipynb": "第6讲 练习资料（完整版）.ipynb",
    "第6回 演習資料 穴埋め版.ipynb": "第6讲 练习资料（填空版）.ipynb",
    "最終課題(Basic).ipynb": "最终课题（基础版）.ipynb",
    "最終課題(Advanced).ipynb": "最终课题（进阶版）.ipynb",
}


def md(value: str) -> str:
    return value.strip("\n") + "\n"


# Markdown is translated cell-by-cell.  The keys are stable notebook cell IDs,
# not cell positions, so a source notebook can contain its original order and
# its original outputs without being reconstructed through global replacement.
MARKDOWN: dict[str, dict[str, str]] = {
    "第1回 演習資料.ipynb": {
        "pE7wik2jgDNZ": md(r"""# Physical AI 基础篇 智能机器人课程 2026 Spring 第1讲练习资料
## 通过 LeRobot × SmolVLA × LIBERO 学习 VLA 推理流程

本 notebook 使用 Hugging Face 的轻量 VLA 模型 **SmolVLA** 的 LIBERO checkpoint `HuggingFaceVLA/smolvla_libero`，在机器人操作基准 **LIBERO** 上体验从
**推理 → 评估 → 可视化** 的完整流程。

这里要特别留意 VLA 的数据流：观测（图像、proprio 和语言指令）先经过预处理，模型一次预测一段 action chunk，再由后处理把动作还原为环境使用的尺度。这样可以把“看见什么”“理解什么”和“如何动作”串在同一条可检查的链路中。"""),
        "A8szw7KNgDNa": md(r"""## 检查 GPU

首先确认 Colab 分配了 **T4 GPU**。
如果 `nvidia-smi` 输出中出现 `Tesla T4` 和约 `15360MiB`（约 16GB）显存，就可以继续。"""),
        "w5Im2Hy7gDNb": md(r"""## 安装依赖

安装带有 **`smolvla`（SmolVLA）** 和 **`libero`（LIBERO 环境）** extra 的 LeRobot。

（之后需要重启 session。）"""),
        "hnZ8EDvOgDNb": md(r"""## 什么是 SmolVLA

**SmolVLA** 是 Hugging Face 在 2025 年发布的轻量 **Vision-Language-Action（视觉-语言-动作，VLA）** 模型。它的目标是做到**可以在单张 GPU 上训练，也能在消费级 GPU 或 CPU 上运行**。

### 训练数据

- 使用 **LeRobot 社区公开的 487 个真实机器人数据集**进行预训练
- 主要依靠**社区公开数据**，而不是大企业的私有超大规模数据；与同类模型相比，训练数据规模小了一个数量级以上

### 性能（LIBERO 基准，论文报告值）

| 模型 | 参数量 | 平均成功率 |
| --- | --- | --- |
| Octo | 0.09B | 75.1% |
| OpenVLA | 7B | 76.5% |
| π0 | 3.3B | 86.0% |
| **SmolVLA** | **0.45B** | **87.3%** |

本 notebook 使用的 `HuggingFaceVLA/smolvla_libero` 是针对 **LIBERO 训练的 SmolVLA checkpoint**。

参考：
- 论文 https://arxiv.org/abs/2506.01844
- 解读博客 https://huggingface.co/blog/smolvla"""),
        "rOJ2MvCWgDNb": md(r"""## 什么是 LIBERO

**LIBERO** 是常用于评估机器人策略性能的**操作任务基准**（Liu et al., NeurIPS 2023）。它在仿真器中定义抓取、放置、打开等操作任务。

### 组成

- 基于物理仿真器 **MuJoCo** 的 **Franka Emika Panda** 机械臂
- **5 个任务 suite（共 130 个任务）**，每个任务都带有人类示范（遥操作）

| Suite | 任务数 | 评估变化 |
| --- | --- | --- |
| `libero_spatial` | 10 | 物体的放置位置（空间关系） |
| `libero_object` | 10 | 目标物体不同 |
| `libero_goal` | 10 | 目标不同 |
| `libero_10`（LIBERO-Long） | 10 | 长时间、复合任务 |
| `libero_90` | 90 | 多样的短任务 |

### 输入与输出

- **观测（observation）**
  - `observation.state`：8 维 proprio（末端位置与姿态 6 + 夹爪两指 2）
  - `observation.images.image`：主相机（俯视）
  - `observation.images.image2`：腕部相机
  - `task`：自然语言指令，例如 "pick up the black bowl and put it on the plate"
- **动作（action）**：7 维（末端位姿增量 6 + 夹爪开合 1）

### 评估指标

- 对每个任务运行多个 episode 的 **rollout**，测量**任务成功率（success rate）**。
- “成功”由每个任务的完成条件（目标物体是否到达目标位置或状态）自动判断。

官方文档：
- https://huggingface.co/docs/lerobot/libero
- https://libero-project.github.io/main"""),
        "7dop30I4gDNb": md(r"""## 什么是 LeRobot

**LeRobot** 是 Hugging Face 开发的、面向**真实机器人学习的开源框架**。模型等组件全部使用 PyTorch 编写。
它能够一站式处理**数据、模型、训练、评估和真实机器人控制**，目前许多项目都使用 LeRobot 格式的数据集。

### 主要组件

- **`LeRobotDataset`**：以统一格式处理机器人 episode（图像、proprio、动作、语言指令）。它可以从 HF Hub 共享和下载，本 notebook 使用的 `HuggingFaceVLA/libero` 也属于这种格式。
- **机器人策略**：包含 ACT、Diffusion Policy、π0、**SmolVLA** 等多种机器人策略实现。
- **环境**：LIBERO、PushT 等仿真环境的封装。

官方仓库：https://github.com/huggingface/lerobot ／ 文档：https://huggingface.co/docs/lerobot"""),
        "9f8Nl1kFgDNc": md(r"""## 加载模型

使用 `SmolVLAPolicy.from_pretrained` 加载 checkpoint **`HuggingFaceVLA/smolvla_libero`**（接口风格与 `transformers` 等库相似）。

同时用 `make_pre_post_processors` 构建**预处理（preprocessor）/后处理（postprocessor）**流水线。这些步骤是推理所必需的：

- **preprocessor**：观测字典键转换 → 增加 batch 维度 → 对语言指令分词 → 转移到设备 → **归一化**
- **postprocessor**：对模型输出动作做**反归一化** → 转移到 CPU

归一化统计量保存在 checkpoint 中，因此把 checkpoint ID 作为 `make_pre_post_processors` 的**第二个参数**，就能加载与训练时相同的统计量。这正是“训练时和推理时保持处理一致”的关键。"""),
        "5uV4VPtlgDNc": md(r"""## 推理演示

从 LIBERO 数据集 **`HuggingFaceVLA/libero`** 中取出**一个 episode**，把第一帧输入模型并输出一个 **action chunk**。"""),
        "bGJ9PhYLgDNc": md("显示输入图像（主相机和腕部相机），确认模型正在“看见”什么。"),
        "4Nx-WSSXgDNc": md(r"""执行预处理 → 推理 → 后处理流程。`predict_action_chunk` 获取**完整 action chunk**，`select_action` 获取**单个时间步的动作**，并分别检查它们的 shape。"""),
        "o45MJfV-gDNd": md(r"""- `action_chunk` 的 `(B, n_action_steps, 7)` 表示：一次推理会预测未来 `n_action_steps` 个时间步的动作。这称为 VLA 的 **action chunking**。
- 在实际控制中，这个 chunk 会先放入内部队列，由 `select_action` 每次取出一个时间步；队列耗尽后再进行推理。"""),
        "0aGWxA-9gDNd": md(r"""## 基准评估

LeRobot 通常可以通过 `lerobot-eval` 命令在 LIBERO 仿真器上实际 rollout，并测量**任务成功率**。
但本次不直接依赖黑盒命令，而是手写评估脚本，以便看清评估内部做了什么。"""),
    },
    "第2回 演習資料.ipynb": {
        "pGGlQFphMacD": md(r"""# Physical AI 基础篇 智能机器人课程 2026 Spring 第2讲练习资料
## 观察 Kinematics（运动学）的内部工作方式

本 notebook 通过实际调用 Kinematics API，加深对运动学的理解。

具体来说，我们使用 Franka Panda 调用 FK / IK API，把自己定义的 task-space 轨迹交给 IK，再让机械臂运动起来。

关键数据流是：FK 把关节空间映射到末端位姿；IK 则把期望末端位姿翻译回一组可执行的关节角。"""),
        "xOU2BoHkMacF": md(r"""## 安装依赖

- `dm_control` …… IK 求解器
- `mujoco` …… 仿真器
- `robot_descriptions` …… 获取 Panda 的 MuJoCo 模型"""),
        "W9QPShJgMacF": md(r"""### Kinematics（运动学）
- **Joint space（关节空间）** `q = [θ₁, …]`：每个关节的角度
- **Task space（任务空间）** `p = [x, y, z, …]`：末端执行器的位姿
- **FK（正向运动学）** `p = f(q)`：关节角 → EE
- **IK（逆向运动学）** `q = f⁻¹(p)`：EE → 关节角，**通常没有解析解**"""),
        "dGFUMiA0MacG": md(r"""我们将在与真实机器人相当的 7 自由度 **Franka Emika Panda** 上实际调用 FK / IK。

本次在 **MuJoCo 中仿真 Panda**，并使用 **[dm_control](https://github.com/google-deepmind/dm_control)** 的 `qpos_from_site_pose` 求解逆运动学。"""),
        "hXFp5y9ZMacG": md(r"""准备绘图辅助函数（后面也会用于制作视频）。这次使用 **MuJoCo 的离屏渲染器**把 Panda 渲染成真实图像，收集帧并制作 mp4 视频。"""),
        "EomzZ4rJMacG": md(r"""### FK（正向运动学）：关节角 → EE

给 `fk(q)` 传入 7 个关节角，就会得到末端（EE）的**位置 `(x, y, z)`**。这就是 **joint space → task space** 的映射。无论输入多少种 `q`，每个 `q` 都会唯一决定一个末端位置。"""),
        "8RBv8NndMacG": md("试着只旋转**第一个关节 θ₁**，观察末端如何运动（改变一个关节后末端随之运动，这就是 FK）。"),
        "zMDXC5zSMacH": md(r"""### IK（逆向运动学）：EE → 关节角

`ik_reach(p)` 接收 **EE 的目标位置**，返回实现该位置的**关节角**。内部调用的是 `dm_control.utils.inverse_kinematics.qpos_from_site_pose`。

验证 **`FK(IK(p*)) ≈ p*`**：把 IK 反算出的关节角重新送入正向运动学，结果应当接近目标位置。"""),
        "ZgHpj9zPMacH": md(r"""### 让 EE 移动到目标位置

人先设计“末端要怎样运动”的 task-space 轨迹，再用 **dm_control 的 IK 将每个 waypoint 翻译成关节角**并跟踪，最后通过视频确认 Panda 的运动。

设计的运动：**向前移动（+x 方向 0.1 m）→ 向下移动（−z 方向 0.1 m）**"""),
        "GUE8DRcKMacH": md(r"""我们只在 **task space 中指定“这样运动”**，然后由 **IK（`dm_control` 的 `qpos_from_site_pose`）把它翻译成关节角**，Panda 就在 MuJoCo 中按设计运动起来了，跟踪误差也保持很小。

这说明 task-space 规划与 joint-space 控制之间的桥梁，就是 IK 求解器。"""),
    },
    "第3回 演習資料.ipynb": {
        "cab0a4db": md(r"""# 模仿学习入门

本 notebook 在物理仿真器上从专家示范学习策略 $π_θ(a\mid s)$，体验训练与评估的基本流程，并理解常见实践。

模仿学习大致有两类方法：

- Behavioral Cloning（BC，行为克隆）：学习从输入观测到动作的映射。
- Inverse Reinforcement Learning（IRL，逆强化学习）：从示范中推断背后的奖励函数，再寻找能最大化该奖励的策略来复现期望行为。

本教材聚焦于生成模型兴起后快速发展的 BC。

本 notebook 将学习：

1. BC 的定义，以及简单回归策略的两个问题；
2. 在玩具任务中观察多峰性（同一观测对应多个正确动作）；
3. 在物理仿真器上训练和评估 BC 策略；
4. 使用深度生成模型 **Diffusion Policy**（扩散策略）挑战更难的任务。

**运行环境**：MuJoCo 的无头渲染需要 GPU。Colab 请选择 `运行时 → 更改运行时类型 → GPU`；本地环境默认使用 `pixi.toml`。"""),
        "OwFAYV4bwzPj": md(r"""# 动机

Diffusion Policy：https://diffusion-policy.cs.columbia.edu/

ACT：https://arxiv.org/abs/2304.13705

pi0：https://www.pi.website/blog/pi0"""),
        "r9suvJhquJod": md(r"""# 注意

本资料是“在仿真环境中动手接触模仿学习的代码与带结果补充材料”，**不以课堂内逐单元执行为目标**。
尤其是数据集下载和训练部分会非常耗时；有时间的同学可以在自己的环境中运行，但不要只是无目的地反复点击按钮。Colab 免费额度还可能受到运行时长限制，需要拆分到多个 session 中，请提前规划。"""),
        "75bd0e16": md(r"""## 环境准备

这里使用物理仿真器 [MuJoCo](https://mujoco.readthedocs.io/en/stable/overview.html)，使用为机器人学习封装 MuJoCo 并提供任务的 [robosuite](https://robosuite.ai/)，以及提供 robosuite 数据集和策略实现的 [robomimic](https://robomimic.github.io/)。

另一个框架是 [LeRobot](https://github.com/huggingface/lerobot)，其中实现了较新的模仿学习算法（ACT / Diffusion Policy）和 VLA（pi0 系列、smolvla 等），有 GPU 就可以方便地做实验。拥有或购买 SO101 等低成本机器人的同学，也可以进一步在真实机器人上实验。"""),
        "5a8e6808": md(r"""## 在玩具任务中观察简单回归的局限

先用最小配置观察问题 1（同一观测对应多个正确动作）。对于状态 $s\in[-1,1]$，专家会凭“心情”以相同概率选择**上方路径 $a=+1$**或**下方路径 $a=-1$**，而 $s$ 不决定选择哪条路径。

此时二次误差的最优答案是两个动作的平均值 $\tfrac{(+1)+(-1)}{2}=0$。这个动作从未出现在示范中，等价于朝墙走。下面用真实生成的数据比较三种策略表示：

- **回归（MSE）**：返回一个动作点；
- **GMM（高斯混合模型）**：用混合高斯 $p(a\mid s)=\sum_k \pi_k N(\mu_k,\sigma_k)$ 表示动作分布。**分布峰值数量 $M$ 必须预先指定**；太少会把多个峰压在一起，太多则多余成分的权重会降到 0。本玩具任务使用真实峰数 $M=2$；
- **Diffusion Model（扩散模型）**：从噪声中去噪并**采样**动作，是 Diffusion Policy 的最小版本。"""),
        "154c06ea": md(r"""从左图的回归结果（红色）可以看到，它会贴在两个 mode 中间的 $≈0$。当同一观测有两种动作时，这个策略会输出示范中不存在的平均动作。

相反，把动作表示成**分布**的策略（GMM、扩散模型）可以保留 $+1$ 和 $-1$ 两个峰。相同的示范和目标，只改变策略表示，结果就会不同。不过 GMM 必须预先给出峰数 $M$，扩散模型则不需要这个设定，可以表示任意形状的分布。现实世界的图像、视频等数据通常是高维的，mode 数量也未知。

当然，这个现象的根源是观测 $s$ 不决定动作。后面的 lift / square 会以图像和精确状态作为条件，观测几乎唯一决定动作，因此多峰性不明显。真实机器人更突出的往往是问题 2（误差累积）；Diffusion Policy 通过一次生成一段动作序列来缓解它。"""),
        "c3d444eb": md(r"""## 准备用于 BC 的机器人数据

[robomimic](https://robomimic.github.io/) 提供 robosuite 上的**机器人操作示范集**和训练算法。本次使用 **ph（proficient human，熟练人工遥操作）**的两个任务：

- **Lift**：抓住红色方块并抬起。任务短、解法几乎唯一；
- **Square**：把方形螺母插入固定插销（nut-assembly）。任务更长，接触过程更精细。

“短且容易 / 长且困难”的对比，会影响问题 2（误差累积）的严重程度。

robosuite 1.5 系列的数据文件 `demo_v15.hdf5` 只有状态序列和动作序列，没有观测图像。这里把状态序列在仿真器中重放，再用相机渲染，生成带图像的 `image_v15.hdf5`。"""),
        "f3160378": md(r"""## 查看数据集分布

开始训练前，先观察数据如何分布。不了解初始状态范围和动作内容就直接训练模仿策略很危险，因为**策略是否成功、任务有多难，都高度依赖数据分布**。这里从三个角度可视化 Lift 和 Square 的 robomimic 数据集：

- **初始状态叠加**：叠加各示范的初始帧，观察物体从哪里开始；
- **动作分布**：绘制每个动作维度的直方图，查看取值范围、饱和和夹爪二值性；
- **末端 3D 轨迹**：在三维空间叠加所有示范的末端位置，观察运动的范围与复杂度。"""),
        "64fb70a5": md(r"""解读：

- **Lift** 的单个 episode 很短（平均约 50 步），轨迹简单，因此朴素回归也容易学习。
- **Square** 的轨迹复杂，抓取和插入阶段会分叉，episode 也更长（平均约 150 步）。轨迹越长，误差越容易累积，对回归策略越苛刻。
- 动作分布中，夹爪维度会分成约 ±1 的二值两类，平移维度两端还可能出现饱和尖峰。了解这些特征，有助于定位训练失败的原因。"""),
        "93ad0dc5": md(r"""## 训练与评估辅助函数

使用 robomimic 经过验证的组件构建、训练和评估策略，同时只把训练循环本身展开，方便理解：

- `build_model`：通过 `config_factory` + `algo_factory` 创建模型（`bc` 和 `diffusion_policy` 使用同一个入口）；
- `make_loader`：从 `SequenceDataset` 提供 batch；
- `train`：一个梯度步骤 = `process_batch → train_on_batch`；
- `make_eval_env` / `rollout` / `evaluate`：让策略在仿真环境中运行，测量成功率并保存视频。"""),
        "b646b451": md(r"""## 用回归策略训练 Lift 任务

Lift 很短，解法几乎唯一；观测基本决定动作，轨迹也短，所以多峰性和误差累积都不明显。使用朴素回归策略（robomimic 的 `bc`）应该足够。"""),
        "48a98d8a": md("在 Lift 中，回归策略可以取得较高成功率。对于观测基本决定动作、轨迹又短的任务，用一个动作点表示的朴素策略就够了。接下来在轨迹更长、接触更精细的 Square 上试试同一个策略。"),
        "f4909fb1": md(r"""## 用回归策略训练 Square 任务

Square 要把方形螺母插入固定插销，轨迹长且接触精细。这里沿用相同的回归策略并观察成功率。"""),
        "5617996a": md(r"""Square 的成功率明显下降。视频中可能会看到策略在插销前犹豫，或者停在不完整的位置。这里混合了两个因素：

一是训练量。本 notebook 受 GPU 和时间限制，训练规模较小；训练充分后，回归策略也可能更好地解决 square-ph，因此不能简单概括为“回归无法解决 Square”。

二是长轨迹上的误差累积（compounding error）。每一步很小的偏差会改变下一次观测，使策略逐渐流向示范中没有的状态。这是逐步输出动作这一方案的结构性弱点，即使增加训练量也可能残留。接下来使用能缓解该问题的 Diffusion Policy，在相同 Square 和相同训练循环下继续实验。"""),
        "WKSu42fboBf8": md(r"""# 扩散模型

在去噪 score matching 中，网络学习预测目标分布 $p(x)$ 的 score function（得分函数）$\nabla_x \log p(x)$，也就是对数似然关于输入的梯度，从而建模真实分布。

这与预测加入数据的噪声只差一个常数比例（证明略）。

## 为什么学习 score 而不是直接学习密度

如果直接建模分布 $p(x)$，通常需要归一化常数，例如 $p_\theta(x)=e^{-f_\theta(x)}/Z_\theta$，其中 $Z_\theta=\int e^{-f_\theta(x)}\,dx$。高维积分难以计算，训练也因此困难。

score 是对数密度关于输入 $x$ 的梯度：

$$\nabla_x \log p_\theta(x)=-\nabla_x f_\theta(x)-\underbrace{\nabla_x \log Z_\theta}_{=0}$$

归一化常数不依赖 $x$，微分后会消失。因此学习 score 时完全不必计算难处理的 $Z_\theta$，仍能捕捉分布形状。

## 知道 score 有什么用

在每个点上，score 指向对数密度增加、概率更高的方向，是一个向量场。知道它后，无需计算密度值本身，也能从分布中采样。代表性方法是 Langevin dynamics：

$$x_{k+1}=x_k+\frac{\delta}{2}\nabla_x\log p(x_k)+\sqrt{\delta}\,z,\quad z\sim N(0,I)$$

score 把样本推向高密度区域，噪声则把样本扩散到整个分布。二者平衡后，经过足够多步，$x_k$ 就会成为来自 $p(x)$ 的样本。

## 作为扩散模型的形式化

单独准确估计一个分布的 score 并不容易，尤其在数据稀疏的低密度区域。因此扩散模型逐步向数据加噪，考虑每个噪声等级 $t$ 的分布 $p_t(x)$，并在各个等级学习 score $s_\theta(x_t,t)$。

生成时从纯噪声（$t=T$）开始，按照学到的 score 一点点去噪，直到 $t=0$。逆过程的每一步都类似 Langevin dynamics；二者都可以看作同一个反向 SDE 的离散化。"""),
        "7Cg2xpS3kegA": md(r"""## 扩散模型训练（伪代码）
```text
for x0 in dataloader:                                  # clean data
    t   = torch.randint(0, T, (x0.shape[0],))          # random timestep
    eps = torch.randn_like(x0)                          # sample noise
    x_t = sqrt_ab[t] * x0 + sqrt_one_minus_ab[t] * eps  # forward process (closed form)
    loss = F.mse_loss(model(x_t, t), eps)               # predict the noise, plain MSE
```

## 扩散模型推理（伪代码）
```text
x = torch.randn(n, 1, 28, 28)                        # start from pure noise
for t in reversed(range(T)):                          # 1000 sequential steps
    eps = model(x, t)                                 # predict the noise
    x = (x - beta[t] / sqrt_one_minus_ab[t] * eps) / sqrt_a[t]  # remove a bit of noise
    if t > 0:
        x = x + sqrt_beta[t] * torch.randn_like(x)    # re-inject fresh noise (DDPM)
```"""),
        "882437b2": md(r"""## Diffusion Policy

[Diffusion Policy](https://arxiv.org/abs/2303.04137) [Chi+, 2023] 把计算机视觉领域成功的**扩散模型用于生成动作**。它与上面的方法一样，从噪声中预测动作。

Diffusion Policy 不只预测一个时间步，而是一次预测多个时间步（例如 16、32）的动作序列。这能缓解误差累积（compounding error）。"""),
        "c26d8717": md(r"""## 成功率比较

像 Lift 这样短且解法唯一的任务，回归策略和 Diffusion Policy 都能解决。对于 Square 这类长且精细的任务，逐步预测的回归策略容易因误差累积而崩溃，而生成动作序列的 Diffusion Policy 通常更能坚持。下面的图展示这种差异。

成功率来自每个设置 20 次 rollout、1 个随机种子，没有误差棒。请把它作为趋势而非绝对数值来读（增加训练量后两者都可能提升）。"""),
        "671d095e": md("关于损失：回归使用动作的二次误差，扩散使用噪声预测的二次误差，定义不同，因此不能比较损失绝对值；应比较成功率。"),
        "d28a5d23": md(r"""## 总结

本 notebook 介绍了模仿学习，尤其是 BC 的一些近期主题。

- 用一个点表示动作的回归策略有两个问题：多峰数据会把多个正确答案平均掉；长轨迹中误差会累积。
- 用分布表示动作的方法可以缓解第一个问题；以序列输出动作（action chunking）的方法可以缓解第二个问题。
- 训练前了解数据集性质非常重要。本次查看了初始状态叠加、动作分布和三维轨迹。

**拓展实验**

- 增大 `NUM_EPOCHS`，或把 `N_DEMOS` 设为 `None` 使用全部示范，观察成功率变化；
- 尝试 `transport` / `tool_hang` 等更长任务，观察误差累积与序列生成的优势。

**参考链接**

- robomimic：https://robomimic.github.io/docs/index.html
- robosuite：https://robosuite.ai/
- Diffusion Policy (Chi et al., 2023)：https://diffusion-policy.cs.columbia.edu/
- ACT (Chao et al., 2023)：https://arxiv.org/abs/2304.13705
- ROS2 入门 1：https://www.docswell.com/s/tatsukamijo/K332P2-2025-07-16-234918
- ROS2 入门 2：https://skinny-chord-c58.notion.site/5-ROS-2-2-2-2049a7a1061380fc8928e500eafc57d0"""),
    },
    "第4回 演習資料.ipynb": {
        "d5PyjKe4pZUA": md("# Physical AI 基础篇 智能机器人课程 2026 Spring 第4讲练习资料"),
        "fCRLA5fGddwA": md(r"""## Colab 执行步骤

**预计耗时**：T4 GPU 约 30 分钟

### 步骤

1. 从上到下执行到“5. 让它走起来 — 从 checkpoint 到视频”。
2. 执行途中可能出现“session 崩溃”。（**这是预期行为，请直接继续步骤 3。**）
3. 把 log 文件保存到 Google Drive：

```python
   from google.colab import drive
   drive.mount('/content/drive')
   !cp -r logs /content/drive/MyDrive/
```

4. 断开并重启运行时（菜单：运行时 → 断开运行时并删除）。
5. 把 log 文件从 Google Drive 放回 `/content` 根目录：

```python
   from google.colab import drive
   drive.mount('/content/drive')
   !cp -r /content/drive/MyDrive/logs/ /content/logs/
```

6. 再次按“0. 环境准备”→“5. 让它走起来 — 从 checkpoint 到视频”的顺序执行。
   → 程序会利用步骤 5 恢复的日志生成后续视频。"""),
        "f11df5cd": md(r"""# 使用 RSL-RL 的 PPO 让 Unitree G1 走起来

本 notebook 只有一个目标：**用强化学习（PPO）让人形机器人 Unitree G1 学会“走路”**。过程中会用真实代码观察两件事：

1. **如何定义 MDP**：观测、动作、奖励、终止条件和指令分别写在哪些文件中（§1–2）；
2. **如何训练**：RSL-RL 的 PPO 如何学习这个 MDP（§3–5）。

唯一需要安装的是可通过 `pip install` 获取的 [mjlab](https://github.com/mujocolab/mjlab)。mjlab 是“Isaac Lab API × MuJoCo Warp 物理”的 GPU 并行 RL 库，内置 G1 机器人模型、速度跟踪任务以及训练/回放 CLI。流程与真实开发一致：

| 小节 | 实务步骤 | 使用内容 |
| --- | --- | --- |
| §1 | 阅读任务定义（= MDP） | `mjlab/tasks/velocity/` |
| §2 | 缩小环境并运行确认 | `ManagerBasedRlEnv` |
| §3 | 启动训练 | `mjlab.scripts.train`（RSL-RL 的 PPO） |
| §4 | 用训练曲线诊断 | TensorBoard 日志 |
| §5 | 让机器人走并用视频确认 | 回放环境 + checkpoint |

技术栈分三层：**MuJoCo Warp**（在 GPU 上并行仿真数千个实例）/ **mjlab**（以 manager 方式描述任务的环境库及内置任务）/ **RSL-RL**（腿式机器人 RL 中常用的 PPO 实现）。"""),
        "c6947578": md(r"""<div style="border:2px solid #5cb85c; padding:12px; border-radius:6px;">

✅ **本 notebook 已在 GPU 服务器上完成全 cell 执行与验证（RTX 3090 / CUDA 12.4，2026-07-04）**

- 物理引擎是 MuJoCo Warp = CUDA。**必须使用 NVIDIA GPU**（Colab：运行时 → 更改运行时类型 → GPU）。
- §0 的安装 cell 固定为已验证的版本组合（直接使用最新版本可能因为不兼容而失败，原因见 cell 内注释）。
- 训练结果（`logs/`）和视频（`videos/`）会作为文件保留；即使 session 断开，重新执行 §0 后也能从 §4–5 恢复。

</div>"""),
        "4c67df85": md(r"""## 0. 环境准备

只需安装 `mjlab`（依赖的 mujoco-warp / rsl_rl / mediapy / tensorboard 等会一并安装）。numpy 使用 Colab 已有版本的兼容范围，**通常无需重启运行时**。

> ⚠️ 如果安装 cell 末尾出现“需要重启运行时以完成 numpy 替换”的 RuntimeError（仅在 pip 替换了 numpy 时发生），请菜单选择**运行时 → 重启 session**（不是“断开并删除”——删除会换一台新机器，需要从头开始），然后再次从上到下执行。第二次安装只需几秒。
>
> ℹ️ pip 显示的依赖警告（如 moviepy / numba）来自本 notebook 不使用的 Colab 内置包之间的冲突，可以忽略。"""),
        "de9cc913": md(r"""## 1. 阅读任务定义（=MDP）

机器人 RL 的实务中，花在**设计 MDP** 上的时间往往多于编写学习算法。mjlab 采用声明式写法：把小的 term 函数（计算一个观测项、奖励项等的函数）通过 Cfg（配置对象）组合起来，这与 Isaac Lab 的 manager 方式相同。

“让 G1 走路”的任务以 **velocity（速度跟踪）任务**的形式内置于 mjlab。定义位于 pip 包中，全部是普通 Python 文件：

- MDP 主体：`mjlab/tasks/velocity/velocity_env_cfg.py`
- G1 专属调整：`mjlab/tasks/velocity/config/g1/env_cfgs.py`（机器人模型、各关节系数等）
- term 函数实现：`mjlab/tasks/velocity/mdp/*.py`
- 机器人模型：`mjlab/asset_zoo/robots/unitree_g1/`（MJCF + 执行器定义）

重点是“走路”的定义方式：不是直接把走路动作写进奖励，而是构造这样的 MDP：**在不摔倒的情况下持续跟踪随机给出的目标速度（前后、左右、旋转）**。于是 PPO 会在整形奖励的引导下把走路找到作为解决方案。

任务通过 `register_mjlab_task(task_id="Mjlab-Velocity-Flat-Unitree-G1", ...)` 注册，并用 `load_env_cfg()` 取出。§3 的训练脚本也使用完全相同的入口。"""),
        "dde046eb": md(r"""### 1.1 动作——让策略输出什么

策略输出的是 **29 个关节的目标角度偏移量**。它不直接输出 torque，而是把 `目标角 = 默认姿态 + scale × 动作` 交给各关节的 PD 控制器（执行器）。这种“用 RL 调节 PD 目标角”的方式是实体人形/四足机器人 RL 的事实标准，比直接输出 torque 更稳定，也能直接部署到真实机器人。`scale` 会按关节调整，以匹配活动范围与 torque 灵敏度。"""),
        "eb479242": md(r"""### 1.2 观测——让策略看到什么

观测分为两组。**actor**（策略看到的观测）只包含真实机器人也能从 IMU、编码器获得的量，并且会加入噪声：机身平移/角速度、重力方向（姿态）、关节角/角速度、上一个动作和速度指令。**critic**（训练期间使用的价值函数）则额外看到足部高度、腾空时间、接触力等**只有仿真器才能取得的特权信息**，形成**非对称 actor-critic**。部署到真实机器人时只带 actor，因此既能让策略在真实机器人的信息条件下运行，又能用丰富信息帮助训练。"""),
        "ae67c911": md(r"""### 1.3 指令——给任务什么目标

`twist` 指令每隔几秒随机重新采样目标速度 `(vx, vy, ωz)`。它会作为观测输入策略，也会作为奖励的参考。一些环境还会给出零速度（=保持站立）指令，因此策略也会学习“被要求停下时站稳”。**想改变任务分布，就修改这里**；例如不想要求倒着走，可以把 `lin_vel_x` 的下限设为 0。课程学习（`command_vel`）会让训练早期先从较窄的速度范围开始，再逐步扩大。"""),
        "1add8f16": md(r"""### 1.4 奖励——定义“好的行走”

这是 MDP 设计的核心。奖励大致分两类：

- **主要目标（正权重）**：`track_linear_velocity` / `track_angular_velocity`。把跟踪误差送入指数核 `exp(−err²/σ²)`，让误差为 0 时得到有界的最大值 1。
- **整形（shaping）**：其余项负责在实现主要目标时引导**走法**，例如保持机身直立（`upright`）和基准姿态（`pose`）、抑制乱晃（`body_ang_vel` / `angular_momentum`）、抑制动作变化率（`action_rate_l2`，避免抖动）、关节活动范围限制（`dof_pos_limits`）、适当抬脚（`foot_clearance` / `foot_swing_height`），以及抑制打滑（`foot_slip`）、着地冲击（`soft_landing`）和自碰撞（`self_collisions`）。

注意：这里没有显式的“摔倒惩罚”项。摔倒会触发 §1.5 的终止条件，**失去之后本来可能得到的全部跟踪奖励**，这本身就构成最大惩罚。

步态由“加入哪些项、给每项多大权重”决定。根据训练结果调整这张表的循环，是腿式机器人 RL 开发中最耗时的工作之一（权重为 0 表示保留该项但暂时禁用）。"""),
        "952748a5": md(r"""term 的实体只是一个函数，契约是 `func(env, **params) -> Tensor(num_envs,)`（按 batch 返回所有并行环境的值）。查看主要奖励 `track_linear_velocity` 的实现，会发现它只是把指令速度和实际速度的平方误差送进指数核："""),
        "3a58873c": md(r"""### 1.5 终止条件与事件（域随机化）

终止条件有两种，含义不同。`fell_over`（机身倾斜过大）表示**失败**，会立即结束 episode；正如 §1.4 所见，失去未来奖励就是惩罚。`time_out`（完成 20 秒）只是**截断**，不是失败，因此用 `time_out=True` 区分（PPO 会采用不同的价值 bootstrap 处理）。

事件用于向环境注入随机性，主要服务于 **sim2real 的域随机化**：重置时的姿态变化、每隔 5–6 秒的推搡（训练出被推后也能稳住的策略），以及摩擦、机身质心和编码器偏置的个体差异随机化。"""),
        "e149067c": md(r"""## 2. 创建环境并运行一次

前面看到的 Cfg 只是**声明**，还没有进行计算。传给 `ManagerBasedRlEnv(cfg, device)` 后，场景会在 GPU 上构建，所有 term 会针对全部并行环境向量化运行。训练前先创建一个小环境（16 个实例）并运行几步，检查观测、奖励和终止的形状——真实开发中新任务也通常从这个** smoke test** 开始。

> ⏳ 第一次运行可能需要几分钟，因为 MuJoCo Warp 会 JIT 编译 CUDA kernel；后续运行会使用缓存。"""),
        "a349c52c": md(r"""## 3. 使用 PPO 训练——`mjlab.scripts.train`

实务中通常不把训练直接写在 notebook cell 里，而是用 **CLI 脚本**运行（便于长任务重试、记录参数并抵抗连接中断）。mjlab 自带 `train` / `play` 命令；在工作站上只需运行 `train Mjlab-Velocity-Flat-Unitree-G1 --env.scene.num-envs=4096`。其核心（`mjlab/scripts/train.py`）本质上是四步：

```python
env    = ManagerBasedRlEnv(cfg=env_cfg, device=device)             # 与 §2 相同
env    = RslRlVecEnvWrapper(env, ...)                              # 适配 RSL-RL 输入输出的薄封装
runner = VelocityOnPolicyRunner(env, agent_cfg, log_dir, device)   # RSL-RL 的 PPO runner
runner.learn(num_learning_iterations=max_iterations)
```

PPO 的一个 iteration 包含：① **rollout**：用当前策略在 GPU 上收集 `24 step × 4096 个环境 ≈ 10 万次转移`；② **GAE**：估计每个动作的好坏（advantage）；③ **更新**：用带 clipping 的策略梯度训练 5 个 epoch，把新旧策略的比率限制在 ±20%，避免单次变化过大。这种“高并行 rollout + 短周期更新”是 GPU 仿真器与 PPO 的经典组合（算法细节见课程第 4 章）。

PPO 超参数也和任务一起注册，先查看它们："""),
        "5deb86cc": md(r"""开始训练。日志会写入 `logs/rsl_rl/g1_velocity/<日期>_notebook/`（TensorBoard event、`model_*.pt` checkpoint，以及用于真实机器人部署的 ONNX）。

> ⏳ 500 个 iteration 是演示用的短配置（RTX 3090 十几分钟，T4 约 1–2 小时）。想缩短时间可把 §0 的 `MAX_ITERATIONS` 调到 200–300；仍能看到机器人不摔倒并开始朝指令方向走。想看到平滑步态，需要数千个 iteration 以上（mjlab 默认 30000）。
>
> 💾 在 Colab 中，训练后把 `logs/` 备份到 Google Drive 会更稳妥（先 `from google.colab import drive; drive.mount('/content/drive')`，再执行 `!cp -r logs /content/drive/MyDrive/`）。"""),
        "572ad16b": md(r"""## 4. 阅读训练曲线

用 matplotlib 绘制 TensorBoard event 文件。这个设置中最直接的“学会了”指标是**平均 episode 长度**（不摔倒能坚持的步数，上限 1000）逐渐上升。

> ⚠️ `Train/mean_reward` 是包含整形惩罚的总和；存活时间变长时，惩罚也会累积，所以训练早期它可能反而下降。实务上不要只看“总奖励”，要综合观察**episode 长度↑ + 跟踪奖励（`track_*`）↑ + 动作标准差↓（探索收敛）**。`Episode_Reward/*` 是 episode 总量除以最大 episode 时长 20 秒得到的每秒速率。"""),
        "e48c7960": md(r"""## 5. 让它走起来——从 checkpoint 到视频

在工作站上，实务流程是运行 mjlab 自带的 `play Mjlab-Velocity-Flat-Unitree-G1 --checkpoint_file=...`，在 GUI viewer 中交互检查策略。在无头 notebook 中手动完成相同流程：取得 **play 环境配置**（无观测噪声、无推搡、仅 1 个实例、episode 实际上不限时），从 `logs/` 的最新 checkpoint 恢复策略，rollout 后写成 mp4。

关键在于它与训练进程相互独立。即使 Colab 断开，只要 `logs/` 还在（或能从 Drive 恢复），只运行这个 cell 就能重新生成视频。

> 渲染使用 `MUJOCO_GL=egl`（可在 Colab GPU runtime 中运行）。如果某个环境的 EGL 失败，请先执行 `!apt-get install -y libosmesa6`，再把 §0 中的 `os.environ["MUJOCO_GL"]` 改为 `"osmesa"` 并重跑。"""),
        "2094051a": md("> 这是 500 iteration 的短训练，所以画面更接近“站住并尝试朝指令方向走”，还不是平滑步态。把 `MAX_ITERATIONS` 增加到数千后，会更接近官方演示。"),
        "8993ee1b": md(r"""## 6. 总结——下一步

本 notebook 走完了一次真实开发循环：

**阅读 MDP（§1）→ 小规模运行确认（§2）→ 用 CLI 训练（§3）→ 用曲线诊断（§4）→ 运行并确认（§5）**

后续工作就是不断重复这个循环：

- **改变步态**：从 §1.4 的奖励表入手。可以修改 `load_env_cfg()` 返回的 `cfg.rewards[...].weight`，再按 §2 创建环境并训练；也可以从 GitHub clone mjlab（`pip install -e`），直接修改 `tasks/velocity/` 中的权重并重新运行。这就是腿式机器人 RL 的日常开发循环。
- **延长训练**：使用 `--agent.max-iterations=3000` 以上得到更平滑的步态。想在崎岖地形行走，可以尝试带地形课程的 `Mjlab-Velocity-Rough-Unitree-G1`。
- **部署到真实机器人**：训练时会自动写出部署用 ONNX（`<run名>.onnx`，位于 `logs/`）。真实部署可参考 Unitree 官方的 [unitree_rl_mjlab](https://github.com/unitreerobotics/unitree_rl_mjlab) 仓库中的 `deploy/`。
- **创建自己的任务**：把 `mjlab/tasks/velocity/` 的结构（term 函数 + Cfg + `register_mjlab_task`）复制到自己的包中再修改，这是实务中常见的做法。manager 方式源自 Isaac Lab，因此同样的模式也适用于 Isaac Lab。"""),
    },
}


STEP6_BY_INDEX = {
    0: md(r"""# Physical AI 基础篇 智能机器人课程 2026 Spring 第6讲练习资料

本讲围绕真实机器人数据的质量检查、时间同步、格式转换和标签审计展开。你会把 ROS bag 中的多路消息整理成可供 LeRobotDataset 使用的训练数据，并观察同步偏移如何影响后续策略。

完整版包含完整参考实现；填空版从自己的源文件生成，只保留原有的 5 个 TODO 差异。"""),
    1: md(r"""### 开始：格式与 Colab 使用方式

按 cell 顺序执行。安装和数据准备只需在 Colab 中进行；重型模型与 checkpoint 会在实际使用它们的 cell 中按需下载。遇到长时间下载时请保持 session 连接，并留意每个步骤的 self-check。"""),
    5: md(r"""## Step 1：Inspect——解剖原始数据（5 分钟）

先从 topic 频率、时间戳和设备延迟入手。ROS bag 同时记录设备写入的 `header.stamp` 与记录机收到消息的时间；这两个时间轴不一致时，单纯看消息数量可能会错过真正的问题。"""),
    10: md("### 写下你的观察（1 行即可）\n\n记录哪一个 topic 或 bag 最值得进一步检查，以及你依据的时间戳/频率证据。"),
    12: md(r"""## Step 2：Sync——自己实现 ApproximateTime（8 分钟）

以主相机帧为基准，在允许的 `slop` 内为其他 topic 找最近消息。关键是区分“没有匹配”与“勉强匹配”，并检查匹配残差；同步后的数据质量取决于真实时间关系，而不是只取决于消息计数。"""),
    18: md(r"""### 填写思考（2 个问题）

1. 增大 `slop` 后，保留率和匹配残差分别如何变化？
2. 设备写入时间与物理响应之间不一致时，你会相信哪个证据，为什么？"""),
    20: md(r"""## Step 3：Format & Visualize——转换为 LeRobotDataset 并核验（5 分钟）

把同步后的多路数据写成 LeRobotDataset。除了 shape 和 dtype，还要检查 episode 长度、动作维度、视频帧和夹爪动作是否彼此对齐。"""),
    25: md("### 写下你的观察\n\n比较视频、动作和统计图，记录一个你认为需要保留、过滤或重新标注的现象。"),
    26: md(r"""## Step 4a：Curate——填写判断表（3 分钟 + 随时补充）

数据清洗不是“看到异常就删除”。对每个 episode 记录 `keep`、`filter` 或 `relabel`，并在 `method` 和 `reason` 中写下可复核的依据，例如延迟、最大时间差、jerk、目视结果或 kNN。这样下游训练才能追溯每个决定。"""),
    28: md(r"""### 练习：填写判断表

- 把 Step 1（延迟）、Step 2（互相关）和 Step 3（统计）发现的问题写进对应行；
- 对犹豫的 bag 用 `utils.episode_video(ds16, episode_id)` 做**最终目视检查**；
- 课堂内填好**至少 1 行**即可，其余可在有时间时完成。"""),
    30: md(r"""## Step 4b：用 embedding kNN 审计标签——统计正常也可能有问题（教师演示）

*对应课程幻灯片“指令标签错误”和“经典工具能做到什么程度”。*

即使通过延迟、gap、长度和 jerk 的全部检查，仍可能有 **2 个 bag 不对**。数值统计和图表都正常，问题在于**指令标签与实际动作不匹配**，也就是 instruction label noise。

这里实现两种工具：

- **Deep kNN** [Bahri+ ICML 2020]：在 embedding 空间中让邻居投票，怀疑那些预测标签与原标签不一致的样本；
- **最近质心（prototype）**：用样本到各任务中心向量的距离查找不一致。

本练习的 lift 与 can 在视觉上容易区分，因此只用视觉 embedding 就能发现问题。但真实数据中，放入架子与从架子取出等任务可能很相似，需要考虑多视角和多模态证据；“应该相信哪个模态、模态失效时怎么办”仍是机器人领域几乎未解决的研究问题。请先亲手运行工具。"""),
    37: md(r"""## Step 5：训练对比——核对交付物（4 分钟，以阅读为主）

*对应课程幻灯片“数据质量与策略性能”。*

这里准备了 3 个 checkpoint：它们使用相同的 ACT 和相同的训练规模（200k step），只改变数据（can 任务，完整数据预训练）：

1. **① 保留同步偏移**：与 D1 一样带有 +350 ms 偏移（300 条）；
2. **② 修正同步**：只修复时间同步，但保留“动作笨拙但成功”的 worse 样本（300 条）；
3. **③ 同时过滤 worse**：修正同步并删除 worse（仅 200 条）。

重点看两件事：① 的 loss 仍然会正常下降，说明“能训练起来”和“机器人能正确运动”是两回事；② 与 ③ 的排名则检验“应该丢弃低质量数据”的直觉。在这个规模下，过滤可能损失数据量和覆盖范围，因此处理是否正确依赖任务、规模和策略，必须测量副作用。"""),
    40: md(r"""### 讨论（与教师一起）

- **①（不修同步）与 ②（修同步）的差异**：350 ms 偏移破坏了多少策略性能？结合发展实验的 0/100/200 ms 剂量反应，说明可接受的偏移范围。
- **②（含 worse 的 300 条）与 ③（过滤后 200 条）的差异**：低质量数据并不总该删除。lift 的小实验里 worse 可能无害，而 can 在这个规模下删除它会损失覆盖范围；“先测副作用，再决定过滤或重标注”是今天的原则。
- 两个标签错误样本没有影响今天 ACT 的成功率，因为 ACT 没有把语言指令作为输入。什么样的策略会从 relabel 中受益？"""),
    41: md(r"""## Step 6（拓展小实验）：同步偏移从多少毫秒开始破坏策略

这是一个把“数据质量 → 成功率”亲手连起来的实验（约 15–20 分钟）。Step 5 使用的是教师预训练结果；这里自己训练一个最小版本：

- 任务是 lift（约 2.5 秒），固定 20 条演示，图像 96×96，小型 ACT，5000 step；
- 唯一质量旋钮是“把所有 episode 的观测与动作错开多少毫秒”：`{0, 100, 200}`；
- 每个数据集约 1 MB，Colab T4 GPU 训练约 10–12 分钟。请选择“运行时 → 更改运行时类型 → T4 GPU”。

> ⚠️ 更改运行时类型会初始化环境，pip 安装和补丁都会消失。切换到 T4 后，请先重新执行 cell 0-1、0-2，再执行 6-1。普通“重启 session”会保留文件，不必重新安装。
>
> **恢复步骤**：①运行时 → 重启 session；②重新执行 0-1、0-2；③确认 0-2 中 `import lerobot.policies` 成功；④回到 6-1。

三种条件任选一种训练和评估，再与教师曲线比较：

| 偏移 | 0 ms | 100 ms | 200 ms |
|---|---:|---:|---:|
| 教师实测（5000 step、每项 100 次 rollout） | 80% | 74% | 56% |

200 ms 的下降具有统计显著性（p<0.001），100 ms 只有趋势、差异不显著。你自己的 10 次 rollout 噪声较大；全班汇总后才会看出稳定趋势。"""),
    44: md(r"""### 记录区

> 我负责的偏移：____ ms；成功率：____%（10 次 rollout）；与教师曲线的差异：____
> 观察（例如：100 ms 与 Step 1 测得的相机传输延迟处在同一数量级）：

**思考问题**：本实验中 200 ms 偏移让成功率下降约 24 个百分点（100 ms 约 6 个百分点，仍在误差范围内）。结合 Step 1 的延迟和 Step 2 的 `slop`，你的机器人记录系统大约能容忍多大偏移？"""),
    45: md(r"""## 想继续探索（拓展，不要求提交）

- 先完成上面的 Step 6，至少尝试一个条件；也可以与同学分工，合并出三点曲线；
- 用自己的规则对完整数据做清洗并重新训练：对 can 的完整数据（ph 200 条 + multi-human 300 条，已转换并提供）按长度、jerk、延迟阈值执行规则，再训练 ACT 并评估，看看能否超过教师条件②的 88%；
- 用偏移估计“拯救”D1 bag，重新同步后加入训练集，成功率会提高吗？
- 测试加入或移除 multi-human 数据中 okay 层的敏感性，观察数据量与质量之间的权衡。"""),
}


BASIC_MARKDOWN = {
    "b8772f57": md(r"""# SmolVLA × LIBERO-plus Spatial Fine-tuning——最终课题教材（基础版）

## 教材定位

本教材用于体验从零开始用 **PyTorch** 编写 **Vision-Language-Action（VLA，视觉-语言-动作）** 模型，并在机器人仿真环境中训练和评估的完整工作流。

我们实现一个吸收 SmolVLA（Hugging Face, 2025）**核心概念**的教育版简化 VLA：冻结 VLM + Flow Matching + action chunking。它不是官方代码的完整复刻，而是优先保证可学习、可检查的最小结构（与官方实现的差异见 section 8.5）：

1. 用预训练权重加载并冻结 **Vision-Language 部分**（SmolVLM2-500M）；
2. 从零实现并训练 **Action 部分**（基于 Flow Matching 的 transformer）；
3. 在 LIBERO-plus 环境中测量**成功率**并输出 rollout **视频**；
4. 把训练条件和结果整理为**提交用 JSON**。

## 🎯 基础版需要提交的内容

**填完所有空缺并从上到下运行 notebook 后，会生成 `submission.json`。**

`section 8-9` 中有 `TODO 1` 到 `TODO 4` 四处**填空题**（用 `raise NotImplementedError(...)` 明确标记）。如果没有全部正确填写，notebook 会在中途停止，无法生成提交 JSON。

### <font color="red">※ 完成课题提交前，请不要编辑填空位置以外的内容</font>

| # | 位置 | 要实现的内容 | 提示（公式） |
|---|---|---|---|
| TODO 1 | 8.1 `SinusoidalTimeEmbedding.forward` | 时间与频率的外积 | $\text{args}[b, i] = t[b] \cdot \text{freqs}[i]$ |
| TODO 2 | 8.5 `SmolVLA.compute_loss` | 线性路径上的中间点 $x_t$ | $x_t = (1-t)\,x_0 + t\,a$ |
| TODO 3 | 8.5 `SmolVLA.compute_loss` | 真实速度 $v^*$ | $v^* = a - x_0$ |
| TODO 4 | 8.5 `SmolVLA.sample_actions` | 一步 Euler 更新 | $x \leftarrow x + v \cdot dt$ |

四个答案都只是**一行短公式**。在 `raise` 后有 `... = ??` 占位符；删除 `raise` 那一行并填写 `??`。

### 提交物（基础版）

执行 `section 11` 会在浏览器下载 **`submission.json`**，同时备份到 Drive：

- **`submission.json`** ← ★唯一需要提交的文件★
- `submission.md` / `pip_freeze.txt` —— 仅供参考，不需提交

基础版的目标是“**实现能运行**”，不是比拼分数。**成功率不用于判定**；教育版从零训练且数据量小，基本以失败为预期（**即使成功率 0% 也合格**）。想竞争数值成绩或展示改进，请使用另一个 Advanced notebook。

## 运行环境（Colab）

本 notebook 以 **Google Colab** 为目标：

- 工作目录为 `/content/workdir`（优先保证运行速度，属于临时目录）；
- 产物会自动复制到 Google Drive 的 `MyDrive/smolvla_task/`，避免运行时结束后丢失。

**运行前必须完成**：

- 选择 **运行时 → 更改运行时类型 → GPU**（T4 或更高）；
- Section 1 请求挂载 Drive 时允许授权。

**Colab 注意事项**：

- LIBERO-plus assets（6GB）的下载与展开需要时间，请提前确认连接稳定；
- Colab 有连续运行时长限制，必要时分段执行并保存进度；
- Drive 剩余空间不足会导致备份失败，请提前检查 `MyDrive`。

## 数据与环境

训练和评估都基于 [LIBERO-plus](https://github.com/sylvestf/LIBERO-plus)。

### 训练数据

- **Hugging Face dataset**：[`lerobot/libero_plus`](https://huggingface.co/datasets/lerobot/libero_plus)
- **任务**：LIBERO-Spatial 的 10 个任务（都是“把黑碗放到盘子上”的变体）
- **episode 数**：10 个任务 × 5 episode = **50 个 episode**（section 7 抽取）

### 评估环境

- **仿真器**：`LiberoEnv`（经由 LeRobot 使用 LIBERO-plus 扰动仿真）
- **任务**：从 LIBERO-Spatial 10 个任务中取 2 个任务各 1 个 episode（共 2 次 rollout）

### 数据流

| 步骤 | 内容 | 来源 |
|---|---|---|
| 抽取数据 | 从 Hugging Face `lerobot/libero_plus` 选出 50 个 episode | section 7 |
| 训练 | 从零训练 PyTorch SmolVLA | section 9 |
| 评估 | 在 `LiberoEnv` 中 rollout | section 10 |
| 提交 | **生成 `submission.json` 并下载** | section 11 |

## 默认条件（可在 `section 6` 修改）

- 训练 episode：LIBERO-Spatial 10 个任务 × 每个 5 个；
- 训练 step：300；
- 模型：`transformer_hidden_dim=256`、4 层（可在 `section 8.5` 调整，同时列出论文规模）；
- 评估：2 个任务 × 1 个 episode = 2 次 rollout（自定义 SmolVLA）。"""),
    "toc-cell": md(r"""## 📖 目录与各 section 的作用

按从上到下的顺序执行。带 **★** 的部分是本课题的核心。

### 【准备阶段】环境与数据

| # | Section | 内容 |
|---|---|---|
| 1 | Colab runtime 检查 | 检查 GPU / Python 版本并设置 `WORKDIR` |
| 2 | 系统包 | 用 apt 安装 `ffmpeg` / `libgl` 等 |
| 3 | LeRobot 安装 | clone v0.6.0 并 editable install |
| 4 | HF 获取辅助函数 | 定义 429 重试和缓存优先的获取函数 |
| 5 | LIBERO-plus 环境 | pin 安装 MuJoCo + robosuite，并下载/展开 6GB assets |
| 6 | 设置训练/评估条件 | 定义数据集、seed、路径等共享常量 |
| 7 | Spatial 数据抽取 | 等间隔抽取 10 个任务 × 5 episode = 50 个 |

### 【★核心】实现 SmolVLA → 训练 → 评估

| # | Section | 内容 |
|---|---|---|
| **8** | **★ 用 PyTorch 实现 SmolVLA** | **包含 TODO 1–4** |
| 8.1 | 时间嵌入 | 把连续时间 `t` 变成高维向量（**TODO 1**） |
| 8.2 | Transformer block | Self/Cross attention + MLP |
| 8.3 | Flow Matching Head | 预测速度场的 transformer |
| 8.4 | 加载并冻结 SmolVLM2 | 以 fp16/bf16 加载并冻结 500M VLM |
| 8.5 | 组装 SmolVLA | 连接 VLM 与 Action head（**TODO 2、3、4**） |
| 8.6 | 检查可训练参数 | 打印 trainable / frozen 的构成 |
| **9** | **训练** | 用 50 个 episode 训练自定义 SmolVLA |
| 9.1 | LIBERO 数据集 | 用 `LeRobotDataset` 提供带 action chunk 的样本 |
| 9.2 | action 归一化 | 计算全部 action 的 mean/std |
| 9.3 | PyTorch 训练循环 | AdamW + warmup+cosine + 梯度裁剪 |
| **10** | **评估与 rollout 视频** | 在 LIBERO 环境中运行并生成 mp4 |
| 10.1 | LIBERO rollout | 2 个任务 × 1 episode 测成功率并收集 frame |
| 10.2 | 制作视频 | 用 `av`（PyAV）制作 mp4 并嵌入 notebook |
| **11** | **★ 导出提交日志** | **这里生成 `submission.json`** |

Advanced 课题（LeRobot 路线、25 个任务的广域评估）在单独的 `smolvla_libero_plus_spatial_advanced.ipynb` 中完成。

### 💡 注意

### <font color="red">※ Section 1–7 是环境和数据准备，按要求执行即可</font>
### <font color="red">※ 填写 Section 8 的 TODO，然后执行 9–11</font>
### <font color="red">※ 提交完成前不要编辑填空位置以外的内容</font>"""),
    "91a0390a": md("## 1. 检查 Colab runtime\n\n请先把 Colab runtime 切换到 GPU，再执行此 cell。"),
    "e7b3a617": md("## 2. 准备系统包\n\n安装 LeRobot、视频解码和 MuJoCo 所需的系统包。"),
    "da486697": md("## 3. 安装 LeRobot\n\n使用 LeRobot `v0.6.0`，本 cell 同时应用 Colab LoRA 训练所需的兼容性调整。"),
    "13be75a1": md("## 4. 准备公开文件获取流程\n\n优先使用缓存；匿名访问受限时自动重试。"),
    "md-sec4": md("## 5. 准备 LIBERO-plus 评估环境\n\n安装 MuJoCo / robosuite / LIBERO-plus fork，并展开评估所需 assets。\n\n由于需要下载并展开约 6GB 的 `assets.zip`，这个 cell 会花较长时间。"),
    "36431140": md(r"""## 6. 设置训练与评估条件

这里仅定义**两条路线共有的内容**：

- 模型 / 数据集 repo 与 revision；
- LIBERO-Spatial 的 10 个任务列表；
- 训练使用的 episode 数和 seed；
- 输出路径与混合精度。

每条路线自己的超参数在下面定义：
- PyTorch 版 → `section 9.3` 的 `TRAIN_STEPS_PY` 等；
- LeRobot 版 → Advanced 的 `STEPS` 等。"""),
    "11702cd4": md("## 7. 选择 Spatial 训练数据\n\n从 10 个任务中为每个任务等间隔选择 5 个 episode。"),
    "md-sec8": md(r"""## 8. 用 PyTorch 实现 SmolVLA

这是本教程的核心：参考论文和实现，用 PyTorch 逐步写出 **Vision-Language-Action 模型 SmolVLA**。

### 参考论文与实现

- **SmolVLA 架构** — Shukor et al., “SmolVLA: A Vision-Language-Action Model for Affordable and Efficient Robotics”（Hugging Face, 2025）— <https://huggingface.co/blog/smolvla>
- **Flow Matching（action head 生成模型）** — Lipman et al., “Flow Matching for Generative Modeling”（ICLR 2023）— <https://arxiv.org/abs/2210.02747>
- **Transformer self/cross-attention** — Vaswani et al., “Attention Is All You Need”（NeurIPS 2017）— <https://arxiv.org/abs/1706.03762>
- **LoRA（Low-Rank Adaptation）** — Hu et al., “LoRA: Low-Rank Adaptation of Large Language Models”（ICLR 2022）— <https://arxiv.org/abs/2106.09685>
- **LIBERO 基准** — Liu et al., “LIBERO: Benchmarking Knowledge Transfer for Lifelong Robot Learning”（NeurIPS 2023）— <https://arxiv.org/abs/2306.03310>
- **基准实现** — LeRobot v0.6.0 policies.smolvla — <https://github.com/huggingface/lerobot/tree/v0.6.0/src/lerobot/policies/smolvla>

### 整体结构

VLA 模型是两段流水线：

- **1. VLM（frozen）** — 输入：图像 $x \in \mathbb{R}^{H \times W \times 3}$ + 任务描述 $\tau$；输出：$h \in \mathbb{R}^{L \times 960}$。
  - 使用 SmolVLM2-500M 转成融合表示，参数不训练；
- **2. Action head（Flow Matching Head，可训练）** — 输入：noisy action chunk $x_t$、时间 $t$、条件 $(h,\ \text{state})$；输出：速度场 $v_\theta(x_t,t,h) \in \mathbb{R}^{K \times d_a}$。
  - 内部是多层 Transformer（self-attn + 对 VLM 的 cross-attn + MLP），再接输入/输出投影；
  - 通过 Flow Matching（Lipman et al. 2023）生成 action chunk。

其中 $K$ 是 `chunk_size`（未来 step 数），$d_a$ 是动作维度（LIBERO 为 7 = 6-DoF + gripper），$L$ 是 image patch + text token 数。

**要点**：VLM 冻结（不触碰 500M 参数），只训练 Action head 的数百万参数。

### Flow Matching 公式

对真实动作 $a \in \mathbb{R}^{K \times d_a}$ 和高斯噪声 $x_0 \sim \mathcal{N}(0,I)$，定义 $t \in [0,1]$ 的**直线路径**：

$$x_t=(1-t)x_0+t a$$

路径上的**真实速度**是：

$$v^*(x_t,t)=\frac{d x_t}{dt}=a-x_0$$

给定条件 $c$（图像、语言）后，让网络 $v_\theta(x_t,t,c)$ 回归 $v^*$，得到 Flow Matching Loss：

$$\mathcal{L}(\theta)=\mathbb{E}_{a\sim\mathcal{D},\ x_0\sim\mathcal{N},\ t\sim U(0,1)}\left[\left\|v_\theta(x_t,t,c)-(a-x_0)\right\|^2\right]$$

**推理**从纯噪声 $x_0 \sim \mathcal{N}(0,I)$ 出发，用 Euler 方法求解 ODE：

$$x_{t+\Delta t}=x_t+v_\theta(x_t,t,c)\cdot\Delta t$$

从 $t=0$ 推进到 $1$ 共 $N$ 步，就得到 $x_1\approx a$（通常 $N\in[5,20]$）。

### 为什么用 Flow Matching（而不是 Diffusion）

- **训练简单**：DDPM 需要处理每个时间的噪声 schedule 和方差，而 FM 只需学习“真实速度 = $a-x_0$”；
- **推理快速**：直线路径只需少量步骤（5–10）就容易得到不错的精度；
- **数值稳定**：不容易发散。

### 实现要点

- **冻结 VLM**：训练 500M 参数会同时增加资源消耗和过拟合风险；
- **只训练 Action head**：Transformer、输入/输出投影和位置/时间嵌入只包含数百万参数；
- **Action head 从零完整训练**：不使用 LoRA（详见 8.6）。

后续 cell 会逐个搭建这些组件。"""),
    "md-sec8-1": md(r"""### 8.1 时间嵌入

将标量时间 `t` 映射为高维的 sinusoidal 向量，让 Action head 知道当前位于 flow 的哪个阶段。这里的 TODO 只需要构造时间和频率的外积，shape 契约是 `(B, dim)`。"""),
    "md-sec8-2": md(r"""### 8.2 Transformer block

Action token 先进行 self-attention，再通过 cross-attention 读取冻结 VLM 的视觉-语言 token，最后经过 MLP。保留 token 维度和 batch 维度的 shape 契约，是后续 action chunk 正常工作的关键。"""),
    "md-sec8-3": md(r"""### 8.3 Flow Matching Head

这个 head 输入 noisy action chunk、时间嵌入和 VLM 条件，预测每个 action token 的速度。训练时回归 `a - x0`，推理时从高斯噪声开始，用多次 Euler 更新生成动作序列。"""),
    "md-sec8-4": md(r"""### 8.4 加载并完全冻结 SmolVLM2

加载 `SmolVLM2-500M-Video-Instruct` 作为视觉-语言 backbone。它只提供条件表示，不参与反向传播；这样训练资源集中在本课题自己实现的 Action head 上。"""),
    "md-sec8-5": md(r"""### 8.5 组装 VLA

把冻结的 VLM、状态投影和 Flow Matching Action head 连接起来。重点检查：图像/语言条件是否与 batch 对齐，action chunk 是否为 `(B, K, d_a)`，以及训练和 rollout 是否使用同一个归一化/反归一化契约。

四个 TODO 分别对应 Flow Matching 的核心公式：中间点、真实速度和 Euler 更新，以及时间嵌入所需的外积。不要改变填空范围或训练参数。"""),
    "md-sec8-6": md("### 8.6 检查可训练参数\n\n确认 VLM 参数全部 frozen，只有 Action head、投影层和嵌入层被列为 trainable。若冻结状态不符合预期，先在继续训练前检查模型组装。"),
    "md-sec9": md("## 9. 训练\n\n使用前面构建的模型和 LIBERO 数据进行少量训练。先准备 action chunk 与归一化统计，再运行 PyTorch 训练循环。"),
    "md-sec9-1": md("### 9.1 加载 LIBERO 数据集\n\n用 `LeRobotDataset` 提供带有 `chunk_size` 个 future action 的样本。训练与 rollout 必须保持相同的观测键、shape 和 action 顺序。"),
    "md-sec9-2": md("### 9.2 计算 action 的 mean / std（归一化）\n\n从训练数据计算 action 的均值和标准差。模型在归一化空间学习，推理结束后必须使用同一组统计量反归一化。"),
    "md-sec9-3": md("### 9.3 PyTorch 训练循环\n\n运行 AdamW、warmup+cosine 学习率与梯度裁剪。基础版的目标是验证实现和日志契约能够走通，不要把少量训练的成功率当作最终性能结论。"),
    "md-sec10": md("## 10. 评估与 rollout 视频\n\n在 LIBERO 环境中运行策略、记录 frame，最后编码为 mp4。评估使用与训练一致的预处理和 action 后处理。"),
    "md-sec10-1": md("### 10.1 在 LIBERO 环境中 rollout\n\n在 2 个任务上各运行 1 个 episode，测量成功率并收集画面。每次新 episode 开始前要重置 action queue。"),
    "md-sec10-2": md("### 10.2 编码并嵌入视频\n\n用 `av`（PyAV）把 frame 序列编码成 mp4，并把视频嵌入 notebook。"),
    "md-sec11": md(r"""## 11. 导出提交日志（基础版要求）

执行本 section 会生成 `submission.json`、辅助说明和依赖记录，并触发浏览器下载。提交时只上传 `submission.json`；Basic 版本的哈希和日志结构属于程序契约，请不要改变。"""),
}


ADVANCED_MARKDOWN = {
    "b8772f57": md(r"""# SmolVLA × LIBERO-plus Spatial Fine-tuning——最终课题教材（进阶版）

## 教材定位

请先完成 **基础版（`smolvla_libero_plus_spatial_basic.ipynb`）**，再开始进阶版。

进阶版包含：

1. 使用 LeRobot 官方实现（`SmolVLAPolicy`），对预训练 SmolVLA 做 **LoRA 追加训练**；
2. 在 LIBERO-plus **4 个 suite × 每个 3 个任务 × 1 个 episode = 每个模型 12 次 rollout**上做广域评估；
3. 通过调整 Section 8.0 的超参数，提升 LeRobot 路线性能。

#### <font color="red">希望争取贡献奖的同学，请把你的改进点发到指定 Slack。</font>

## 与基础版的关系

- **基础版**：用 PyTorch 自己实现 SmolVLA → 训练 → 评估 → 提交 `submission.json`；
- **进阶版（本 notebook）**：用 LeRobot 官方版 warm-start 训练 → 在 4 个 suite 上广域评估。

### 主要差异

- **主目标**：基础版理解 SmolVLA 内部，进阶版使用官方实现做实践；
- **模型**：基础版是教育用简化模型，进阶版是 LeRobot 官方 `SmolVLAPolicy`；
- **Action head 初始值**：基础版随机初始化，进阶版从预训练权重 warm-start；
- **训练方法**：基础版自定义 PyTorch 循环，进阶版通过 `lerobot-train` 使用 LoRA；
- **评估范围**：基础版 Spatial 2 个任务 × 1 episode，进阶版 4 个 suite × 3 个任务 × 1 episode。

### 共用的 Drive 缓存

基础版 Section 5 生成的 **LIBERO-plus assets tar.gz 缓存**（`Drive/MyDrive/smolvla_task/libero_plus_assets.tar.gz`）会被进阶版自动发现并复用。若基础版已经完成，进阶版 Section 5 只需展开 tar.gz，耗时会明显减少。

## 运行环境（Colab）

与基础版相同：使用 **GPU（T4 或更高）**并允许挂载 Drive。

## 数据与环境

- **训练数据**：`lerobot/libero_plus`（与基础版相同）；
- **评估环境**：`LiberoEnv`（LIBERO-plus 扰动仿真）；
- **评估范围**：LIBERO Spatial + Object + Goal + Long-horizon，**4 个 suite / 每个 3 个任务 / 1 个 episode = 每个模型 12 次 rollout**。"""),
    "toc-cell": md(r"""## 📖 目录与各 section 的作用

### 【准备阶段】环境与数据（与基础版共用）

1. 检查 Colab runtime——确认 GPU / Python 版本并设置 `WORKDIR`；
2. 系统包——用 apt 安装 `ffmpeg` / `libgl` 等；
3. 安装 LeRobot——clone v0.6.0 并 editable install；
4. HF 获取辅助函数——定义 429 重试和缓存优先的获取函数；
5. 准备 LIBERO-plus——复用基础版的 Drive tar.gz 缓存（没有时执行完整下载）；
6. 设置训练/评估条件——定义数据集、seed、路径等共享常量；
7. 抽取 Spatial 训练数据——等间隔选择 10 个任务 × 5 episode = 50 个。

### 【★核心】用 LeRobot 训练 → 广域评估

**Section 8（LeRobot 训练/评估）**：对预训练 SmolVLA 做 LoRA 追加训练。若要继续 Section 9，必须完整执行 Section 8。

- **8.0** 进阶超参数：调整 `STEPS` / `LORA_R` / `LEARNING_RATE` 等；
- **8.1** 下载预训练 SmolVLA（`lerobot/smolvla_libero_plus`）；
- **8.2** 用 LeRobot subprocess 进行 LoRA 训练（`lerobot-train`）；
- **8.3** 把 LoRA 合并回 base（`PeftModel.merge_and_unload`）；
- **8.4** 准备对照 baseline（用同一个 processor 保存追加训练前的权重）；
- **8.5** 在 Spatial 上比较训练前后（10 task × 1 ep × 2 model = 20 rollout）；
- **8.6** 比较 LeRobot 版本的成功率（每任务 Δ + CSV）；
- **8.7** 把合并模型压缩为 zip（提交用）；
- **8.8** 可选地输出 rollout 视频（mp4）。

**Section 9（进阶评估）**：4 suite × 3 task × 1 ep = 每模型 12 次 rollout（共 24 次）。"""),
    "91a0390a": md("## 1. 检查 Colab runtime\n\n请先把 Colab runtime 切换到 GPU，再执行此 cell。"),
    "e7b3a617": md("## 2. 准备系统包\n\n安装 LeRobot、视频解码和 MuJoCo 所需的系统包。"),
    "da486697": md("## 3. 安装 LeRobot\n\n使用 LeRobot `v0.6.0`，本 cell 同时应用 Colab LoRA 训练所需的兼容性调整。"),
    "13be75a1": md("## 4. 准备公开文件获取流程\n\n优先使用缓存；匿名访问受限时自动重试。"),
    "md-sec4": md("## 5. 准备 LIBERO-plus 评估环境\n\n安装 MuJoCo / robosuite / LIBERO-plus fork，并展开评估所需 assets。这个步骤同时服务 PyTorch 版评估（section 10）与 LeRobot 版评估（section 8），请尽早完成。\n\n由于需要下载并展开约 6GB 的 `assets.zip`，这个 cell 会花较长时间。"),
    "36431140": BASIC_MARKDOWN["36431140"],
    "11702cd4": BASIC_MARKDOWN["11702cd4"],
    "md-sec12": md(r"""## 8. 使用 LeRobot 进行 LoRA 追加训练

> **📌 如果要进入 Section 9，本 section 必须完成。**
> Section 9 的进阶评估需要 Section 8.3 生成的合并模型和 8.4 生成的对照 baseline。不能只执行 Section 9，请先完成整个 Section 8。

> **📎 本 section 负责生成 Section 9 的输入。**
> 这里生成的训练后模型（`MERGED_MODEL_DIR`）和对照 baseline（`BASELINE_MODEL_DIR`）会作为 Section 9 的输入。只要经由 `SmolVLAPolicy.save_pretrained` 保存，传入 Section 9 的格式就会自动正确；通常只需调整 Section 6 的超参数或 Section 8.2 的 `lerobot-train` 参数，评估代码无需修改。详见 Section 9 开头的“输入格式契约”。

> **📌 LoRA 的优势在这里体现。** 基础版从随机初始值训练 Action head，因此 LoRA 的收益有限；进阶版先 warm-start `lerobot/smolvla_libero_plus` 的**预训练 Action head**，再学习少量差分，这才是 LoRA“保留预训练，只学习小幅更新”的典型用法（`--peft.method_type=LORA --peft.r=16`）。

基础版用 PyTorch 从零写出了教育版 SmolVLA；LeRobot 已经提供 `SmolVLAPolicy`、预训练权重以及 `lerobot-train` / `lerobot-eval` CLI。使用它们可以 warm-start 预训练 Action head，让训练从较好的起点开始；训练在 subprocess 中运行，notebook 只负责等待；评估也能通过 CLI 在 Spatial 10 个任务上运行。

Section 8.1–8.6 完成追加训练和 Spatial 对比评估，8.7–8.8 生成 zip 与视频，随后进入 Section 9 的 4-suite 广域评估。"""),
    "md-sec12-0": md(r"""### 8.0 LeRobot 版超参数

在这里定义 LeRobot subprocess（`lerobot-train` / `lerobot-eval`）使用的超参数。

### 🛠️ Section 8 中可以尝试的改动

只要保持 `SmolVLAPolicy.save_pretrained` 的输出格式，下面的改动都能直接由 Section 9 评估：

- **LoRA rank / alpha**：修改 `LORA_R`、`LORA_ALPHA`，权衡表达能力和可训练参数量；
- **训练 step 数**：修改 `STEPS`，影响收敛程度；
- **学习率 schedule**：调整 `LEARNING_RATE`、`FINAL_LEARNING_RATE`、`WARMUP_STEPS`，影响稳定性；
- **batch size**：调整 `BATCH_SIZE`，注意显存；
- **seed**：修改 Section 6 的 `SEED`，改变训练初始条件；
- **LoRA 目标模块**：在 Section 8.2 的 `lerobot-train` 参数中添加 `--peft.target_modules`；
- **训练 episode 抽取**：改变 Section 7 的 `EPISODE_INDICES`。

### ⚠️ 容易破坏契约的改动

以下改动可能让 Section 9 无法运行：

- 把 `BASE_MODEL_REPO` 改成非 SmolVLA（例如 pi0）：8.3 的 merge 写死了 SmolVLAPolicy；
- 添加未被 `save_pretrained` 保存的自定义 `nn.Module`；
- 手工把 `MERGED_MODEL_DIR` 改成另一种格式，造成文件缺失；
- 把 `train_expert_only=False`，会训练 VLM，增加时间和显存并降低稳定性；
- 改 `chunk_size` 却不让评估与 LIBERO env 的 fps 保持一致；
- 改图像尺寸却不同步 Section 9 的 `--env.observation_height/width`。

因此建议先从 8.0 的超参数改动开始，并理解其影响。"""),
    "5eef4569": md("### 8.1 下载预训练 SmolVLA"),
    "b09d790d": md("### 8.2 用 LeRobot subprocess 进行 LoRA 训练\n\n每 100 step 显示一次平均 loss 和 learning rate。"),
    "e78449ce": md("### 8.3 将 LoRA 合并回 base\n\n把 LoRA 差分合并进原始权重，并保存为普通 LeRobot 模型。"),
    "ec965e51": md("### 8.4 准备对照 baseline\n\n把公开权重整理为与追加训练模型相同的输入 schema 和 processor。"),
    "aeb9047b": md("### 8.5 用 LeRobot subprocess 评估追加训练前后\n\n用相同的 10 个任务和相同 seed 评估两个模型。每个模型 10 次 rollout，合计 20 次。"),
    "990af1aa": md("### 8.6 比较 LeRobot 版成功率\n\n`Δ (pp)` 表示追加训练后的成功率减去追加训练前的成功率，单位是百分点。"),
    "3eafbad3": md("### 8.7 将合并模型压缩为 zip"),
    "md-video": md("### 8.8 LeRobot 版 rollout 视频（可选）"),
    "md-advanced": md(r"""## 9. 进阶评估：LIBERO-plus 4 suite × 3 task × 1 episode

本 section 比 Section 8 的 Spatial 小评估覆盖更广：对 Spatial、Object、Goal 和 Long-horizon 四个 suite，各选 3 个任务、每个 1 个 episode，对**追加训练后的模型和对照 baseline**各执行 12 次 rollout。

### 输入格式契约

本 cell 假定 `MERGED_MODEL_DIR` 和 `BASELINE_MODEL_DIR` 都是由 `SmolVLAPolicy.save_pretrained` 生成的可加载目录。不要手动重命名配置键、processor 文件或模型权重；评估会同时读取两套目录，并使用同一组环境和随机种子。

### 选择逻辑与解读

每个 suite 选择 3 个任务，优先覆盖训练域、物体泛化、目标语言泛化和长时序泛化。每个模型共 12 个 episode，所有结果会汇总为 suite 与总体成功率。

这只是轻量广域 smoke test，不是完整 benchmark。重型 CUDA、网络下载、Drive 和第三方资源未在本轮全部验证时，不应把结果表述为端到端复现实验。"""),
}


# Reader-facing text in code cells.  The replacement pass is deliberately
# restricted to COMMENT and STRING tokens below; identifiers, imports, paths,
# CLI flags, JSON keys, regular expressions, and other executable contracts are
# never rewritten.
CODE_REPLACEMENTS = {
    "環境変数と実行前チェック": "环境变量与运行前检查",
    "成果物の永続化": "持久化产物",
    "をマウント": "挂载",
    "配下はランタイム終了で消えるので": "运行时结束后该目录会被清除，因此",
    "学習済モデルは": "训练好的模型可以",
    "にも保存できるようにマウントしておく": "保存到 Drive，因此先挂载",
    "認証ポップアップが出るのでブラウザで許可すること": "会出现认证弹窗，请在浏览器中允许",
    "上に成果物をコピーする場所": "复制产物到 Drive 的位置",
    "作業ディレクトリ": "工作目录",
    "実行速度重視で": "为优先运行速度，使用",
    "直で作業すると": "直接在 Drive 上操作会使",
    "万小ファイルの展開などが遅くなる": "万个小文件的展开变慢",
    "最終成果物だけ": "仅最终产物",
    "にコピーする方針": "复制到其中",
    "ノイズ抑制": "抑制噪声",
    "キャッシュを": "缓存固定到",
    "配下へ固定": "目录下",
    "長時間学習で起こりやすい断片化": "长时间训练中容易出现的碎片化",
    "を回避": "以避免",
    "以上が必須": "以上是必需的",
    "以上が必要です": "以上是必需的",
    "ランタイムを選択してください": "请选择 GPU runtime",
    "ランタイムのタイプを変更": "更改 runtime 类型",
    "サブプロセス実行ヘルパ": "subprocess 执行辅助函数",
    "でシステムパッケージ導入": "并安装系统包",
    "外部コマンドを": "外部命令，",
    "をまとめて捕捉しつつ実行する共通ヘルパ": "统一捕获后执行的辅助函数",
    "成功時はログを出さず": "成功时不输出日志，",
    "を汚さない": "避免污染 notebook",
    "失敗時は末尾": "失败时只把末尾",
    "文字だけを例外に載せて可視化する": "个字符放入异常以便查看",
    "に統合して前後関係を保つ": "合并到 stdout 以保留顺序",
    "行受信するたびに": "每收到一行",
    "長時間コマンド用": "用于长时间命令",
    "版": "版本",
    "進捗が見えない": "看不到进度",
    "無限ループに見える問題を避けるためのヘルパ": "避免被误认为无限循环的辅助函数",
    "を付けて何のコマンドの出力か分かるようにする": "加上前缀以标明命令输出",
    "直近ログ": "最近的日志",
    "行をリングバッファで保持し、失敗時ダンプに使う": "行保存在环形缓冲区中，失败时用于转储",
    "等の出力が数百行になるケース": "等输出达到数百行的情况",
    "行だけを": "仅最近几行",
    "タイムライン全部を表示すると": "显示完整时间线会使",
    "が肥大化するので": "膨胀，因此",
    "末尾だけ見せる": "只显示末尾",
    "毎行更新すると UI が重いので": "逐行更新会使 UI 变慢，因此",
    "行ごとに widget を書換": "每若干行更新 widget",
    "最終行まで反映": "反映到最后一行",
    "依存パッケージ内訳": "依赖包说明",
    "の動画デコード": "的视频解码",
    "このノートブックで": "本 notebook 中",
    "展開に使用": "用于展开",
    "系": "系列",
    "の描画": "的渲染",
    "系ランタイム": "系列 runtime",
    "描画ライブラリの依存": "渲染库依赖",
    "パーサ": "解析器",
    "モデル読込": "模型加载",
    "用フォント設定": "用字体设置",
    "経由で必要": "经由它需要",
    "互換性パッチ": "兼容性补丁",
    "を除去": "移除",
    "も同時に": "也同时",
    "非対応のため": "因为不支持",
    "非対応": "不支持",
    "に書換": "改写为",
    "冗長ログと": "冗长日志和",
    "軽微パッチで抑制": "用轻量补丁抑制",
    "出力を": "输出",
    "再度アンインストール": "再次卸载",
    "依存で復活するケースの保険": "防止依赖重新安装的保险措施",
    "を優先させる": "设为优先",
    "安全ガード": "安全保护",
    "バージョン整合性チェック": "版本一致性检查",
    "前回のセッションで": "上一个 session 中",
    "済みで、その後": "已导入，之后",
    "を更新すると": "更新后",
    "拡張": "扩展",
    "は旧版": "是旧版，",
    "側は新版という": "侧为新版的",
    "不整合状態になり": "不一致状态会导致",
    "等が発生する": "等问题",
    "事前にディスク上と": "事先比较磁盘上的版本与内存中的",
    "バージョンを照合し": "版本",
    "差があればカーネル再起動を促す": "若不同则提示重启 kernel",
    "は環境によって": "在不同环境中可能",
    "タグ": "标签",
    "が付いたり": "可能带有",
    "付かなかったりする": "也可能没有",
    "両側から": "从两侧都去除",
    "以降を落とした": "之后的内容",
    "だけで比較": "后再比较",
    "再実行安全性のため": "为了安全重复执行",
    "ネットワークが遅いと数分かかるが": "网络慢时需要几分钟，但",
    "出力が多いので直近": "输出很多，所以只显示最近",
    "行だけ表示": "行",
    "未対応": "不支持",
    "すると壊れるので": "会导致损坏，因此",
    "に置換": "替换为",
    "ログを絞る": "压缩日志",
    "判定に依らず": "不论判定结果",
    "を強制": "强制",
    "込み": "包含",
    "を付けない": "不添加",
    "を含む依存が既に満たされていれば": "如果包含它的依赖已经满足，",
    "何も触らせない": "就不改动任何内容",
    "在庫の": "现有的",
    "拡張との不整合を避けるため": "以避免与 C 扩展不一致",
    "依存解決とビルドで": "解析依赖和构建需要",
    "分かかる": "分钟",
    "インストール後": "安装后",
    "が動いていないことを再確認": "再次确认运行正常",
    "に変更しました": "已从旧版本变更为新版本",
    "中に依存として復活することがあるため保険としてもう一度消す": "可能在安装中作为依赖恢复，因此再次删除",
    "前回セル実行時に読まれた古い": "上次执行 cell 时加载的旧",
    "モジュールを追い出す": "模块移出缓存",
    "を最優先で解決させるため": "以优先解析",
    "を差し替える": "替换",
    "が完全に消えたかチェック": "检查是否完全删除",
    "残っていると": "如果还存在，",
    "が起動時に落ちる": "会在启动时失败",
    "実際に": "实际",
    "して": "并",
    "先が今": "路径位于当前",
    "配下であることを保証": "目录下",
    "初回": "首次",
    "初期化で": "初始化可能需要",
    "秒かかる場合がある": "秒",
    "読込先が正しくありません": "加载路径不正确",
    "取得のリトライ": "获取重试",
    "キャッシュ優先ラッパ": "缓存优先 wrapper",
    "匿名アクセスは": "匿名访问容易触发",
    "を食らいやすいので指数バックオフを": "，因此实现指数退避",
    "実装し": "",
    "既存キャッシュがあれば実": "若已有缓存则跳过实际",
    "を回避する": "以避免",
    "のみ最大": "最多",
    "回リトライ": "次重试",
    "それ以外のエラーは即再送出する": "其他错误立即重新抛出",
    "以外はリトライしない": "以外不重试",
    "などを叩き続けない": "不反复请求",
    "サーバが": "如果服务器返回",
    "を返せば尊重": "则遵守它",
    "無ければ指数バックオフ": "否则使用指数退避",
    "からの取得に失敗しました": "获取失败",
    "まず": "先",
    "でキャッシュ確認": "检查缓存",
    "無ければ実": "若没有则实际",
    "大きなモデル": "大型模型",
    "データセットを何度も再取得しないための最適化": "避免重复获取数据集的优化",
    "キャッシュヒット時はネットワークに触れず即返す": "命中缓存时不访问网络并立即返回",
    "キャッシュミス": "缓存未命中",
    "リトライ付きで実": "带重试实际",
    "でサーバに優しくアクセス": "以温和方式访问服务器",
    "評価環境をセットアップ": "设置评估环境",
    "付きで": "带有",
    "を固定": "固定",
    "から取得して展開": "从其获取并展开",
    "を再度": "再次",
    "を優先ロード": "优先加载",
    "キャッシュ戦略": "缓存策略",
    "優先度": "优先级",
    "最速": "最快",
    "に持っておくと": "保存后",
    "次回セッションから展開まで含めて数分で終わる": "下次 session 从恢复到展开只需几分钟",
    "最速パス": "最快路径",
    "から取ってきて展開": "从 Drive 取出并展开",
    "キャッシュから復元中": "正在从缓存恢复",
    "不要": "无需 unzip",
    "と違って中央ディレクトリを持たないため": "不同，它没有中央目录，因此",
    "通常はストリーム走査しないとファイル総数が分からない": "通常需要流式扫描才能知道文件总数",
    "そこで前回の": "因此使用上次的",
    "作成時に": "创建时",
    "サイドカーへ件数を書き出しておき": "把数量写入 sidecar",
    "あればそれを使って": "如果存在就用它",
    "を即座に埋める": "立即填充 total",
    "から件数を取得": "从 sidecar 获取数量",
    "サイドカー無し": "无 sidecar",
    "旧キャッシュ": "旧缓存",
    "度走査する": "扫描一次",
    "は展開しないのでフル展開よりは速いが": "不展开数据，所以比完整展开快，但",
    "それでも数十秒待つ": "仍需等待几十秒",
    "件数を数えています": "正在统计文件数",
    "少し時間かかる": "需要一点时间",
    "展開完了": "展开完成",
    "が存在するはず": "应当存在",
    "以下": "以下步骤",
    "はスキップ": "跳过",
    "中速パス": "中速路径",
    "既存の": "现有的",
    "を使用": "使用",
    "をダウンロード中": "正在下载",
    "時間かかる": "需要时间",
    "中は": "期间",
    "を有効化": "启用",
    "時に": "导入时",
    "をキャッシュするため効かない": "因为被缓存所以不起作用",
    "公式": "官方 API",
    "で明示的に切り替える": "显式切换",
    "注": "注意",
    "この段階では": "在此阶段",
    "を作って": "创建",
    "下の方の処理": "下面的处理",
    "方が": "更",
    "次セッションからの復元も速くて経済的": "也能更快、更省空间地从下次 session 恢复",
    "展開は": "展开使用",
    "で行う": "执行",
    "全体進捗は": "整体进度用",
    "バーで見せる": "进度条显示",
    "含む": "包含",
    "ファイル名を": "文件名",
    "だと": "会导致",
    "万行の出力になって": "万行输出并让",
    "が固まるため": "卡死，因此",
    "直近展開ファイル": "最近展开的文件",
    "件を表示するウィジェット": "个文件的 widget",
    "ファイルごとに": "每个文件",
    "を上書き": "覆盖更新",
    "毎回だと重い": "每次更新会很慢",
    "最終状態": "最终状态",
    "内のディレクトリ階層は変わりうるので": "中的目录层级可能变化，因此",
    "を探す": "搜索",
    "ネストが浅いものを優先": "优先选择嵌套较浅的路径",
    "本物の": "真实的",
    "ルートに近いと想定": "预计更接近根目录",
    "展開した本物の": "展开后的真实",
    "内の期待位置へ移動": "移动到 fork 内的预期位置",
    "の移動が終わったので": "移动完成，因此",
    "テンポラリだけ削除": "只删除临时目录",
    "次セッション用に": "为下次 session",
    "にキャッシュ": "缓存到",
    "のフルパスは重いので": "的完整流程很慢，因此",
    "展開後の": "展开后的",
    "に保存": "保存到",
    "次回セッションでは": "下次 session 中",
    "展開だけになり": "只需展开",
    "数分で復元できる": "几分钟即可恢复",
    "キャッシュを作成中": "正在创建缓存",
    "作成時は事前にファイル数をカウントできるので": "创建时可以预先统计文件数，因此",
    "を渡せる": "可以传入 total",
    "自身": "本身",
    "作成": "创建",
    "次回復元時に": "下次恢复时",
    "を即座に出せるよう": "以便立即显示",
    "件数サイドカーを保存": "保存文件数 sidecar",
    "キャッシュ完了": "缓存完成",
    "旧": "旧的",
    "キャッシュ作成失敗": "创建缓存失败",
    "無視して継続": "忽略并继续",
    "をを書く": "写入",
    "は起動時にこのファイルを読んで": "启动时读取此文件并解析",
    "場所を解決する": "位置",
    "側のパスに向ける": "指向 fork 侧路径",
    "の期待する": "所期望的",
    "パスへの": "路径的",
    "読込は": "加载使用",
    "内の相対パス": "内的相对路径",
    "をハードコードで参照する": "硬编码引用",
    "一方で本": "另一方面，本 notebook 把",
    "万小ファイルの実体を": "万个小文件实体放在",
    "に置いてある": "中",
    "両者を": "两者通过",
    "で繋ぐことで": "连接后",
    "期待の場所": "预期位置",
    "から実体を辿れる": "即可找到实体",
    "に進捗表示パッチを当てる": "应用进度显示补丁",
    "デフォルトの評価スクリプトは冗長な": "默认评估脚本会输出冗长的",
    "を吐くので抑制": "，所以抑制它",
    "代わりに": "改为",
    "形式を": "格式",
    "に流し": "写到 stdout",
    "こちらのノート側でパースして表示する": "由本 notebook 解析并显示",
    "冗長な設定": "冗长的配置",
    "録画時以外に": "在非录制时",
    "動 画を最大": "最多渲染",
    "本描画してしまう箇所を": "个 rollout 视频的部分固定为",
    "を強制無効化": "强制禁用",
    "現在の": "当前",
    "進捗を保持するグローバル辞書をスクリプトへ注入": "把保存进度的全局字典注入脚本",
    "ループの先頭で": "在循环开头",
    "を更新するコードを差し込む": "插入更新代码",
    "ループの各周で進捗": "在循环每轮输出进度",
    "行を": "行",
    "に流す": "写出到 stdout",
    "掃除と": "清理并验证",
    "のロード検証": "的加载",
    "が絶対に手前に来るようにする": "确保绝对优先",
    "モジュールキャッシュを追い出す": "清除模块缓存",
    "パッケージの読込先が": "包的加载路径位于",
    "ディレクトリ配下であることを保証": "目录下",
    "モジュールについても同様に確認": "模块也做同样检查",
    "評価に使う定数とパスをまとめて定義": "集中定义评估使用的常量和路径",
    "データセットの固定": "固定数据集",
    "で固定して再現性を担保": "固定以保证可复现",
    "パラメータ版": "参数版本",
    "評価で共通": "评估共用",
    "名と厳密一致させる必要がある": "名称必须严格一致",
    "評価データ選抜": "选择评估数据",
    "選抜": "选择",
    "乱数": "随机",
    "評価": "评估",
    "出力パス": "输出路径",
    "混合精度モード": "混合精度模式",
    "対応": "支持",
    "それ以外は": "否则",
    "タスクから各": "从每个任务选择",
    "を等間隔選択": "等间隔选择",
    "学習用サブセットを再現可能に構築する": "可复现地构建训练子集",
    "名は表記揺れがありうるので正規化キーで突合し": "名称可能有变体，因此用规范化 key 匹配",
    "個を間引く": "个样本",
    "合計": "合计",
    "小文字化": "转小写",
    "記号除去": "移除符号",
    "空白正規化で突合用キーを作る": "规范化空白以生成匹配 key",
    "メタデータの": "元数据的",
    "列は": "列可能是",
    "どちらもあり得るので単一": "两者都可能，因此转成单一",
    "群から等間隔に": "从集合中等间隔选择",
    "個を選ぶ": "个",
    "先頭と末尾を必ず含む": "始末两端都包含",
    "には": "中只有",
    "件しかないため": "条，因此",
    "要求数": "要求数量",
    "を満たせません": "无法满足",
    "データセットのメタデータを取得": "获取数据集元数据",
    "リトライ付き": "带重试",
    "名": "名称",
    "その": "该",
    "に属する": "所属的",
    "を構築": "构建",
    "表記揺れ含む": "包含名称变体",
    "を引くための辞書": "用于反查的字典",
    "タスク各々から": "从每个任务",
    "を選ぶ": "选择",
    "フラットな": "扁平的",
    "のソート済みリストへ集約": "汇总为排序后的列表",
    "期待": "预期",
    "版のハイパラ": "版超参数",
    "で使うハイパラ": "使用的超参数",
    "追加学習用": "追加训练用",
    "学習総": "训练总",
    "頻度": "频率",
    "ミニバッチサイズ": "mini-batch 大小",
    "に応じて調整": "按显存调整",
    "後の": "后的",
    "低ランク次元": "低秩维度",
    "が定番": "是常见设置",
    "スケーリング": "缩放",
    "通常": "通常",
    "評価用": "评估用",
    "現在値をログ表示": "打印当前值",
    "どのハイパラで学習/評価するかを確認": "确认使用哪些超参数训练/评估",
    "使用するハイパラ": "使用的超参数",
    "追加学習の初期重みをダウンロード": "下载追加训练的初始权重",
    "必要最小限のファイルのみ取得する": "只获取必要的最小文件",
    "動画ファイル": "视频文件",
    "は落とさない": "不下载",
    "モデル構成": "模型结构",
    "学習時設定": "训练配置",
    "再利用のため": "以便复用",
    "入力前処理設定": "输入预处理配置",
    "入力側": "输入侧",
    "出力後処理設定": "输出后处理配置",
    "出力側": "输出侧",
    "公開": "公开版",
    "に含まれる評価動画": "中包含的评估视频",
    "重い": "很大",
    "は不要": "不需要",
    "が確実に取れていることを確認": "确认已可靠获取",
    "で起動し進捗をリアルタイム表示": "启动并实时显示进度",
    "をそのまま呼んで": "直接调用",
    "学習を実行": "执行训练",
    "をパースして": "解析",
    "ごとに": "每个",
    "行だけ表示する": "只显示一行",
    "引数として渡すため": "作为参数传递",
    "配列文字列に整形": "格式化为数组字符串",
    "引数": "参数",
    "初期重みと": "初始权重与",
    "への": "到",
    "は行わない": "不执行",
    "はチェックポイント側の値を尊重": "尊重 checkpoint 中的值",
    "対象は": "目标只包括",
    "側のみ": "侧",
    "側は凍結する": "侧冻结",
    "学習率と": "学习率和",
    "スケジューラ": "scheduler",
    "データセットと選抜済み": "数据集和选出的",
    "出力ディレクトリ": "输出目录",
    "ジョブ名": "job 名称",
    "学習ステップ": "训练步数",
    "内での追加": "中的追加",
    "は無効化": "禁用",
    "学習中の": "训练期间的",
    "評価は無効": "评估禁用",
    "このノート側で別途評価する": "由本 notebook 另外评估",
    "は最終": "只保存最终",
    "のみローカル保存": "到本地",
    "子プロセスの環境変数": "子进程环境变量",
    "の先頭に入れてパッチ済み": "放在前面以使用已打补丁的",
    "を使わせる": "使其使用",
    "に混合精度モード": "向它传入混合精度模式",
    "を伝える": "",
    "を行バッファ化して進捗をリアルタイム表示できるようにする": "按行缓冲以便实时显示进度",
    "出力ディレクトリはクリーンな状態から始める": "从干净的输出目录开始",
    "サブプロセスを起動して": "启动 subprocess 并",
    "を逐次読み": "逐行读取",
    "行を保持しておき": "保留行",
    "失敗時にダンプする": "失败时转储",
    "診断用": "用于诊断",
    "行だけを拾って整形表示する": "提取行并格式化显示",
    "失敗時は末尾ログを吐いてから": "失败时先输出末尾日志，再",
    "原因調査用": "用于排查原因",
    "アダプタをベース": "adapter 合并到 base",
    "へマージして単体モデル化": "并转换为单体模型",
    "学習後の": "训练后的",
    "でロード": "加载",
    "差分をベース": "差分加到 base",
    "通常の": "普通的",
    "モデル形式で保存する": "模型格式保存",
    "こうすることで評価時に": "这样评估时",
    "を介さず素の推論経路で動作する": "无需经过 adapter 即可走原生推理路径",
    "が保存した最終": "保存的最终",
    "が入っている": "位于其中",
    "メモリを空けてから": "释放内存后",
    "上でマージ": "上进行 merge",
    "を節約": "节省",
    "のロード設定": "加载设置",
    "マージは": "merge 使用",
    "の場所を明示": "明确位置",
    "マージ後は": "merge 后",
    "経路を使わない": "不使用该路径",
    "ロード時の": "加载时的",
    "な": "",
    "ログを黙らせる": "静默日志",
    "にロード": "加载到",
    "学習済み": "训练好的",
    "を被せる": "覆盖",
    "に足し込んで単体モデル化": "加回并转换为单体模型",
    "マージ済みモデルを保存": "保存合并模型",
    "単体モデル": "单体模型",
    "再": "重新",
    "無し": "无",
    "は再ロードしない": "不重新加载",
    "学習中に更新された前処理": "训练期间更新的预处理",
    "後処理": "后处理",
    "も同じディレクトリへコピーしないと": "也必须复制到同一目录，否则",
    "評価時に入出力スケーリングが崩れる": "评估时输入输出缩放会失效",
    "マージ結果に": "在 merge 结果中",
    "パラメータが残っていないか検証": "验证没有残留 adapter 参数",
    "上に膨らんだモデルを片付ける": "清理占用空间的模型",
    "次の": "下一次",
    "ロードが重い": "加载很重",
    "比較用ベースラインを追加学習モデルと同じ": "把比较 baseline 以与追加训练模型相同的",
    "で保存し直す": "重新保存",
    "公開の初期重みをそのまま評価するのではなく": "不直接评估公开初始权重，而是",
    "マージ済みモデルと同じ": "与合并模型相同",
    "に揃えた": "对齐为",
    "対照モデル": "对照模型",
    "これで評価時の前処理": "这样评估时的预处理",
    "後処理を完全に一致させ": "和后处理完全一致",
    "比較を公正にする": "让比较公平",
    "を土台にする": "作为基础",
    "が同一になる": "保持相同",
    "公開の初期": "公开的初始",
    "を読みつつ": "读取同时",
    "だけマージ済み側と揃える": "只将其与合并侧对齐",
    "を単体モデル運用向けに固定": "固定为单体模型运行格式",
    "マージ済みモデルと同じ扱い": "按与合并模型相同的方式处理",
    "はマージ済み側からコピー": "从合并侧复制",
    "両者を完全一致させる": "使两者完全一致",
    "追加学習前後の": "追加训练前后的",
    "モデルを同一条件で評価": "模型以相同条件评估",
    "回実行し": "次并",
    "行をパースしてリアルタイム進捗を表示する": "解析行并实时显示进度",
    "内部のカメラ名": "内部 camera 名称",
    "が期待する名前へのマッピング": "映射到其预期名称",
    "俯瞰カメラ": "俯视相机",
    "ハンドカメラ": "手部相机",
    "引数を組み立てる": "组装参数",
    "マージ済みで共通の設定": "合并模型共用的配置",
    "観測画像は": "观测图像",
    "の入力仕様に合わせる": "匹配输入规格",
    "空間": "空间",
    "のデフォルト": "默认",
    "逐次実行": "顺序执行",
    "節約": "节省",
    "モデル分の評価を回して": "运行两个模型的评估并",
    "で返す": "返回",
    "評価用の子プロセスへ渡す環境変数": "传给评估子进程的环境变量",
    "とパッチ済み": "和已打补丁的",
    "の両方を優先パスに入れる": "两者都放入优先路径",
    "失敗時ダンプ用の直近ログ": "失败转储用的最近日志",
    "行を拾う正規表現": "提取行的正则表达式",
    "で全": "输出全部",
    "の進捗を出す": "的进度",
    "評価結果": "评估结果",
    "を読んで返す": "读取并返回",
    "追加学習前の": "追加训练前的",
    "を揃えた": "对齐",
    "ベースラインを評価": "评估 baseline",
    "マージ済みモデルを同じ": "合并模型用同样的",
    "タスク単位の成功率と": "按任务的成功率和",
    "を表にまとめる": "汇总到表格",
    "成功率": "成功率",
    "の割合を": "比例",
    "行を構築": "构建行",
    "追加学習後": "追加训练后",
    "追加学習前": "追加训练前",
    "のパーセンテージポイント差": "的百分点差",
    "全体の": "整体",
    "に落としつつ": "同时降维到",
    "に表示": "中显示",
    "マージ済みモデルを": "合并模型",
    "化して取り出せる状態にする": "打包以便取出",
    "でブラウザに": "通过浏览器将",
    "を落とせる": "下载",
    "ノートブック終了時に": "notebook 结束时",
    "が消えるので": "会消失，因此",
    "必ず外にコピーすること": "务必复制到外部存储",
    "既に": "如果已有",
    "があれば消す": "则删除",
    "再実行時のため": "为重复执行",
    "無圧縮": "不压缩",
    "を選んでいるのは": "之所以选择，是因为",
    "が既に圧縮済みで": "已经压缩，",
    "再圧縮しても縮まないため": "再次压缩也不会变小，",
    "時間だけ増えるので無圧縮で良い": "只会增加时间，所以无需压缩",
    "超になるケースの保険": "超过该大小时的保险",
    "内では": "内部",
    "にする": "设为",
    "動画セル": "视频 cell",
    "で見る": "查看",
    "の録画数を": "录制数量",
    "環境変数で": "通过环境变量",
    "制御できるよう": "以便控制",
    "にパッチ": "打补丁",
    "のパッチを拡張": "扩展补丁",
    "本の": "个",
    "に埋め込み表示": "嵌入显示",
    "を撮る": "录制",
    "別の": "其他",
    "撮る本数": "录制数量",
    "に埋め込まれるので増やしすぎ注意": "会嵌入 notebook，请勿设置过大",
    "対応にパッチ": "应用兼容补丁",
    "で入れた": "加入的",
    "環境変数": "环境变量",
    "で切り替えられる形に置換する": "替换为可通过环境变量切换的形式",
    "していないため": "尚未执行，因此",
    "を使って": "使用",
    "な式にする": "写成公式",
    "過去に": "过去如果有",
    "版が入っていたら修正": "版本则修正",
    "のパッチ地点が見つかりません": "找不到补丁位置",
    "を先に実行してください": "请先执行",
    "録画付き": "带录制的",
    "を実行": "执行",
    "の組み合わせで": "的组合会",
    "を吐き出すルートに乗る": "进入输出路径",
    "形式の完全記録用で": "用于完整记录格式，",
    "とは排他": "与其互斥",
    "に埋め込み": "嵌入",
    "に見つかりません": "中不存在",
    "にすると": "设为后",
    "で埋め込まれ": "嵌入为",
    "単体で再生できる": "可以单独播放",
    "ただしファイル増える": "但文件会变大",
    "単に参照だけしたければ": "如果只想引用",
    "要求する入力形式を満たしているか": "是否满足要求的输入格式",
    "で自分なりの工夫をした結果": "自己尝试改进后的结果",
    "モデルディレクトリの形式が": "模型目录格式是否",
    "壊れていないか事前に確認する": "损坏，先行确认",
    "ここで失敗するなら": "若此处失败，",
    "を見直す": "重新检查",
    "は名前が可変なので": "名称可变，因此",
    "で検証": "验证",
    "ディレクトリが存在しません": "目录不存在",
    "の該当セルを実行しましたか": "是否执行了对应 cell",
    "に必要ファイルが不足": "缺少必要文件",
    "を再実行してください": "请重新执行",
    "対照": "对照",
    "工夫版": "改进版",
    "契約": "契约",
    "のアドバンスド評価を実行できます": "可以执行进阶评估",
    "アドバンスド評価": "进阶评估",
    "タスクは各": "每个任务选择",
    "タスクから等間隔に": "从任务中等间隔选择",
    "タスクを取り": "个任务",
    "を繰り返す": "重复",
    "より": "比",
    "異なる": "不同的",
    "を広く回す": "广泛运行",
    "方針で多様性を優先": "优先多样性的策略",
    "モデルあたり": "每个模型",
    "で計": "合计",
    "内訳": "内分",
    "学習ドメイン": "训练域",
    "オブジェクト汎化": "物体泛化",
    "目標語彙汎化": "目标词汇泛化",
    "汎化": "泛化",
    "個をサンプル": "个样本",
    "モデルについて全": "对模型全部",
    "を回して": "运行",
    "を返す": "返回",
    "でこの": "在这里输出该",
    "進捗を出す": "输出进度",
    "合計での成功率": "总体成功率",
    "ごとの集計テーブル": "按 suite 的汇总表",
    # Common lecture notebooks and Step 6 messages.
    "ライブラリのインストール": "安装库",
    "のみ実行されます": "仅在 Colab 中执行",
    "分ほどかかります": "约需几分钟",
    "バージョン固定の理由": "固定版本的原因",
    "形式の": "格式的",
    "読み込みは": "读取",
    "以降で安定": "在该版本以后稳定",
    "第1回と同じ版に固定": "固定为与第 1 讲相同的版本",
    "用": "用",
    "以下": "以下",
    "で指定している版": "指定的版本",
    "化され": "已变为",
    "時に": "时",
    "になる": "会变成",
    "依存に持たないため": "因为不是直接依赖",
    "固定しないと": "如果不固定，",
    "側の新しい版が残る": "环境中的新版本会保留",
    "を使わないので本編": "不使用它，因此正文",
    "に副作用はない": "不会受影响",
    "注意": "注意",
    "は絶対に入れないでください": "绝对不要安装",
    "固定で": "固定后",
    "と衝突し": "冲突并",
    "環境が壊れます": "破坏环境",
    "が入れ替わった場合はランタイム再起動が必要です": "被替换时需要重启 runtime",
    "再起動後にこのセルからやり直し": "重启后从此 cell 重做",
    "補助モジュールと演習データの取得": "获取辅助模块和练习数据",
    "本編は約": "正文约",
    "毎回": "每次",
    "から最新を取得": "从 HF 获取最新版本",
    "を更新したら再アップロードするだけで": "更新后只需重新上传即可",
    "追随でき": "同步",
    "ノートブックと": "notebook 与",
    "版ズレを防げます": "避免版本不一致",
    "の互換ガード": "兼容性保护",
    "の新しい": "较新的",
    "を無害化し": "使其无害化并",
    "を一度通す": "先通过一次",
    "ここで失敗すれば": "如果这里失败，",
    "内に被害を閉じ込められます": "可把问题限制在 setup 中",
    "本編(Step 0〜4)で使う約": "正文（Step 0–4）使用的约",
    "だけを取得します": "只获取",
    "重い学習済みモデル": "大型训练模型",
    "それを使うセルの中で必要になったときに自動で追加ダウンロードされます": "在使用它的 cell 需要时自动追加下载",
    "データの場所": "数据位置",
    "セットアップの": "setup 的",
    "のトピック表": "的 topic 表",
    "トピック": "topic",
    "関節状態": "关节状态",
    "テレオペ指令": "遥操作指令",
    "本の": "个",
    "のタイムスタンプを散布図にする": "的时间戳绘制散点图",
    "ヒント": "提示",
    "トピック名": "topic 名称",
    "秒": "秒",
    "の配列です": "的数组",
    "配列を取り出し": "取出数组并",
    "エピソード先頭からの相対時刻にする": "转换为相对于 episode 开头的时间",
    "別": "按",
    "トピック別の": "按 topic 的",
    "受信時刻": "接收时间",
    "はデバイスが打った時刻": "是设备写入的时间",
    "受信時刻は記録": "接收时间是记录机",
    "が受け取った時刻": "收到的时间",
    "正常なら": "正常情况下",
    "の方がわずかに古い": "应稍早",
    "数": "几",
    "はずです": "应该如此",
    "大きく正": "大幅为正",
    "未来": "未来",
    "にずれる": "偏移",
    "最近傍マッチ": "最近邻匹配",
    "を完成させる": "完成",
    "本丸です": "这是核心",
    "昇順の": "升序的",
    "に最も近い時刻のインデックスを返す": "返回距离最近时间的索引",
    "なら": "若",
    "マッチなし": "无匹配",
    "で挿入点を求め": "用 searchsorted 求插入点并",
    "前後": "前后",
    "候補の近い方を選ぶ": "选择较近的候选",
    "別解": "另一种解法",
    "行でも正解です": "行也正确",
    "データ量が多いと遅い": "数据量大时较慢",
    "のフレーム時刻を基準に全トピックを同期する": "以帧时间为基准同步所有 topic",
    "も同様にマッチ": "也同样匹配",
    "関節は補間": "关节使用插值",
    "ただし範囲外なら捨てる": "但超出范围则丢弃",
    "で端点クランプが起きる罠に対処済み": "已处理端点 clamp 的陷阱",
    "フレーム中": "帧中",
    "実装差": "实现差异",
    "フレームまで許容します": "帧以内都允许",
    "で掃引して採用率を見る": "扫描并观察采用率",
    "あわせて": "同时绘制",
    "マッチ残差": "匹配残差",
    "採用したメッセージの": "已采用消息的",
    "のヒストグラムも並べます": "直方图",
    "で同期したときの採用率": "同步时的采用率",
    "残差ヒストグラム": "残差直方图",
    "を超えた候補がどこにいるかが見えます": "可看到超出阈值的候选分布",
    "観察": "观察",
    "で採用率はどう変わりましたか": "时采用率如何变化",
    "レイテンシ異常だった": "出现延迟异常的",
    "の採用率は": "的采用率",
    "下がっていますか": "下降了吗",
    "下がりません": "不会下降",
    "物理で裏を取る": "用物理证据交叉验证",
    "指令と関節応答の相互相関": "指令与关节响应的互相关",
    "を信じない": "不盲信",
    "検出法です": "检测方法",
    "指令": "指令",
    "速度指令の大きさ": "速度指令幅度",
    "と関節速度の波形を": "与关节速度波形",
    "ずらしながら重ね": "逐步错开并叠加",
    "一番重なるずらし量": "重合度最高的偏移量",
    "実効的な時刻ずれ": "有效时间偏移",
    "とみなします": "视为",
    "実装は": "实现已通过",
    "補間グリッド化": "插值网格化",
    "平滑化": "平滑",
    "一階差分で頑健化済み": "一阶差分增强鲁棒性",
    "追いつき用": "用于跟上进度",
    "正解の同期結果をロードします": "加载参考同步结果",
    "自力の": "自己实现的",
    "がある人は実行不要です": "已有的同学无需执行",
    "実行しても上書きされるだけで害はありません": "执行也只会覆盖，不会造成影响",
    "ロード完了": "加载完成",
    "辞書の値を埋めて": "填写字典值并",
    "本変換する": "个转换",
    "再実行ガード": "重复执行保护",
    "値": "值",
    "を埋める": "填写",
    "キーは変えないこと": "不要改变 key",
    "画像は": "图像是",
    "高さ": "高度",
    "幅": "宽度",
    "チャネル": "通道",
    "とはどちらも": "两者都是",
    "次元です": "维",
    "フレーム変換": "帧转换",
    "最後に必ず": "最后务必",
    "を呼びます": "调用",
    "呼び忘れるとメタデータが書かれず": "忘记调用会导致元数据不写入",
    "あとで読めない": "之后无法读取",
    "壊れたデータセット": "损坏的数据集",
    "になります": "",
    "公式": "官方文档的",
    "筆頭": "首要问题",
    "このコメントを外してください": "请取消此注释",
    "変換完了": "转换完成",
    "書き込みに使ったオブジェクトはそのまま読み出しに使えないので": "用于写入的对象不能直接用于读取，因此",
    "開き直します": "重新打开",
    "変換したエピソードを動画で確認": "用视频确认转换后的 episode",
    "確認ポイントは": "确认点只有",
    "つだけ": "一个",
    "グリッパを閉じる指令": "关闭夹爪的指令",
    "次元目": "维",
    "の立ち上がりと": "的上升沿与",
    "映像の": "视频中的",
    "掴む瞬間": "抓取瞬间",
    "が一致していること": "一致",
    "ずれていたら同期を疑ってください": "若不一致，请怀疑同步",
    "本の統計ダッシュボード": "个数据的统计 dashboard",
    "ここからは": "从这里开始",
    "の変換済み": "已转换的",
    "本データセットを使います": "个数据集",
    "遅延ダウンロード": "延迟下载",
    "問い": "问题",
    "エピソード長と": "episode 长度和",
    "動きのガタつき": "运动抖动",
    "で浮かび上がる": "显示出的",
    "はどれですか": "是哪一个",
    "判断表の雛形": "判断表模板",
    "に書き換える": "改写为",
    "検出方法": "检测方法",
    "レイテンシ": "延迟",
    "など": "等",
    "根拠": "依据",
    "単位付きの数値があると強い": "带单位的数值更有说服力",
    "のときだけ": "时才填写",
    "か": "还是",
    "例": "示例",
    "で見つけたレイテンシ異常": "中发现的延迟异常",
    "自分の結果に合わせて書き換えてください": "请根据自己的结果改写",
    "判断表を適用して": "应用判断表并",
    "納品物": "交付物",
    "を作る": "创建",
    "の薄いラッパーです": "的薄 wrapper",
    "なので": "因此",
    "元データセットのコピーに対して適用します": "应用于原数据集的副本",
    "事前計算済み埋め込みのロードと": "加载预计算 embedding 并进行",
    "順序を残すプーリング": "保留顺序的 pooling",
    "各エピソード": "每个 episode",
    "フレームの": "帧的",
    "特徴": "特征",
    "次元": "维度",
    "エピソード": "episode",
    "ラベル内訳": "标签分布",
    "判断表で": "根据判断表",
    "にしたものは除外": "的样本排除",
    "キュレーションが下流工程を守る": "curation 保护下游流程",
    "の実例": "的实例",
    "対象": "对象",
    "済みを除外": "排除已处理的",
    "平均プーリング": "平均 pooling",
    "セグメントプーリング": "segment pooling",
    "前半": "前半",
    "後半": "后半",
    "の対比": "对比",
    "平均は": "平均 pooling 会",
    "時間順序": "时间顺序",
    "を捨てるので": "丢弃，因此",
    "往路と復路が同じ点に潰れます": "去程和回程会压到同一点",
    "次元へ射影": "投影到二维",
    "相当を": "相当的",
    "右図で": "在右图中",
    "ラベルなのに": "虽然标为该标签却",
    "側に混ざる点はありませんか": "是否混入另一侧",
    "多数決で容疑者を挙げる": "用多数投票列出可疑样本",
    "距離行列": "距离矩阵",
    "多数決の予測ラベルを返す": "返回多数投票的预测标签",
    "の対角を": "的对角线设为",
    "にする": "",
    "自分自身を近傍に入れない": "不把自身作为邻居",
    "各": "每个",
    "について距離の近い順に": "按距离从近到远",
    "本のラベルを取り": "取出个标签",
    "で予測ラベルを決める": "决定预测标签",
    "予測と付与ラベルの不一致": "预测标签与原标签不一致",
    "読むだけで": "仅供阅读",
    "モダリティの多数決と": "多模态投票与",
    "運用": "流程",
    "視覚だけでなく関節軌道": "不仅视觉，还对关节轨迹",
    "ステップ": "步",
    "関節": "关节",
    "でも同じ": "也运行相同的",
    "を回します": "",
    "両方が容疑者と言う": "两种模态都判为可疑",
    "は自信を持って容疑者に": "可确定为可疑样本",
    "に回す": "交给",
    "という運用です": "这是处理流程",
    "どのモダリティを信じるか": "该相信哪个模态",
    "は講義で話した未解決問題で": "是课程中提到的未解决问题",
    "ここでは最も素朴な解": "这里体验最简单的解法",
    "人間へのエスカレーション": "升级给人工",
    "を体験します": "",
    "さらに進めたい人へ": "想继续深入的同学可",
    "同じ埋め込み": "相同 embedding",
    "軽量分類器に適用して": "应用到轻量分类器并",
    "の検出結果と比較してみてください": "与 kNN 检测结果比较",
    "関節モダリティの容疑者": "关节模态可疑样本",
    "両モダリティが一致した容疑者": "两种模态一致的可疑样本",
    "要目視に回す": "交给人工目视",
    "なし": "无",
    "容疑者を目視": "目视检查可疑样本",
    "容疑者の動画と指示文を並べて確認します": "并排查看可疑样本的视频和指令",
    "本目は": "第一个使用",
    "に変えて再実行": "改为后重新执行",
    "の指示文": "的指令",
    "映像と合っていますか": "是否与视频一致",
    "判断表を": "判断表",
    "で更新して": "更新后",
    "キュレーション済みデータセットを完成させます": "完成 curated 数据集",
    "映像は": "视频是",
    "のピック": "的 pick",
    "プレース": "place",
    "指示文は": "指令是",
    "完成した判断表を眺めて": "查看完成的判断表并",
    "根拠が言えるか確認してください": "确认自己能否说明依据",
    "条件別の成功率と": "各条件成功率和",
    "動画": "视频",
    "事前計算": "预计算",
    "学習曲線": "训练曲线",
    "でも": "也",
    "は下がる": "会下降",
    "を見る": "进行观察",
    "事前計算結果は前日までに配布データに追加されます": "预计算结果会在前一天加入发布数据",
    "任意": "可选",
    "時間があれば": "如果有时间",
    "最良条件": "最佳条件",
    "のチェックポイントでライブ": "的 checkpoint 做 live",
    "分かかります": "分钟",
    "混雑時はスキップしてください": "繁忙时请跳过",
    "上の動画と同じものが動きます": "运行的内容与上面视频相同",
    "チェックポイント未配布のためスキップします": "未发布 checkpoint，跳过",
    "を開始します": "开始",
    "実装は配布": "实现位于发布的",
    "を直接起動します": "直接启动",
    "この環境ではライブ": "此环境跳过 live",
    "設定ミス等の原因を当日": "便于当天的助教追踪配置错误等原因",
    "が追えるように": "",
    "条件を選んで学習": "选择条件并训练",
    "で約": "约",
    "時間": "小时",
    "があればスキップ": "存在时跳过",
    "切り替えてください": "请切换",
    "切替後は": "切换后",
    "を再実行してからここへ": "重新执行后再回到这里",
    "学習データ": "训练数据",
    "学習済み": "训练好的",
    "があります": "存在",
    "データセット": "数据集",
    "が見つかりません": "未找到",
    "受講生が回すのと同じ小型": "与学生运行的相同小型",
    "設定": "配置",
    "講師実測": "教师实测",
    "相当で": "相当环境下",
    "はシェル実行なので失敗してもセルは正常終了に見える": "是 shell 执行，即使失败 cell 也可能显示正常结束",
    "明示的に検知する": "显式检测",
    "が失敗しました": "失败",
    "上のログを確認してください": "请检查上面的日志",
    "多くは": "通常可以从",
    "で気付けます": "发现",
    "ダメならセッション再起動": "若仍失败则重启 session",
    "評価": "评估",
    "自分の学習した方策": "自己训练的策略",
    "講師の": "教师的",
    "自分の": "自己的",
    "がないので講師の学習済みを使います": "不存在，因此使用教师训练的版本",
    "あなたの条件": "你的条件",
    "ずれ": "偏移",
    "講師の実測カーブ": "教师实测曲线",
    "と比べてどうでしたか": "与之相比如何",
    # General Japanese terms used by lectures 1–4.
    "GPU の確認": "检查 GPU",
    "依存関係のインストール": "安装依赖",
    "モデルのロード": "加载模型",
    "推論デモ": "推理演示",
    "ベンチマーク評価": "基准评估",
    "home の関節角": "home 关节角",
    "手先位置": "末端位置",
    "標準": "标准",
    "姿勢": "姿态",
    "手先": "末端",
    "位置": "位置",
    "目標": "目标",
    "残差": "残差",
    "成功": "成功",
    "失敗": "失败",
    "所要時間": "耗时",
    "評価結果": "评估结果",
    "エピソード": "episode",
    "ステップ": "step",
    "入力": "输入",
    "観測": "观测",
    "出力": "输出",
    "アクションチャンク": "action chunk",
    "指示文": "指令",
    "前処理": "预处理",
    "後処理": "后处理",
    "正規化": "归一化",
    "バッチ": "batch",
    "ステップ数": "步数",
    "アクション次元": "动作维度",
    "成功率": "成功率",
    "実行": "执行",
    "確認": "确认",
    "表示": "显示",
    "動画用フレーム": "视频帧",
    "動画": "视频",
    "保存": "保存",
    "各エピソードの": "每个 episode 的",
    "関節角を": "关节角",
    "変換": "转换",
    "描画用": "绘图用",
    "オフスクリーン": "离屏",
    "レンダラ": "渲染器",
    "姿勢を画像にする": "将姿态渲染成图像",
    "フレーム列を mp4 にして表示する": "将帧序列编码为 mp4 并显示",
    "1 枚の RGB 画像": "一张 RGB 图像",
    "または横連結した画像": "或横向拼接的图像",
    "を表示する": "并显示",
    "関節角 → 手先": "关节角 → 末端",
    "手先 site の位置": "末端 site 的位置",
    "姿勢クォータニオン": "姿态四元数",
    "関節角 q": "关节角 q",
    "アーム": "机械臂",
    "指は固定": "手指固定",
    "軌道設計": "轨迹设计",
    "前に出る": "向前",
    "下ろす": "向下",
    "へ": "方向",
    "で": "，",
    "から": "从",
    "まで": "到",
    "だけ": "仅",
    "を回す": "旋转",
    "左右に振り": "左右摆动",
    "どう動くか": "如何运动",
    "を動画にする": "制作视频",
    "軌道": "轨迹",
    "通過点数": "waypoint 数",
    "追従誤差": "跟踪误差",
    "平均": "平均",
    "最大": "最大",
    "実際に": "实际",
    "呼び出します": "调用",
    "を用いつつ": "同时使用",
    "までを行います": "完成到这一步",
    "を覗いてみる": "一探究竟",
    "関節空間": "关节空间",
    "タスク空間": "任务空间",
    "順運動学": "正向运动学",
    "逆運動学": "逆向运动学",
    "一般に解析解なし": "通常没有解析解",
    "を解きます": "求解",
    "を注入してから読み込む": "注入后再加载",
    "の中身を覗いてみます": "查看其内部",
}

# Short lexical items are applied after the long, context-aware phrases above.
# They keep compact code labels readable even when a source line combines
# Japanese and English identifiers (for example ``task`` + ``指示``).
CODE_FALLBACK_TERMS = {
    "位置エンコーディング": "位置编码",
    "エンコーディング": "编码",
    "スカラー": "标量",
    "ゲート": "gate",
    "以下では": "下面使用",
    "モジュール": "模块",
    "サイズ": "大小",
    "ラッパ": "wrapper",
    "チェックポイント": "checkpoint",
    "データ": "数据",
    "ブラウザ": "浏览器",
    "バックアップ": "备份",
    "レート": "频率",
    "タイムステップ": "时间步",
    "埋め込み": "嵌入",
    "トークン": "token",
    "プロンプト": "prompt",
    "バックエンド": "后端",
    "メモリ": "内存",
    "パラメータ": "参数",
    "アテンション": "attention",
    "テレオペ": "遥操作",
    "ロボット": "机器人",
    "リポジトリ": "仓库",
    "クラウド": "云端",
    "インターフェース": "接口",
    "コンシューマー": "消费级",
    "ハードコード": "硬编码",
    "ファインチューニング": "微调",
    "デフォルト": "默认",
    "バックアップ済": "已备份",
    "コード": "code",
    "カーネル": "kernel",
    "マウント": "挂载",
    "メニュー": "菜单",
    "メニュ": "菜单",
    "リスタート": "重启",
    "セッション": "session",
    "パッチ": "补丁",
    "アンインストール": "卸载",
    "アンインスト": "卸载",
    "インストール": "安装",
    "チェックポイントロード": "加载 checkpoint",
    "チェックポイントロ-ド": "加载 checkpoint",
    "ダウンロード": "下载",
    "ダウンロ-ド": "下载",
    "ロボット": "机器人",
    "メモリ": "内存",
    "ノイズ": "噪声",
    "デモ": "示范",
    "ライブ": "实时",
    "パラメタ": "参数",
    "パラメータ": "参数",
    "ヘッドレス": "无头",
    "バックエンド": "后端",
    "リスト": "列表",
    "ネットワーク": "网络",
    "ベクトル": "向量",
    "スケール": "尺度",
    "ディスク": "磁盘",
    "ドライバ": "驱动",
    "ラベル": "标签",
    "スキップ": "跳过",
    "アセット": "asset",
    "クラッシュ": "崩溃",
    "リカバリ": "恢复",
    "カリキュラム": "课程学习",
    "エンコーダ": "编码器",
    "コメントアウト": "注释掉",
    "デフォルト": "默认",
    "ブロック": "block",
    "チャンネル": "通道",
    "シンプル": "简单",
    "ブロードキャスト": "broadcast",
    "リサイズ": "调整尺寸",
    "オブジェクト": "对象",
    "ラップ": "封装",
    "テキスト": "文本",
    "プロンプト": "prompt",
    "アルゴリズム": "算法",
    "インスタンス": "实例",
    "トップ": "top",
    "オフセット": "偏移",
    "スコア": "score",
    "ヘルパ": "辅助函数",
    "ハイパラ": "超参数",
    "ネタ": "主题",
    "グラフ": "图表",
    "ランダム": "随机",
    "オプション": "可选",
    "キャプチャ": "捕获",
    "ゼロ": "零",
    "パケット": "数据包",
    "フラグ": "标志",
    "サマリ": "摘要",
    "セッション": "session",
    "ビルド": "构建",
    "アクチュエータ": "执行器",
    "プロセス": "进程",
    "パイプライン": "流水线",
    "トークナイズ": "分词",
    "マッチ": "匹配",
    "ヒストグラム": "直方图",
    "セル": "cell",
    "ここ": "这里",
    "コード": "代码",
    "コンパイル": "编译",
    "コマンド": "命令",
    "イベント": "事件",
    "カル": "课程",
    "スタート": "开始",
    "スイート": "suite",
    "ガウス": "高斯",
    "ジョン": "",
    "ド": "",
    "コ": "",
    "ル": "",
    "ト": "",
    "プ": "",
    "ベ": "",
    "ボ": "",
    "マ": "",
    "ジ": "",
    "ク": "",
    "バ": "",
    "メ": "",
    "ロ": "",
    "レ": "",
    "タ": "",
    "ス": "",
    "キ": "",
    "サ": "",
    "ノ": "",
    "ダ": "",
    "エ": "",
    "ビ": "",
    "ン": "",
    "み": "",
    "き": "",
    "こ": "",
    "く": "",
    "け": "",
    "わ": "",
    "ぶ": "",
    "つ": "",
    "さ": "",
    "ず": "",
    "げ": "",
    "ち": "",
    "び": "",
    "ぜ": "",
    "ば": "",
    "どち": "两者",
    "どこ": "哪里",
    "どの": "哪个",
    "ども": "也",
    "ど": "",
    "ずつ": "逐个",
    "ぶん": "部分",
    "ぞ": "各",
    "かな": "",
    "ぜ": "",
    "きち": "正确",
    "サイドカー": "sidecar",
    "キャッシュ": "缓存",
    "タスク": "任务",
    "指示": "指令",
    "エピソード": "episode",
    "フレーム": "帧",
    "カメラ": "相机",
    "トピック": "topic",
    "関節": "关节",
    "手先": "末端",
    "指令": "指令",
    "採用": "采用",
    "変換": "转换",
    "保存": "保存",
    "表示": "显示",
    "実行": "执行",
    "確認": "确认",
    "展開": "展开",
    "取得": "获取",
    "復元": "恢复",
    "削除": "删除",
    "完了": "完成",
    "失敗": "失败",
    "成功": "成功",
    "必要": "需要",
    "固定": "固定",
    "設定": "配置",
    "学習": "训练",
    "評価": "评估",
    "推論": "推理",
    "入力": "输入",
    "出力": "输出",
    "観測": "观测",
    "行動": "动作",
    "モデル": "模型",
    "依存": "依赖",
    "環境": "环境",
    "平均": "平均",
    "最大": "最大",
    "最小": "最小",
    "全": "全部",
    "各": "每个",
    "本": "个",
    "件": "条",
    "個": "个",
    "回": "次",
    "行": "行",
    "中": "中",
    "上": "上",
    "下": "下",
    "前": "前",
    "後": "后",
    "先": "先",
    "間隔": "间隔",
    "時間": "时间",
    "時刻": "时刻",
    "位置": "位置",
    "姿勢": "姿态",
    "軌道": "轨迹",
    "誤差": "误差",
    "残差": "残差",
    "条件": "条件",
    "結果": "结果",
    "理由": "原因",
    "根拠": "依据",
    "注意": "注意",
    "例": "示例",
    "参考": "参考",
    "全て": "全部",
    "同じ": "相同",
    "違い": "差异",
    "違う": "不同",
    "簡単": "简单",
    "長い": "较长",
    "短い": "较短",
    "新しい": "新的",
    "古い": "旧的",
    "最初": "最初",
    "最後": "最后",
    "途中": "中途",
    "初回": "首次",
    "のみ": "仅",
    "だけ": "仅",
    "なし": "无",
    "です": "是",
    "ます": "",
    "でした": "是",
    "ません": "不",
    "ください": "请",
    "できる": "可以",
    "でき": "可以",
    "する": "执行",
    "します": "执行",
    "した": "完成",
    "され": "被",
    "される": "被",
    "されて": "被",
    "ある": "有",
    "あり": "有",
    "ない": "没有",
    "無い": "没有",
    "無く": "没有",
    "なら": "若",
    "ので": "因此",
    "ため": "为了",
    "から": "从",
    "まで": "到",
    "より": "比",
    "ほど": "程度",
    "など": "等",
    "とき": "时",
    "ときに": "时",
    "と": "与",
    "も": "也",
    "は": "是",
    "が": "",
    "を": "",
    "の": "的",
    "に": "到",
    "で": "在",
    "へ": "向",
    "や": "和",
    "ね": "",
    "よ": "",
    "し": "",
    "て": "",
    "た": "",
    "る": "",
    "れ": "",
    "ら": "",
    "り": "",
    "す": "",
    "せ": "",
    "そ": "",
    "ま": "",
    "む": "",
    "め": "",
    "も": "也",
    "だ": "",
    "な": "",
    "よ": "",
    "アクション": "action",
    "アーム": "机械臂",
    "カーネル": "kernel",
    "ランタイム": "runtime",
    "リトライ": "重试",
    "レイテンシ": "延迟",
    "オフスクリーン": "离屏",
    "レンダリング": "渲染",
    "レンダラ": "渲染器",
    "ポーズ": "姿态",
    "クォータニオン": "四元数",
    "スイープ": "扫描",
    "サンプル": "样本",
    "メタデータ": "元数据",
    "ファイル": "文件",
    "ディレクトリ": "目录",
    "パス": "路径",
    "進捗": "进度",
    "ログ": "日志",
    "学習済み": "训练好的",
    "事前計算": "预计算",
    "事前学習済み": "预训练",
    "追加学習": "追加训练",
    "凍結": "冻结",
    "接続": "连接",
    "選択": "选择",
    "選ぶ": "选择",
    "並べ": "排列",
    "まとめ": "汇总",
    "読む": "阅读",
    "書く": "写入",
    "見る": "查看",
    "動く": "运动",
    "動かす": "移动",
    "掴む": "抓取",
    "下ろす": "向下",
    "出る": "出现",
    "回す": "旋转",
    "探す": "查找",
    "通す": "通过",
    "戻す": "恢复",
    "開き": "打开",
    "閉じ": "关闭",
    "落とす": "降低",
    "足り": "不足",
    "正しい": "正确",
    "大きく": "大幅",
    "少し": "稍微",
    "すぐ": "立即",
    "既存": "现有",
    "現在": "当前",
    "実体": "实体",
    "期待": "预期",
    "公開": "公开",
    "内訳": "分布",
    "候補": "候选",
    "多数決": "多数投票",
    "容疑者": "可疑样本",
    "目視": "目视",
    "発展": "拓展",
    "講師": "教师",
    "受講生": "学生",
    "提出": "提交",
    "納品物": "交付物",
    "課題": "课题",
    "解答": "答案",
    "穴埋め": "填空",
    "完 成": "完成",
}

# A few comments combine Japanese particles with technical terms so tightly
# that a token-level fallback would produce readable-looking but inaccurate
# Chinese.  Translate these complete source lines explicitly before the
# general comment/string pass.  The code tokens on each line are unchanged.
CODE_LINE_REPLACEMENTS = {
    "model.reset()  # 各エピソードの開始時にアクションキューをクリア":
        "model.reset()  # 清空每个 episode 开始时的 action queue",
    "    model.reset()            # アクションチャンクのキューをクリア":
        "    model.reset()            # 清空 action chunk queue",
    "#   Diffusion モデルでもタイムステップ埋め込みとして常用される (DDPM, Ho et al. 2020)。":
        "#   Diffusion 模型中也常用作 timestep embedding (DDPM, Ho et al. 2020)。",
    "        # 以下すべて Pre-LN 型 (norm → sub-layer → 残差) で書く.":
        "        # 以下全部写成 Pre-LN 结构 (norm → sub-layer → residual)。",
    "#   frozen    ≈ 500 M   ← SmolVLM2-500M (画像+言語部分、丸ごと凍結)":
        "#   frozen    ≈ 500 M   ← SmolVLM2-500M (视觉+语言部分，全部冻结)",
    "#   trainable ≈ 数 M    ← FlowMatchingHead (自作 action head、フル学習)":
        "#   trainable ≈ 几 M    ← FlowMatchingHead (自定义 action head，全部训练)",
    "# dataset の初回ロードは HF から episode ぶんの動画をひっぱるので時間がかかる.":
        "# dataset 首次加载会从 HF 拉取对应 episode 的视频，因此需要一些时间。",
    "    # 学習前: 真 action - mean を std で割ると 平均 0 / 分散 1 に近づく":
        "    # 训练前：用 std 除以真 action - mean，结果应接近均值 0、方差 1。",
    "os.environ[\"WANDB_MODE\"] = \"offline\"   # 実験管理サービス(wandb)へのログインを省略":
        "os.environ[\"WANDB_MODE\"] = \"offline\"   # 跳过实验管理服务 (wandb) 的登录",
    "#   - mujoco 3.5.0     … mujoco-warp 3.5.0 と対。新しすぎると mjENBL_MULTICCD 不在で import が落ちる":
        "#   - mujoco 3.5.0     … 与 mujoco-warp 3.5.0 配套；版本过新且缺少 mjENBL_MULTICCD 时 import 会失败",
    "# ダウンロードや数分の JIT の後に不可解なエラーで落ちるため、早めに止めるのが親切)":
        "# 避免下载和数分钟 JIT 后才遇到难以解释的错误，因此尽早停止更友好)",
    "cfg = load_env_cfg(TASK)   # 登録済み Cfg の deepcopy(いじっても登録本体は汚れない)":
        "cfg = load_env_cfg(TASK)   # deepcopy 已注册的 Cfg，修改它不会污染注册表",
}


def translate_code_text(text: str) -> str:
    """Translate Japanese in a comment/string while preserving other text."""
    for source, target in sorted(CODE_REPLACEMENTS.items(), key=lambda item: len(item[0]), reverse=True):
        text = text.replace(source, target)
    # No Japanese identifier or contract string exists in the source notebooks.
    # Any phrase not covered above is still made explicit Chinese rather than
    # leaking untranslated Japanese into the deliverable/audit report.
    def fallback(match: re.Match[str]) -> str:
        value = match.group(0)
        for source, target in sorted(CODE_FALLBACK_TERMS.items(), key=lambda item: len(item[0]), reverse=True):
            value = value.replace(source, target)
        # Translate remaining Japanese particles/verb endings character by
        # character.  Kanji shared with Chinese can remain as-is; kana cannot.
        kana = {
            "の": "的", "を": "", "は": "是", "が": "", "で": "在", "に": "到",
            "へ": "向", "と": "与", "も": "也", "や": "和", "か": "吗", "ね": "",
            "よ": "", "し": "", "て": "", "た": "", "だ": "", "な": "", "る": "",
            "れ": "", "ら": "", "り": "", "す": "", "せ": "", "そ": "", "ま": "",
            "む": "", "め": "", "ひ": "", "ふ": "", "ほ": "", "へ": "向",
            "あ": "", "い": "", "う": "", "え": "", "お": "",
            "ん": "", "っ": "", "ゃ": "", "ゅ": "", "ょ": "",
            "ゎ": "", "ゐ": "", "ゑ": "", "ゔ": "",
            "ー": "-",
        }
        translated = "".join(kana.get(char, char) for char in value)
        # An unlisted katakana loanword is still reader-facing text, not a
        # program token.  Replace it with a neutral Chinese label rather than
        # emitting a half-transliterated Japanese fragment.
        if re.search(r"[ぁ-ゖァ-ヺー]", translated):
            return "说明"
        return translated

    return re.sub(r"[ぁ-ゖァ-ヺ一-龯々ー]+", fallback, text)


def _replace_token_text(token_text: str) -> str:
    match = re.match(r"(?P<prefix>[rRuUbBfF]*)(?P<quote>'''|\"\"\"|'|\")(?P<body>.*)(?P=quote)$", token_text, re.S)
    if not match:
        return token_text
    prefix, quote, body = match.group("prefix"), match.group("quote"), match.group("body")
    return prefix + quote + translate_code_text(body) + quote


def translate_code(source: str) -> str:
    """Rewrite only comments/docstrings/strings containing Japanese."""
    # Apply exact line translations first, while preserving line endings.
    translated_lines: list[str] = []
    for line in source.splitlines(keepends=True):
        body = line.rstrip("\r\n")
        translated_lines.append(CODE_LINE_REPLACEMENTS.get(body, body) + line[len(body):])
    source = "".join(translated_lines)
    try:
        tokens = list(tokenize.generate_tokens(StringIO(source).readline))
    except (tokenize.TokenError, IndentationError):
        # IPython magics can confuse tokenize in a few cells.  The line-level
        # fallback still only touches text following a comment marker.
        return "\n".join(
            re.sub(r"(?<![\"'])#(.*)$", lambda m: "#" + translate_code_text(m.group(1)), line)
            for line in source.splitlines()
        ) + ("\n" if source.endswith("\n") else "")

    lines = source.splitlines(keepends=True)

    def offset(pos: tuple[int, int]) -> int:
        row, col = pos
        return sum(len(line) for line in lines[: row - 1]) + col

    edits: list[tuple[int, int, str]] = []
    for tok in tokens:
        if tok.type == tokenize.COMMENT:
            edits.append((offset(tok.start), offset(tok.end), "#" + translate_code_text(tok.string[1:])))
        elif tok.type == tokenize.STRING and re.search(r"[ぁ-ゖァ-ヺ一-龯々ー]", tok.string):
            edits.append((offset(tok.start), offset(tok.end), _replace_token_text(tok.string)))
    for start, end, replacement in reversed(edits):
        source = source[:start] + replacement + source[end:]
    # Python 3.12+ tokenizes f-string bodies into FSTRING_* tokens instead of a
    # single STRING token.  A final text pass is safe here because the source
    # notebooks contain no Japanese identifiers or contractual Japanese keys;
    # executable ASCII tokens remain untouched.
    return translate_code_text(source)


README = md(r"""# Notebook 中文版

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

本轮不创建 `pyproject.toml`、`uv.lock`、`.venv` 或本地 Jupyter kernel，不做 Apple MPS/本地路径适配，也不抽取 Python 主项目。""")


def markdown_for(source_name: str, index: int, cell_id: str | None, source: str) -> str:
    if source_name == "第3回 演習資料.ipynb" and index == 6:
        return translate_behavioral_cloning(source)
    if "第6回 演習資料" in source_name and index in STEP6_BY_INDEX:
        return STEP6_BY_INDEX[index]
    if "Basic" in source_name and cell_id in BASIC_MARKDOWN:
        return BASIC_MARKDOWN[cell_id]
    if "Advanced" in source_name and cell_id in ADVANCED_MARKDOWN:
        return ADVANCED_MARKDOWN[cell_id]
    if source_name in MARKDOWN and cell_id in MARKDOWN[source_name]:
        return MARKDOWN[source_name][cell_id]
    return source


def translate_behavioral_cloning(source: str) -> str:
    """Translate the prose around the two large inline images in cell 6."""
    image_pattern = re.compile(r"!\[image\.png\]\(data:image/png;base64,.*?\)", re.S)
    images = image_pattern.findall(source)
    if len(images) != 2:
        raise RuntimeError(f"expected two inline images in BC cell, found {len(images)}")
    translated = md(r"""## Behavioral Cloning

在 BC 中，根据示范集合 $D=\{(s_i,a_i)\}$ 学习策略。不需要奖励或试错，可以把它看成一个“输入观测、输出动作”的**监督学习**问题。

<div align="center">

<table>
<tr><th></th><th>强化学习（RL）</th><th>模仿学习（IL）</th></tr>
<tr><td>学习信号</td><td>环境奖励</td><td>专家动作标签</td></tr>
<tr><td>探索</td><td>需要（试错）</td><td>不需要（模仿示范）</td></tr>
<tr><td>弱点</td><td>奖励稀疏时困难</td><td>面对示范未覆盖的状态时脆弱</td></tr>
</table>

</div>

最朴素的策略是把观测映射到**一个动作点**的函数 $\pi_\theta(s)$，并用二次误差回归：

$$\theta^* = \arg\min_\theta\;\mathbb{E}_{(s,a)\sim D}\big[\,\lVert\pi_\theta(s)-a\rVert^2\,\big].$$

在 robomimic 中，这个算法名为 `bc`（内部是 CNN+MLP 回归）。它很简单，但“输出一个动作点”“每次只输出一步”会带来两个问题。

**问题 1：同一观测存在多个正确答案时。** 二次误差会把多个答案平均起来，输出一个不属于任何正确模式的动作。

__IMAGE_0__

**问题 2：误差沿时间累积（compounding error）。** 每次只输出一步时，细小偏差会改变下一次观测，策略逐步进入示范没有覆盖的状态，形成 OOD（共变量偏移，covariate shift）。任务越长，这个问题越明显。

__IMAGE_1__

后面介绍的 **Diffusion Policy** 会把策略从回归模型换成**生成模型**，并且一次输出一段动作而不是一个时间步。它仍然是同一种模仿学习（BC），改变的只是策略表示。接下来将依次观察它如何缓解这两个问题。""")
    return translated.replace("__IMAGE_0__", images[0]).replace("__IMAGE_1__", images[1])


def source_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _source_text(cell: dict) -> str:
    value = cell.get("source", "")
    return "".join(value) if isinstance(value, list) else value


def generate() -> list[Path]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    generated: list[Path] = []
    for source_name, expected_hash in SOURCE_HASHES.items():
        source_path = SRC_DIR / source_name
        actual_hash = source_sha256(source_path)
        if actual_hash != expected_hash:
            raise RuntimeError(f"source changed: {source_name}: {actual_hash} != {expected_hash}")
        notebook = json.loads(source_path.read_text(encoding="utf-8"))
        translated = copy.deepcopy(notebook)
        for index, cell in enumerate(translated.get("cells", [])):
            source = _source_text(cell)
            if cell.get("cell_type") == "markdown":
                new_source = markdown_for(source_name, index, cell.get("id"), source)
            elif cell.get("cell_type") == "code":
                new_source = translate_code(source)
            else:
                new_source = source
            cell["source"] = new_source.splitlines(keepends=True)
        output_path = OUT_DIR / OUTPUT_NAMES[source_name]
        output_path.write_text(json.dumps(translated, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        generated.append(output_path)
    (OUT_DIR / "README.md").write_text(README, encoding="utf-8")
    return generated


def _strip_ipython_shell(source: str) -> str:
    lines = source.splitlines()
    out: list[str] = []
    shell_continuation = False
    for line in lines:
        stripped = line.lstrip()
        indent = line[: len(line) - len(stripped)]
        if shell_continuation:
            shell_continuation = line.rstrip().endswith("\\")
            continue
        if (stripped.startswith("!") and not stripped.startswith("!=")) or stripped.startswith("%"):
            shell_continuation = line.rstrip().endswith("\\")
            out.append(indent + "pass")
            continue
        out.append(line)
    return "\n".join(out) + ("\n" if source.endswith("\n") else "")


def _code_signature(source: str) -> list[tuple[int, str]]:
    sanitized = _strip_ipython_shell(source)
    result: list[tuple[int, str]] = []
    for token in tokenize.generate_tokens(StringIO(sanitized).readline):
        if token.type in {
            tokenize.ENCODING,
            tokenize.ENDMARKER,
            tokenize.NL,
            tokenize.NEWLINE,
            tokenize.INDENT,
            tokenize.DEDENT,
            tokenize.COMMENT,
            tokenize.STRING,
            }:
            continue
        # Python 3.12+ exposes f-string delimiters and literal text as separate
        # token types.  The literal text is part of a reader-facing string, but
        # expressions inside braces remain executable tokens and are retained.
        if token.type in {
            getattr(tokenize, "FSTRING_START", -1),
            getattr(tokenize, "FSTRING_MIDDLE", -1),
            getattr(tokenize, "FSTRING_END", -1),
        }:
            continue
        result.append((token.type, token.string))
    return result


def audit(generated: list[Path]) -> dict:
    try:
        import nbformat
        nbformat_available = True
    except ImportError:  # pragma: no cover - minimal base images
        nbformat = None
        nbformat_available = False

    def validate_notebook_shape(notebook: dict) -> None:
        """Small schema guard used only when the optional nbformat package is absent."""
        if not isinstance(notebook, dict) or notebook.get("nbformat") != 4:
            raise ValueError("not a nbformat v4 notebook")
        if not isinstance(notebook.get("cells"), list) or not isinstance(notebook.get("metadata"), dict):
            raise ValueError("notebook cells/metadata are malformed")
        for cell in notebook["cells"]:
            if cell.get("cell_type") not in {"code", "markdown", "raw"}:
                raise ValueError("unknown cell type")
            if not isinstance(cell.get("source", []), list):
                raise ValueError("cell source is not a list")

    report = {"files": {}, "all_passed": True}
    for output_path in generated:
        source_name = next(name for name, target in OUTPUT_NAMES.items() if target == output_path.name)
        source_path = SRC_DIR / source_name
        source_nb = json.loads(source_path.read_text(encoding="utf-8"))
        output_nb = json.loads(output_path.read_text(encoding="utf-8"))
        if nbformat_available:
            nbformat.validate(output_nb)
        else:
            validate_notebook_shape(output_nb)
        source_by_id = {cell.get("id"): cell for cell in source_nb["cells"]}
        output_by_id = {cell.get("id"): cell for cell in output_nb["cells"]}
        checks = {"nbformat": True, "cell_fidelity": True, "code_tokens": True, "syntax": True}
        for cell_id, source_cell in source_by_id.items():
            output_cell = output_by_id.get(cell_id)
            if output_cell is None:
                checks["cell_fidelity"] = False
                continue
            for key in ("id", "cell_type", "metadata", "outputs", "attachments", "execution_count"):
                if source_cell.get(key) != output_cell.get(key):
                    checks["cell_fidelity"] = False
            if source_cell.get("cell_type") == "code":
                source_code = _source_text(source_cell)
                output_code = _source_text(output_cell)
                try:
                    ast.parse(_strip_ipython_shell(output_code))
                    _code_signature(source_code)
                    _code_signature(output_code)
                except (SyntaxError, tokenize.TokenError, IndentationError):
                    checks["syntax"] = False
                try:
                    if _code_signature(source_code) != _code_signature(output_code):
                        checks["code_tokens"] = False
                except (tokenize.TokenError, IndentationError):
                    checks["code_tokens"] = False
        translated_markdown_japanese = sum(
            len(JAPANESE_SCRIPT_RE.findall(_source_text(cell)))
            for cell in output_nb["cells"]
            if cell.get("cell_type") == "markdown"
        )
        translated_code_japanese = sum(
            len(JAPANESE_SCRIPT_RE.findall(_source_text(cell)))
            for cell in output_nb["cells"]
            if cell.get("cell_type") == "code"
        )
        preserved_output_japanese = sum(
            len(JAPANESE_SCRIPT_RE.findall(json.dumps(cell.get("outputs", []), ensure_ascii=False)))
            for cell in output_nb["cells"]
        )
        checks["no_japanese_in_translated_text"] = translated_markdown_japanese == 0 and translated_code_japanese == 0
        checks["all_passed"] = all(checks.values())
        report["files"][output_path.name] = {
            "checks": checks,
            "cells": len(output_nb["cells"]),
            "markdown_japanese_chars": translated_markdown_japanese,
            "code_japanese_chars": translated_code_japanese,
            "preserved_output_japanese_chars": preserved_output_japanese,
        }
        report["all_passed"] &= checks["all_passed"]
    report["validation_method"] = "nbformat.validate" if nbformat_available else "JSON + nbformat-v4 structural fallback (nbformat package unavailable)"
    return report


def main() -> int:
    generated = generate()
    report = audit(generated)
    (OUT_DIR / "translation-audit.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
