# 第 2 回｜PushT RoboOps 实践

这里是原 `pai_code_part2_roboops/1/` 项目。第 3 回课件 10.pdf · PDF 第 2、52、60、93、104 页明确回顾“第 2 回 PushT Notebook／Docker 配置”，并展示 Compose、`uv.lock`、数据验证等；与本项目内容对应，因此按第 2 回归档。

中文说明、翻译与代码可同步；日语原版教学资料及课件截图仅保留在 Mac 本地。

## 从这里读起

1. [原始 README（日文）](README.md)：项目整体与 Docker 入口。
2. [原始课前准备](PREPARATION.md)：账户、Docker 和 Git 准备。
3. Mac 本地：`pai_code_part2_roboops/02_robops_workshop/notebooks/01_roboops_workshop.ipynb`：数据 → 验证 → 学习 → 仿真评估 → 自动化。
4. [下载](src/download_dataset.py)、[验证](src/validate_dataset.py)、[训练](src/train.py)、[评估](src/eval.py)脚本：查看 notebook 对应的可复用实现。
5. [测试](tests/)、[训练配置](configs/train_ci.yaml)、[评估配置](configs/eval_ci.yaml)、[CI](.github/workflows/ci.yml)。

原来散在 Part 2 外层的 `.github/` 与 `.dockerignore` 已放回本项目根目录，原内容不变；这样 README 所述的 Dockerfile、Compose、CI 与源码处于同一项目下。`.gitignore` 也复制到项目根目录。若日后单独将本目录作为 GitHub 仓库，CI 文件应位于这个仓库根部的 `.github/workflows/`；本次未创建仓库或触发 CI。

> **原项目启动方式，仅作阅读，未执行：**在本目录而非 Part 2 总目录运行 `docker compose up --build`，预期提供 notebook 的 JupyterLab。实际依赖、端口及停止方法以原始 README 为准。

本回没有独立 PDF；[第 09 章中文讲义](../../notes_zh_sumed_up/09_robops_practice.md) 是依据本回习题拓展的知识资料。`homework/9.ipynb` 是确认测验，不是这里的项目 notebook。
