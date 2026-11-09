# 第 6 回｜Dora 数据流与开源贡献

中文说明、翻译与代码可同步；日语原版教学资料及课件截图仅保留在 Mac 本地。

## Dora 动手实验

第 6 回原始 notebook（Mac 本地：`pai_code_part2_roboops/06_open_source/notebooks/第6回 演習資料.ipynb`）已从 Part 2 外层原样移入，内容包括 timer → doubler → printer、传感器／滤波／监视、多输入与记录节点，以及 alarm 扩展。

Notebook 标注 Google Colab、无需 GPU 或实机；课件 14.pdf · PDF 第 17、20 页提及同一 Dora hands-on，但没有提供直接 Colab 下载链接。本次使用你已经持有的原文件，不从演示标题猜造另一个 notebook。

## 开源贡献练习

新收集 [pai-2026-advance-oss-lecture](pai-2026-advance-oss-lecture/README.md)，来源是 14.pdf · PDF 第 48 页。

- [CONTRIBUTING.md](pai-2026-advance-oss-lecture/CONTRIBUTING.md)：先读贡献流程。
- [participants/README.md](pai-2026-advance-oss-lecture/participants/README.md)：参与者条目格式。
- [tests/test_participants.py](pai-2026-advance-oss-lecture/tests/test_participants.py)：理解数据约束与自动检查。

这与 Dora 的 notebook 是两项不同练习。当前目录保存固定 commit 的源码快照，可本地阅读；若以后真要向上游贡献，应另按原仓库说明 fork/clone。此次没有创建提交、PR 或修改上游。

其他 Dora/OpenArm 等框架入口保留在 [SOURCES](../SOURCES.md)，没有把整个生态复制进课堂代码目录。知识说明见 [第 13 章](../../notes_zh_sumed_up/13_open_source_robotics.md)，测验见 Mac 本地：`homework/13.ipynb`。
