# 第 4 章｜强化学习：从环境反馈到机器人策略

来源：Mac 本地：`pdfs/4.pdf`、Mac 本地：`homework/4.ipynb`。参考答案由题干、课件概念和算法定义推导，并非官方答案。

## 1. 强化学习在机器人中的位置与难点

### 1.1 从示范学习转向环境反馈

> 来源：4.pdf，第 6–14、17 页。

监督学习用标注样本学习输入到输出的映射；无监督学习从数据中找结构；**强化学习**（Reinforcement Learning, RL／強化学習）则让智能体（agent）在环境（environment）中试错，以奖励（reward）为信号改进行动策略（policy／方策）。上一章的行为克隆（BC）把专家给出的动作作为监督标签；RL 不需要逐步的专家动作标签，但需要明确任务目标、环境交互和反馈信号。

RL 在机器人上的角色随任务而异。步行、跑步、平衡等低层周期控制中，课件指出常见路线是 PPO 加大量并行仿真；VLA、Diffusion Policy 等基础策略通常先用大规模示范预训练，再对目标任务做监督微调，之后可用 RL 提升成功率和鲁棒性。因此 RL 有时负责从头学策略，有时负责改进已经较强的初始化策略。

RL 不是“选一个算法跑起来就会成功”。实际难点主要有三类：

1. **局部解**：稀疏或不恰当的奖励会让策略停在容易获得局部奖励、却未完成真实任务的行为上。
2. **学习目标在变化**：Actor-Critic 同时更新策略（Actor）和价值估计器（Critic），一个网络追随另一个网络变化，可能放大学习不稳定。
3. **样本效率有限**：策略梯度通常要靠许多环境交互估计改进方向；如果每次试验都要真实机器人执行，成本和安全风险都很高。课件还把物理模拟器进步、大规模数据采集基础设施和缩放规律列为机器人学习进展的推动因素；其“仿真十年约等于现实十天”是说明加速能力的课件示例。

> 原课件图仅在 Mac 本地：`assets/04/page-11.png`

**PushT** 是把 T 形物体推到目标位置与姿态的操作任务。课件示例把覆盖率（coverage）除以成功阈值后裁剪到 $[0,1]$ 作为奖励：
$$
r=\operatorname{clip}\left(\frac{\mathrm{coverage}}{\mathrm{success\_threshold}},0,1\right).
$$
机器人需要接触、推动、可能离开后再接触物体；物体姿态和接触状态会改变后续行为，因而存在许多自然的失败吸引区。课件借此展示：BC 可以从成功示范中学习一个相对直接的推动动作，而 RL 可能花大量试错时间找到局部改进，Critic 对“哪一步有助于最终覆盖目标”的估计也会随策略变化。

> 原课件图仅在 Mac 本地：`assets/04/page-12.png`

### 1.2 奖励塑形：把目标变成可学习信号

> 来源：4.pdf，第 10、12–14 页。

奖励设计（reward design）把任务目标转换成每步可计算的信号。密集奖励（dense reward）在任务完成前也提供进展方向；成功/失败时才给信号则是稀疏奖励（sparse reward）。密集信号有助于探索，但若每项权重或符号不合理，策略可能优化代理指标而非真实目标。课程的步态奖励代码是一个综合性例子。下方用数学记号重排了课件代码结构；其中范数符号等是伪代码，不能直接当作可运行 Python：

~~~~python
def compute_reward(s):
    # 跟踪期望速度与偏航角速度
    r_task = 1.0 * exp(-||s.cmd_xy - s.v_xy||^2 / sigma) \
           + 0.5 * exp(-(s.cmd_yaw - s.v_yaw)^2 / sigma)

    # 保持身体平稳
    p_body = 2.0 * s.v_z^2 \
           + 0.05 * ||s.w_xy||^2 \
           + 1.0 * ||s.gravity_xy||^2 \
           + 1.0 * (s.height - h_ref)^2

    # 限制力矩、关节速度和动作变化
    p_smooth = 1e-5 * ||s.torque||^2 \
             + 1e-4 * ||s.qd||^2 \
             + 2e-7 * ||s.qd - s.qd_prev||^2 \
             + 0.01 * ||s.a - s.a_prev||^2

    # 鼓励脚离地并惩罚打滑/碰撞
    r_gait = 1.0 * feet_air_time(s)
    p_contact = 0.5 * foot_slip(s) + 1.0 * collision(s)

    reward = r_task + r_gait - p_body - p_smooth - p_contact
    return clip(reward, min=0.0)
~~~~

式中 $s$ 汇总本步状态与指令，$cmd\_xy$ / $cmd\_yaw$ 是期望的平面速度/偏航角速度，$v$ 是实际速度；指数项使误差越小、奖励越接近给定权重。$p_{\rm body}$ 抑制竖直速度、横向角速度、身体倾斜和身高偏差；$p_{\rm smooth}$ 惩罚大力矩、关节高速和动作突变；$p_{\rm contact}$ 惩罚脚滑和非期望碰撞；$r_{\rm gait}$ 鼓励符合步态的腾空时间。$\sigma$ 控制速度误差奖励随误差衰减的尺度。最后裁剪为非负值是课件代码示例的具体选择，不是所有任务的通用规则。

使用 RL 前可以借鉴已有实现并逐步调参：选相近任务的 Isaac Lab、ManiSkill、mjlab、rsl_rl、skrl 或 CleanRL 配置；用课程学习（curriculum）逐渐提高任务难度；提供辅助奖励、目标指令或状态线索降低探索难度；记录训练曲线和策略视频。TensorBoard、Weights & Biases 等工具帮助定位“奖励增长但行为错误”、策略崩溃或 sim-to-real 失效。课件的经验判断是：周期性、每步可评分、可在仿真中重置和并行收集大量经验的任务，通常更适合 RL；这是一种任务特征总结，不是严格定理。

## 2. MDP：把机器人任务写成决策问题

### 2.1 五元组、马尔可夫性与机器人状态

> 来源：4.pdf，第 17–21 页。

强化学习常用**马尔可夫决策过程**（Markov Decision Process, MDP／マルコフ決定過程）描述智能体与环境的交互：
$$
\mathcal M=(\mathcal S,\mathcal A,P,R,\gamma).
$$

> 原课件图仅在 Mac 本地：`assets/04/page-18.png`

| 符号 | 含义 | 机器人例子 |
|---|---|---|
| $\mathcal S$ | 状态空间 | 关节角、关节速度、机身姿态、接触状态 |
| $\mathcal A$ | 行为空间 | 关节力矩、目标关节角、速度指令 |
| $P(s_{t+1}\mid s_t,a_t)$ | 状态转移分布 | 当前状态和动作如何决定下一状态 |
| $R(s_t,a_t)$ | 奖励函数 | 前进速度、姿态稳定、能耗或任务成功 |
| $\gamma\in[0,1)$ | 折扣因子 | 对较远未来奖励的重视程度 |

**马尔可夫性**要求：已知当前状态和当前动作后，未来状态与过去历史条件独立：
$$
P(s_{t+1}\mid s_t,a_t,s_{t-1},a_{t-1},\ldots)
=P(s_{t+1}\mid s_t,a_t).
$$
这是建模假设，不保证任意传感观测天然满足。若“状态”只包含相机图像，而关键速度、接触或隐藏目标信息未纳入，观测可能不足以满足马尔可夫性；实践中可扩展状态或加入历史帧/循环网络。

离散 FrozenLake 例子把 $4\times4$ 网格编号为 $s=0,\ldots,15$，动作是上、下、左、右；课件示意在选定方向附近按概率移动，撞边界则留在原格。格子 $5,7,11,12$ 为洞，进入洞得 $-1$；$15$ 为终点，得 $+1$；其他格奖励为 $0$。这个例子把状态、动作、随机转移和终止目标都显式列出；实际 FrozenLake 的转移概率需以具体环境配置为准。

> 原课件图仅在 Mac 本地：`assets/04/page-20.png`

Ant 四足环境则有连续状态和动作：课件例子把各关节位置/速度及各连杆外力等合为 107 维状态，8 维动作是归一化关节力矩；给定状态和力矩后由模拟器动力学推进，奖励包含前进进度和动态行为代价。维数是课件所用环境配置的例子，不是所有 Ant 版本都固定如此。

### 2.2 回报、折扣与优化目标

> 来源：4.pdf，第 19、22–24 页。

策略 $\pi(a\mid s)$ 在状态 $s$ 下给出动作概率分布。强化学习一般优化从轨迹 $\tau$ 得到的折扣累积回报（return）：
$$
G_t=\sum_{k=0}^{\infty}\gamma^k r_{t+k}.
$$
较小 $\gamma$ 使智能体更关注近期奖励；较大的 $\gamma$ 会赋予远期结果更大权重。持续控制任务常需较大折扣因子，避免策略只追逐立即奖励。若任务有限时结束，回报在终止时停止；实践计算还会用终止标志屏蔽终止状态之后的 bootstrap 项。

目标是求使期望回报最大的策略：
$$
J(\pi)=
\mathbb E_{\tau\sim\pi}\left[
\sum_{t=0}^{\infty}\gamma^t R(s_t,a_t)
\right],
\qquad
\pi^*=\arg\max_\pi J(\pi).
$$
课程的“无人岛脱出”图用三步表达这个闭环：先明确目标，再探索未知环境、收集线索，最后用奖励更新行动规则。图中的食物/出口代表帮助策略估值的正反馈，浪费体力等代价对应负反馈。

> 原课件图仅在 Mac 本地：`assets/04/page-23.png`

### 2.3 状态价值与动作价值

> 来源：4.pdf，第 24–25 页。

**状态价值函数** $V^\pi(s)$ 表示从状态 $s$ 开始、之后一直按策略 $\pi$ 行动的期望回报：
$$
V^\pi(s)=
\mathbb E_\pi\left[
\sum_{k=0}^{\infty}\gamma^k r_{t+k}
\mid s_t=s
\right].
$$
它回答“处于这个状态有多好”。**动作价值函数** $Q^\pi(s,a)$ 则先在 $s$ 执行指定动作 $a$，之后按 $\pi$ 行动：
$$
Q^\pi(s,a)=
\mathbb E_\pi\left[
\sum_{k=0}^{\infty}\gamma^k r_{t+k}
\mid s_t=s,\ a_t=a
\right].
$$
它回答“在这个状态采取这个动作有多好”。若已知最优 $Q^*(s,a)$，离散动作下可取 $a^*=\arg\max_a Q^*(s,a)$。连续动作空间通常不能直接枚举所有动作，因此常用参数化策略（Actor）或优化器来输出动作。

## 3. 从价值关系到常用算法

### 3.1 Bellman 方程、TD 学习与 SARSA / Q-Learning

> 来源：4.pdf，第 25–26 页。

价值函数满足的递归关系称为**Bellman 方程**。对策略 $\pi$：
$$
V^\pi(s_t)=
\mathbb E_\pi[r_t+\gamma V^\pi(s_{t+1})\mid s_t].
$$
其直觉是“现在的价值 = 现在获得的奖励 + 下一状态价值的折扣期望”。**时序差分学习**（Temporal-Difference learning, TD）用单步经验估计右侧，不必等完整 episode 结束：
$$
\delta_t=r_t+\gamma V(s_{t+1})-V(s_t),
\qquad
V(s_t)\leftarrow V(s_t)+\alpha\delta_t.
$$
$\delta_t$ 是 TD 误差，衡量实际一步结果与当前估计的差；$\alpha$ 是学习率。终止转移不应从终止状态继续 bootstrap，常写作
$$
\delta_t=r_t+\gamma(1-d_t)V(s_{t+1})-V(s_t),
$$
其中 $d_t=1$ 表示本步终止。

SARSA 与 Q-Learning 都用一步样本更新 $Q(s,a)$，核心区别是目标中的“下一动作”怎么选：
$$
\begin{aligned}
\text{SARSA:}\quad
Q(s_t,a_t)&\leftarrow Q(s_t,a_t)+\alpha[
r_t+\gamma Q(s_{t+1},a_{t+1})-Q(s_t,a_t)],\\
\text{Q-Learning:}\quad
Q(s_t,a_t)&\leftarrow Q(s_t,a_t)+\alpha[
r_t+\gamma\max_{a'}Q(s_{t+1},a')-Q(s_t,a_t)].
\end{aligned}
$$
SARSA 使用实际策略采样得到的 $a_{t+1}$，故其目标包含探索策略的影响，是 on-policy 更新；Q-Learning 用贪心最优动作的价值作为目标，即使行为策略当时探索了别的动作，也在学习贪心目标，因此是 off-policy。两者的公式、样本和分类见图。

> 原课件图仅在 Mac 本地：`assets/04/page-26.png`

### 3.2 Policy Gradient、REINFORCE 与 Actor-Critic

> 来源：4.pdf，第 27–29 页。

当动作空间连续或难以对每个动作枚举价值时，可用带参数 $\theta$ 的策略网络 $\pi_\theta(a\mid s)$，直接最大化期望回报。**策略梯度**（Policy Gradient）沿目标对参数的梯度上升：
$$
J(\theta)=\mathbb E_{\tau\sim\pi_\theta}
\left[\sum_{t=0}^{\infty}\gamma^t r_t\right],
\qquad
\theta\leftarrow\theta+\alpha\nabla_\theta J(\theta).
$$
策略梯度定理给出一种可由采样估计的形式：
$$
\nabla_\theta J(\theta)=
\mathbb E_{\tau\sim\pi_\theta}
\left[
\sum_t \gamma^t\nabla_\theta\log\pi_\theta(a_t\mid s_t)\,G_t
\right].
$$
这里 $G_t=\sum_{k=t}^{T}\gamma^{k-t}r_k$ 是从时刻 $t$ 起算的折扣回报；由于 $J$ 按整条轨迹折扣，直接写轨迹采样估计时还要保留外层的 $\gamma^t$。若改用折扣状态访问分布，或采用相应的采样权重约定，这个因子可并入期望分布，因此教材也常见不显式写 $\gamma^t$ 的简式；课件第 27 页采用了简写形式。

$\log\pi_\theta$ 的梯度是“提高这个动作概率”的方向，$G_t$ 越大，该动作就越应被强化。

- **REINFORCE** 使用采样到的实际回报 $G_t$ 作权重，简单直接，但长轨迹回报方差大，梯度估计可能忽上忽下。
- **Actor-Critic** 用 Actor 表示策略，用 Critic 学习 $V(s)$ 或 $Q(s,a)$；常以优势函数 $A_t$ 替代高方差回报，显式保留折扣时的轨迹更新写作 $\theta\leftarrow\theta+\alpha\sum_t\gamma^t\nabla_\theta\log\pi_\theta(a_t\mid s_t)A_t$。课件页27写的是单步简式。优势常近似为“该动作比基准预期好多少”，例如 $A_t=Q(s_t,a_t)-V(s_t)$；Critic 可降低梯度方差，但 Actor 和 Critic 的耦合也可能导致训练不稳定。

### 3.3 DQN、TRPO / PPO 与 SAC

> 来源：4.pdf，第 30–34 页。

**DQN**（Deep Q-Network）用神经网络 $Q_\theta(s,a)$ 近似离散动作的价值，因而可处理像图像这样的高维观测。其单步目标和平方损失可写成
$$
y_t=r_t+\gamma(1-d_t)\max_{a'}Q_{\bar\theta}(s_{t+1},a'),
\qquad
L(\theta)=\mathbb E[(y_t-Q_\theta(s_t,a_t))^2].
$$
$\bar\theta$ 是目标网络参数：把目标计算所用网络与当前被更新网络分开，并周期性复制参数，可减缓学习目标快速漂移。经验回放（Experience Replay）把过去的 $(s,a,r,s')$ 存入 Replay Buffer，再随机抽取小批次训练，降低相邻样本高度相关的问题。课件图中的流程是：状态图像进入 Q 网络，网络输出每个离散动作的 Q 值，行为策略选取动作；训练时从 buffer 抽样，用 target network 算目标、按误差更新 Q 网络。

> 原课件图仅在 Mac 本地：`assets/04/page-31.png`

**TRPO**（Trust Region Policy Optimization）约束新旧策略间的 KL 距离，在信赖域内提高代理目标，避免一次更新让策略变化过大。它的约束优化及近似求解通常比 PPO 实现复杂。**PPO**（Proximal Policy Optimization）用概率比裁剪实现更简单的保守更新：
$$
r_t(\theta)=
\frac{\pi_\theta(a_t\mid s_t)}
{\pi_{\theta_{\rm old}}(a_t\mid s_t)},\qquad
L^{\rm CLIP}(\theta)=
\mathbb E_t\!\left[
\min\left(r_t(\theta)A_t,\,
\operatorname{clip}(r_t(\theta),1-\epsilon,1+\epsilon)A_t\right)
\right].
$$
$\pi_{\theta_{\rm old}}$ 是采样数据时的旧策略，$A_t$ 是优势估计，$\epsilon$ 控制概率比裁剪范围。裁剪会限制过大的改进幅度，允许在同一批数据上做多次小步更新；PPO 通常仍是 on-policy，需要周期性收集新 rollout。

> 原课件图仅在 Mac 本地：`assets/04/page-32.png`

**SAC**（Soft Actor-Critic）是 off-policy Actor-Critic。它最大化奖励，同时最大化策略熵，鼓励策略在训练中保留动作多样性：
$$
J(\pi)=\mathbb E_{\tau\sim\pi}
\left[\sum_t\gamma^t
\bigl(r(s_t,a_t)-\alpha\log\pi(a_t\mid s_t)\bigr)\right].
$$
$\alpha$ 是熵温度，控制奖励与随机探索的权衡；随机策略的熵 $-\mathbb E[\log\pi(a\mid s)]$ 越大，鼓励多样行为的项越强。课件的 Critic 和 Actor 目标为
$$
\begin{aligned}
y_t&=r_t+\gamma\left[
\min_i Q_{\bar\theta_i}(s_{t+1},a_{t+1})
-\alpha\log\pi(a_{t+1}\mid s_{t+1})
\right],\\
J_\pi&=\mathbb E_{s\sim D,\,a\sim\pi}
\left[
\alpha\log\pi(a\mid s)-\min_i Q_{\theta_i}(s,a)
\right].
\end{aligned}
$$
其中 $a_{t+1}$ 从新策略采样，双 Critic 取较小估值减轻过估计；训练实现也会通过终止掩码处理 episode 结束。Replay Buffer 允许重用旧样本，通常比只用最新 rollout 的方法更省交互数据，但“样本效率更高”不等于每个环境上一定更快或更优。

> 原课件图仅在 Mac 本地：`assets/04/page-33.png`

## 4. 强化学习的几条独立分类轴

### 4.1 Online / Offline 与 On-Policy / Off-Policy

> 来源：4.pdf，第 29 页。

这些术语回答不同问题，不能混作一个分类：

| 轴 | 区分的问题 | 常见定义 | 课件中的例子 |
|---|---|---|---|
| Online / Offline | 训练时是否继续从环境采集新经验？ | Offline RL 只用预先收集好的固定数据集；online 阶段会和环境继续交互、生成新样本 | Offline：AWR、AWAC、IQL、CQL；online 方法见右两列 |
| On-Policy / Off-Policy | 学习数据来自哪一版行为策略，是否能重用旧数据？ | On-policy 主要用当前/最新策略数据；off-policy 可用与当前策略不同、较旧的数据 | On-policy：REINFORCE、vanilla Policy Gradient、A2C、A3C、TRPO、PPO；off-policy：DQN、SAC、DDPG、TD3 |
| Q-Learning / Actor-Critic / Policy Gradient | 用什么对象表示与更新？ | Q-Learning 学 $Q$；Actor-Critic 同时有策略 Actor 和价值 Critic；Policy Gradient 直接更新 Actor | DQN、SAC、PPO 等各在不同坐标上的位置 |

Offline RL 中的“固定数据”可来自历史机器人示范、旧策略或数据库；它不在训练这一步继续探索环境。AWAC 可先做 offline 预训练，也可再进行 online fine-tuning，因此不要把某个算法永久等同于唯一训练阶段。A3C 常归入 on-policy 算法家族，但异步 worker 可能用稍旧的参数采样，严格说数据并非每一步都来自完全相同的当前参数；这是近似 on-policy 的分类约定。

课件分类图用箭头表示某些经典在线算法经验上常见的数据需求趋势，但不能读成“Q-learning、Actor-Critic、Policy Gradient之间存在普适样本量定理”。这些名称彼此并非互斥：例如 PPO 是 Actor-Critic 结构、Policy Gradient 更新，同时通常按 on-policy 训练；SAC 是 Actor-Critic 结构但 off-policy。具体数据量取决于任务、状态/动作空间、网络、探索方式、并行环境和调参。

> 原课件图仅在 Mac 本地：`assets/04/page-29.png`

### 4.2 Model-Free 与 Model-Based

> 来源：4.pdf，第 35–39 页。

**Model-Free RL** 不显式学习状态转移函数 $P(s'\mid s,a)$ 或奖励模型，而直接用环境数据更新 $V/Q$ 或策略，例如 PPO、SAC、TD3、A3C、DQN。其流程是策略选动作 → 环境返回奖励和次状态 → 记录经验 → 用经验更新策略/价值函数。

**Model-Based RL** 学习或利用可用的环境模型，再用模型预测未来、规划或训练策略。若模型已知（given model），可直接规划；若未知，则根据 $(s,a,s',r)$ 学习转移模型和奖励模型。课件列出的例子包括 PILCO、GPS、Dreamer、PETS。模型有机会减少真实交互次数并显式前瞻，但模型误差会导致规划偏差，且模型结构、优化与不确定性处理会增加复杂度。因此“通常更数据高效”是设计动机/经验倾向，不是每项任务的保证。

~~~mermaid
flowchart LR
  E[环境经验 s,a,r,s′] --> MF[Model-Free<br/>直接更新 V、Q 或策略]
  E --> M["学习转移模型 P(s′|s,a)<br/>和奖励模型 R(s,a)"]
  M --> PLAN[Model-Based<br/>用模型规划或更新策略]
  PLAN --> A[选择后续动作]
  MF --> A
  A --> E
~~~

## 5. 仿真器、RL 软件栈与 sim-to-real

### 5.1 为什么用仿真，以及如何选工具

> 来源：4.pdf，第 41–45 页。

物理仿真器可在不消耗实机寿命的情况下训练/评测策略；可重复环境为算法比较提供统一条件；并行化可让计算机在较短墙钟时间内收集大量 rollout；数字场景也能低成本构造现实中昂贵或危险的情境。课件以“仿真中十年经验约相当于现实十天”作加速示例，这是解释并行采样潜力的课件说法，并非对任一模拟器或任务的通用基准。

仿真器选型需看：底层物理引擎、渲染方式、支持的传感器、刚体/软体/布料/流体等动力学范围、GPU 并行能力和许可/开放程度。课件第42页图示的机器人模拟器包括 Bullet、MuJoCo、SAPIEN、Isaac Gym、Drake、RaiSim、Genesis 等；第44页按应用展示 Isaac Lab、ManiSkill、RLBench、Habitat、OmniGibson 等环境。用途不同：有的重视大量并行与 MDP 训练接口，有的重视视觉渲染和操作评测，有的专门模拟居住环境。

下表保留课件第43页能力比较表中的条目。它是课件制作时的版本快照，适合了解选型维度，不应视为今天所有版本的完整能力矩阵：

| 模拟器 | 课件列出的物理后端 | 渲染 | 传感器（表中举例） | 动力学类型 | GPU并行 | 开源 |
|---|---|---|---|---|---:|---:|
| Isaac Sim | PhysX 5 | Rasterization、Ray Tracing | RGB-D、LiDAR、Force、Effort、IMU、Contact、Proximity | 刚体、软体、布料、流体 | 是 | 否 |
| Isaac Gym | PhysX 5、Flex | Rasterization | RGB-D、Force、Contact | 刚体、软体、布料 | 是 | 否 |
| SAPIEN | PhysX 5、Warp | Rasterization、Ray Tracing | RGB-D、Force、Contact | 刚体、软体、流体 | 是 | 是 |
| PyBullet | Bullet | Rasterization | RGB-D、Force、IMU、Tactile | 刚体、软体、布料 | 否 | 是 |
| MuJoCo | MuJoCo | Rasterization | RGB-D、IMU、Tactile | 刚体、软体、布料 | 图表标有支持/提示标记 | 是 |
| CoppeliaSim | MuJoCo、Bullet、ODE、Newton、Vortex | Rasterization、Ray Tracing | RGB-D、Force、Contact | 刚体、软体、布料 | 否 | 是 |
| Gazebo | Bullet、ODE、DART、Simbody | Rasterization | RGB-D、LiDAR、Force、IMU | 刚体、软体、布料 | 否 | 是 |
| Genesis | Genesis | Rasterization、Ray Tracing | RGB-D、Tactile（课件标注“update soon”） | 刚体、软体、布料、流体 | 是 | 是 |

课件还给出一个渲染速度比较，条件来自图下注释：运行于 Intel Core i9-13900K 和 RTX 4090；PyBullet 一列标注 RTX 3090；IsaacGym 无法把深度、分割和 RGB 渲染解耦，故按三种渲染模式平均报告 FPS。数值如下，**仅代表该课件测量快照，不能直接推断当前版本或不同场景性能**：

| 渲染模式 | SAPIEN Rasterization | IsaacGym Rasterization | IsaacSim Ray Tracing | PyBullet Rasterization | MuJoCo Rasterization |
|---|---:|---:|---:|---:|---:|
| RGB @ FPS | 1175.74 | 1917.32（图中带表情标记） | 182.33 | 258.04（RTX 3090） | 2262.59 |
| Depth @ FPS | 1467.48 | 1917.32（图中带表情标记） | 156.31 | 尚未更新 | 1039.91 |
| Segmentation @ FPS | 1153.03 | 1917.32（图中带表情标记） | 141.08 | 尚未更新 | 320.86 |

### 5.2 Newton、mjlab 和强化学习库的职责

> 来源：4.pdf，第 45–48 页。

课件图示强调仿真基础设施逐渐整合：Newton 将不同物理求解器组合在一个面向机器人仿真的体系内，课件提到 NVIDIA Warp、MuJoCo Warp 与 Disney Research 的 Kamino Engine；Isaac Lab 提供 RL/MDP 模板并整合环境，独立的 mjlab 则以 MuJoCo Warp 后端提供类似的机器人学习基建。**补充解释：**Newton 官方当前项目说明其为基于 NVIDIA Warp 的开源 GPU 物理仿真引擎，主要集成 MuJoCo Warp，并由 Disney Research、Google DeepMind 和 NVIDIA 发起；项目当前称其兼容 MuJoCo Playground 与 Isaac Lab。课程图是一个时间点的生态概览，组件和集成状态会随软件发展变化。[Newton 官方仓库](https://github.com/newton-physics/newton)

强化学习库封装 PPO、SAC 等算法和训练循环；多数库集中于 model-free 方法，model-based 支持相对少。库的选型维度包括支持算法、学习框架（PyTorch/JAX/TensorFlow）、向量化并行、分布式、多智能体、文档和社区。课件第47页比较的是一组特定版本/维护状态：

| 课件比较项 | RL-Games | RSL RL | skrl | Stable-Baselines3 |
|---|---|---|---|---|
| 表中算法 | PPO、SAC、A2C | PPO、Distillation | — | — |
| 向量化训练 | 有 | 有 | 有 | 有 |
| 分布式训练 | 有 | 有 | 有 | 无 |
| 框架 | PyTorch | PyTorch | PyTorch、JAX | PyTorch |
| 多智能体 | PPO | PPO | PPO + 多智能体算法 | 外部项目支持 |
| 文档 | Low | Low | Comprehensive | Extensive |
| 社区 | Small | Small | Small | Large |

课件脚注特别说明，skrl 和 Stable-Baselines3 表外支持的算法很多，细节要以各自官方文档为准；上表不可作为当前版本的选型结论。

一套训练系统通常由七类模块组成：①仿真环境，②经验记忆/回放缓冲区，③策略和价值模型，④探索噪声，⑤学习率调度器，⑥RL agent，⑦训练器。强化学习库通过统一 API 管理算法侧模块；模拟器整合机器人模型、物体模型、场景、控制器、传感器、渲染器和物理引擎。策略输出 actions，模拟器执行控制并返回 observation/reward 与仿真数据；数据反过来更新 agent。图中 agent 内的 Noise、Memories、Scheduler 依次承担探索、存储/采样和学习率变化等职责。

> 原课件图仅在 Mac 本地：`assets/04/page-48.png`

### 5.3 Sim-to-Real 与仿真工程

> 来源：4.pdf，第 49–52 页。

**Sim-to-Real gap** 是仿真和真实机器人之间的差异：视觉侧可能有纹理、光照、背景、相机差异；动力学侧可能有质量、摩擦、刚度、延迟、碰撞和传感噪声差异。结果是仿真中成功的策略在实机上失效。课件展示三类互补的补救思路：

- **Domain Randomization**：训练时在合理范围内随机化物理或视觉参数，让策略适应一族环境，而非只记住一个仿真配置。
- **System Identification**：用实机观测/控制日志估计质量、摩擦、刚度、延迟等，再更新模拟器的参数。
- **Domain Adaptation**：根据实机数据调整表示或策略，使它适应目标域。也可通过提高渲染相似度、把现实重建为仿真场景（Real2Sim）缩小视觉差异。

> 原课件图仅在 Mac 本地：`assets/04/page-50.png`

**补充解释：**视觉重建不等于获得完整的物理模型；Gaussian Splatting 可重建逼真的外观，但接触仿真还需可碰撞几何和物理参数。PolaRiS 项目把 3D Gaussian Splatting 的视觉重建、碰撞网格提取和真实场景评测联系起来；SimFoundry 则研究由视频生成适合仿真与策略评测的场景及其变体。它们是课件页50提到 Real2Sim/Gaussian Splatting方向的研究实例，不代表所有重建管线都自动具备准确的动力学。[PolaRiS 项目与论文入口](https://polaris-evals.github.io/)，[SimFoundry 论文](https://arxiv.org/abs/2606.28276)。

仿真工程要配置质量、摩擦、刚度、阻尼、接触、关节限位等大量参数；模拟器不是现实的完整复制品，目标是保留对任务性能最重要的现象。优先解决影响成功率的差异，必要时结合系统辨识与随机化；一味精确拟合所有参数可能耗费时间却不改善策略。课件的实机例子把参考步态、未适配策略和适配后的步态并排，说明真实试验/适配可暴露仿真中看不到的偏差。

## 6. 用强化学习微调机器人基础策略

### 6.1 VLA 微调流程与普通 RL 的错配

> 来源：4.pdf，第 54–59、61–62 页。

课件给出的基础流程是：

1. **Pretraining**：用多样、大规模离线示范训练通用初始策略。
2. **Supervised Fine-Tuning（SFT）**：用目标任务少量数据做任务适配。
3. **RL Fine-Tuning**：在环境中 rollout、接收奖励并更新策略，追求更高成功率和鲁棒性。

> 原课件图仅在 Mac 本地：`assets/04/page-54.png`

课件用 SimpleVLA-RL 的 LIBERO-Long 曲线举例：一条轨迹的 SFT 基线为 17.3%，完整轨迹 SFT 标注为 86.5%，曲线中的 RL 微调达到约 91.7%，相对单轨迹 SFT 增加 74.4 个百分点（课件同时标注相对增加 430.1%）。这只是该论文及基准配置下的曲线，不应推广成所有 VLA 或任务的固定增益。[SimpleVLA-RL 论文](https://arxiv.org/abs/2509.09674)。

微调的难点包括：

- **模型大、反向传播贵**：策略 rollout、价值估计和梯度反传都会增加 FLOPs 与显存，探索合适超参数又需要多次实验。图中一个前向 VLA backbone 接收 image/text 并输出 action，层数增加时需保存中间激活；只训练 action expert 等参数子模块可减少成本。
- **模仿学习初始化没有 Critic**：VLA 通常从动作示范预训练得到 Actor，却没有与新环境回报匹配的价值函数。Critic 从零开始时早期估值噪声大，可能令 Actor 更新方向不稳定；一种研究路线是先用离线数据学习 Critic，再在线微调。
- **Action chunking 改变时间尺度**：策略一次输出多个控制步，标准 RL 常假设“一次动作对应一个环境步”。如果把 chunk 内的每个去噪/生成步骤都建成 MDP 决策，规划 horizon 会膨胀，哪个 chunk 对最终成功负责也更难归因（credit assignment）。
- **在线 rollout 代价高**：PPO 等可用于 VLA，但通常需大量新交互；仿真能并行收集经验，Sim2Real gap 随之成为约束。课件曲线显示 SimpleVLA-RL 在 LIBERO-Long 的训练成功率随 RL step 上升；策略本身仍须经过规定基准/真实任务的评估，不能只看训练曲线。

### 6.2 Diffusion / Flow Matching 策略的额外挑战

> 来源：4.pdf，第 59–60、62 页。

扩散或 Flow Matching 策略通过多步去噪/积分生成动作序列，密度 $\log\pi(a\mid s)$ 通常不像单次高斯策略那样能直接、廉价地计算，而 PPO、SAC、KL 正则等常用算法会用到策略概率或密度比。把“每一步去噪”当成 RL 的一个决策步，又会把一个环境动作展开成许多内部生成步，拉长 credit assignment horizon、增加计算与内存成本。RL 还可能把原有多峰示范分布推向单个高奖励模式，造成 mode collapse 或损害预训练能力；长 action chunk 则让价值归因与 rollout 收集更重。以上是标准算法与这类生成策略结合时的研究难点，并不意味着不存在可行的专门算法。

> 原课件图仅在 Mac 本地：`assets/04/page-59.png`

### 6.3 可微分模拟器与人形机器人

> 来源：4.pdf，第 60–61 页。

常规 RL 把模拟器当黑盒，靠 rollout 估计价值或策略梯度，通常要较多样本。**可微分模拟器**（differentiable simulator）允许从终端损失沿模拟计算图反向传播到动作或策略参数，因而可直接利用梯度优化轨迹；它与轨迹优化、model-based RL、MPC 有较强联系。若系统包含碰撞、摩擦等非光滑接触，梯度可能不稳定或不代表真实动力学，需要谨慎验证。

> 原课件图仅在 Mac 本地：`assets/04/page-60.png`

人形机器人例子将大规模人体动作/动作捕捉数据转为 key pose 跟踪目标，在仿真中大量运行 RL 学习 whole-body tracking policy，再通过各自的 sim-to-real 技术迁移到实机。课件展示了两组研究工作：[Agile/Human2Humanoid](https://agile.human2humanoid.com/) 与 [ExBody2](https://exbody2.github.io/)；具体目标动作、奖励和迁移方法因论文而异。

### 6.4 课程中的仿真步行练习

> 来源：4.pdf，第 7、67 页。

课件练习目标是在 Unitree G1 的 Unitree-G1-Flat 环境中学习速度跟踪策略：mjlab 提供仿真环境，rsl_rl 提供 PPO 训练；示例以 4096 个并行环境收集 rollout。学习者需要配置观测、奖励、速度命令和终止条件，按 Train → Play 流程训练并回放策略，观察奖励/观测设置如何改变步态。这里仅说明课程练习的学习目标与组件关系，不执行安装、训练或机器人操作。

## 7. 习题：机器人强化学习、算法与仿真

题目中的类别边界有少数是教学简化；以下答案按经典算法定义推导，并在相应选项解释中指出适用范围。

### 7.1 Q1｜机器人 RL 的位置与适用任务

> 来源：homework 4。

**题目：**关于当前机器人学习中的强化学习位置与特点，选择一项错误陈述。

- **(A)** 在步行控制等低层控制中，PPO 加大量并行仿真仍是常见主流路线。
- **(B)** 对 VLA、Diffusion Policy 等机器人基础模型，预训练和模仿学习常是基础，RL 常用于后续提升成功率或鲁棒性。
- **(C)** 不论问题如何，强化学习都是“只要运行算法就能解决”的方法；奖励设计和课程学习的试错几乎不必要。
- **(D)** RL 相对擅长具有周期性、奖励较密集、可大量试错等特征的任务。
- **(E)** 实现时从 Isaac Lab、rsl_rl 等已有库中经过实践打磨的实现出发通常更现实。

**提示：**RL 优化的是被定义出来的奖励，不会自动知道用户真正想要的目标。

**答案：C。**

- **(A) 正确。** 步态等周期任务可在模拟器中重置并运行许多并行环境，PPO 易与这种 rollout 流程配合。这里描述的是常见实践路线，不能理解为所有机器人/步态项目都只用 PPO。
- **(B) 正确。** 大规模示范可先提供可用的初始化策略，SFT 再适配任务，RL 以环境奖励进一步优化。若奖励难定义或在线试验代价过高，也可能不适合直接做 RL 微调。
- **(C) 错误。** 算法只能优化给定目标；奖励遗漏安全性或定义错误会得到“高分但行为不对”的策略。稀疏奖励下还可能找不到成功轨迹，通常需要重新设计奖励、探索课程或辅助信号。
- **(D) 正确。** 周期任务有重复结构，密集奖励提供逐步反馈，模拟器和并行重置能降低每次试错成本。反之，长时程、偶发成功且无法安全大量试验的操作任务往往更难。
- **(E) 正确。** 现有库往往包含并行采样、初始化、归一化、更新周期等实践细节，可作为可复现的起点。仍需核对它们的任务假设、版本和环境接口，不能把库默认设置视作对所有机器人都适用。

### 7.2 Q2｜价值函数、Bellman 方程与 TD

> 来源：homework 4。

**题目：**关于价值函数、Bellman 方程和 TD 学习，选择一项错误陈述。

- **(A)** 状态价值函数 $V^\pi(s)$ 是从状态 $s$ 按策略 $\pi$ 行动所得期望回报，表示“处于该状态有多好”。
- **(B)** 行为价值函数 $Q^\pi(s,a)$ 是在状态 $s$ 先执行 $a$、之后按 $\pi$ 行动的期望回报。
- **(C)** Bellman 方程写出“现在价值 = 当前奖励 + 后继状态价值”的递归关系。
- **(D)** TD 学习必须等待 episode 结束并取得真实完整回报，不能依靠单步经验更新。
- **(E)** TD 学习可用 $\delta_t=r_t+\gamma V(s_{t+1})-V(s_t)$ 更新 $V(s_t)\leftarrow V(s_t)+\alpha\delta_t$。

**提示：**区分 Monte Carlo 等完整回报估计与 TD 的 bootstrap 目标。

**答案：D。**

- **(A) 正确。** $V^\pi(s)$ 把未来奖励对当前状态求期望，因此是衡量状态长期价值的函数。期望同时对策略动作和环境转移的不确定性取平均。
- **(B) 正确。** $Q^\pi$ 固定当前第一个动作，再对之后按 $\pi$ 执行的回报取期望。改变首步动作可能改变后续状态，所以 $Q(s,a)$ 可用于比较当前候选动作。
- **(C) 正确。** Bellman 关系把整段未来回报拆成当前一步和余下部分的价值，并以 $\gamma$ 折扣后续项。随机环境下等式包含对奖励与下一状态的条件期望。
- **(D) 错误。** TD 用实际一步奖励和估计的下一状态价值构造 bootstrap 目标，可以不等 episode 结束就更新。等待完整 episode 的回报是 Monte Carlo 风格的目标，不是 TD 必要条件。
- **(E) 正确。** $\delta_t$ 是单步目标与当前估值的差，$\alpha$ 控制每次修正幅度。若本步进入终止状态，下一状态价值应屏蔽；题目省略终止标志是简化写法。

### 7.3 Q3｜Offline / On-Policy / Off-Policy 分类

> 来源：homework 4。

**题目：**关于 model-free 强化学习的分类，选择一项错误陈述。

- **(A)** Offline RL 不在该训练阶段继续靠探索采集数据，只用预先给定数据集训练（如 AWR、AWAC、IQL、CQL）。
- **(B)** Off-Policy RL 可通过 Replay Buffer 重用过去探索数据，例如 DQN、SAC、DDPG、TD3。
- **(C)** On-Policy RL 使用当前策略收集的数据，例如 REINFORCE、A2C、A3C。
- **(D)** 学习所需在线数据量会沿 Q-Learning → Actor-Critic → Policy Gradient 的顺序逐渐减少。
- **(E)** PPO、TRPO 可归入 Actor-Critic 结构，通常放在 On-Policy 一侧。

**提示：**算法结构、数据来源和是否在线交互是不同分类轴；比较样本需求也需固定任务和实现。

**答案：D（按题目预期）。**该项把课件图中的经验箭头误当成普适排名；不同分类轴并不定义通用样本效率顺序。另有细节：AWAC 可离线预训练后继续在线微调；A3C 的异步 worker 可能带来参数滞后，因此“只用当前策略”是对其 on-policy 属性的近似归类。

- **(A) 基本正确。** Offline RL 的特征是在这段训练中使用固定经验数据，不再为每个梯度更新新采集环境轨迹。AWAC 等算法可用于离线初始化并转入在线阶段，但那是训练范式的扩展，不改变“offline 阶段”的定义。
- **(B) 正确。** Off-policy 学习允许行为策略和目标策略不同，旧样本可经回放缓冲区反复使用。DDPG、TD3、SAC 是连续控制中典型例子；回放并不会自动消除数据分布偏移或估值偏差。
- **(C) 教学上正确但需限定。** REINFORCE、A2C 通常按 on-policy 算法讲授；A3C 的多个异步 actor 可能用略旧参数采样，故不是严格的“同一时刻当前策略”数据。实践分类通常仍把 A3C 放在近似 on-policy 一侧。
- **(D) 错误。** Q-learning、Actor-Critic 和 Policy Gradient 并非相互排斥的算法分类；PPO 本身就是策略梯度目标和 Actor-Critic 价值估计的组合。样本需求取决于任务、动作空间、数据复用、并行度和调参，不能由箭头推出普适顺序。
- **(E) 正确。** PPO/TRPO 优化参数化策略，也通常用 Critic 估计优势，符合常见 Actor-Critic 结构；它们通常从当前策略采集数据再更新。Actor-Critic 结构并不意味着 off-policy，SAC 就是反例。

### 7.4 Q4｜Model-Free 与 Model-Based

> 来源：homework 4。

**题目：**关于 Model-Free RL 与 Model-Based RL，选择一项错误陈述。

- **(A)** Model-Free 方法（如 PPO、SAC、DQN）不显式持有状态转移或奖励模型，而用环境数据学习价值函数/策略。
- **(B)** Model-Based 方法（如 Dreamer、PETS）学习状态转移模型或奖励模型，并据此规划或学习策略。
- **(C)** Model-Free 从经验直接更新价值/策略，Model-Based 从经验建模后再利用模型获得价值/策略。
- **(D)** Model-Based 可以显式考虑未来，但通常也需要处理更复杂优化和模型化知识。
- **(E)** 从数据效率看，Model-Free 通常比 Model-Based 需要更少数据；Model-Based 需要大量数据是其一般缺点。

**提示：**模型学习/规划的动机之一正是提高交互数据利用率，但错误模型会造成偏差。

**答案：E。**

- **(A) 正确。** 以课件采用的宽泛定义，Model-Free 不单独学习可供规划的完整环境转移/奖励模型，而直接更新策略或价值函数。它仍会使用采样得到的 $s',r$，这不等于显式持有环境模型。
- **(B) 正确。** Model-Based 方法预测动作如何改变状态，必要时还学习奖励，再用模型做规划或更新策略。Dreamer、PETS 都属于常见模型学习/利用路线，但具体模型结构不同。
- **(C) 正确。** 两者的关键差异在于是否把显式环境模型放入学习和决策链条。Model-Free 也会使用 Bellman bootstrapping，但并不因此自动变成 Model-Based。
- **(D) 正确。** 预测未来有助于重用数据或进行规划；代价是模型误差会影响预测，优化过程也可能更复杂。模型结构与先验知识需求因算法而异。
- **(E) 错误。** Model-Based 的常见动机是用可学习的动力学模型更有效利用交互数据，并非一般需要更多数据。它可能因模型偏差、复杂优化或现实系统建模难而表现较差，但这与“通常比 Model-Free 更费数据”不是同一结论。

### 7.5 Q5｜VLA 上的 RL Fine-Tuning 难点

> 来源：homework 4。

**题目：**关于机器人基础模型 VLA 的 RL 微调难点，选择一项错误陈述。

- **(A)** 常见流程是大规模预训练获得初始化策略、小规模 SFT 适配目标任务、再用 RL 提升成功率和鲁棒性。
- **(B)** VLA 规模大，反向传播计算开销高；寻找 RL 配置需要多次实验，因而较难反复运行。
- **(C)** 许多 VLA 以模仿学习预训练、没有已训练 Critic，从零学 Critic 可能不稳定。
- **(D)** VLA 一开始就有预训练 Critic，可直接套标准 Actor-Critic，而且只需很少 Online RL rollout。
- **(E)** Action Chunking 一次输出多步动作，会让 credit assignment 和价值估计变难。

**提示：**示范动作预训练出的 Actor 不自动包含针对目标任务奖励训练过的 Critic。

**答案：D。**

- **(A) 正确。** 先在大规模示范上学习通用动作，再用少量目标数据适配，最后用奖励信号做交互优化，是课件介绍的常见研究流程。它不是唯一流程；数据、奖励和部署条件会改变采用的训练阶段。
- **(B) 正确。** 大模型前向/反向、保存激活、策略 rollout 和价值估计都会占用算力与显存；不同 RL 超参数又需实验搜索。只训练动作专家或部分参数可降低负担，但不能消除 rollout 成本。
- **(C) 正确。** 模仿学习通常教 Actor 复现示范动作，不提供“这个动作对最终奖励的长期贡献”标签。Critic 从零学习时估值会先很不准，可能导致策略梯度噪声大或更新不稳。
- **(D) 错误。** 预训练 VLA 通常有动作策略，却不默认带一个对目标奖励校准好的 Critic；在线 fine-tuning 也常需大量采样。标准 Actor-Critic 可作为方法起点，但需处理模型大小、生成策略、动作块、价值估计与仿真现实差异。
- **(E) 正确。** 如果一次决策执行很长的动作块，奖励要归因到块内哪个动作就更困难；标准每步更新的 MDP 时间尺度也不再直接对应策略输出频率。长块能减少决策次数，但会减慢对新观测的反馈并增加价值估计负担。
