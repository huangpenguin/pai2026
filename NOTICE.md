# 来源与许可范围

Copyright © 2026 huangpenguin，限本仓库作者拥有或有权授权的原创部分。

## 自编内容

根目录 `LICENSE`（CC BY 4.0）仅适用于作者有权授权的原创中文补充解释、推导说明、导航文字和原创 Mermaid 图。引用或翻译课程材料的部分仍受原作者权利约束；中文翻译、归纳及公开托管本身不改变原有权利。

根目录 `LICENSE-CODE`（MIT）仅适用于本仓库作者有权授权的自编工具代码，例如 `pai_code_part1/scripts/translate_notebooks.py`。第三方工程代码、课程代码、数据和模型不适用这一根目录许可。

复用自编文档可注明：huangpenguin, pai2026, https://github.com/huangpenguin/pai2026, CC BY 4.0，并说明修改。

## 课程材料

中文资料参考东京大学松尾・岩澤研究室的 Physical AI 2026 基础篇、应用篇 1，以及相关论文与官方文档；第 11 章亦对照 2025 版。章节保留来源文件名、页码与引用链接，用于学习溯源。材料经过 AI 辅助翻译、整理和扩写，不是官方教材，也不代表讲师或上游项目意见。

原日语 PDF、教学 notebook、习题原件、课件截图和日语说明通过 `.gitignore` 留在 Mac，本仓库当前历史不分发这些文件。课件包含“未经许可禁止拍摄或向第三方披露”的说明；本仓库的许可不能代替课程方授权，也不对课程衍生内容授予超出作者权利的许可。

## 第三方代码

- `pai_code_part2_roboops/04_ros2_pubsub/physicalai_pubsub/` 保留其 MIT LICENSE。
- `physicalai_teleop` 在 `package.xml` 与 `setup.py` 声明 MIT；无独立 LICENSE 文件，不应误写为无许可声明。
- `pai_training/lerobot/`、Hugging Face 上游示例，以及第 6 回 OSS 示例仓库保留各自 Apache-2.0 LICENSE。内层 LeRobot 的许可不自动覆盖 `pai_training` 外层。
- `smolvla_ros2` 中 `franka_vla_sim` 子包声明 Apache-2.0，该声明不自动覆盖父目录所有文件。
- 其余未发现明确许可的课程代码或材料仍保留原有权利，不因放入本仓库就变为 MIT、Apache-2.0 或 CC BY 4.0。

再利用第三方内容时应核对具体子目录、文件头、LICENSE、NOTICE 及对应版本。上游与固定版本的记录见 `pai_code_part2_roboops/SOURCES.md` 和 `sources.lock.json`；这些记录也包含只在 Mac 保存的课程原件信息，不表示所有原件随 Git 分发。
