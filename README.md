# Physical AI 2026｜中文讲义与课程代码

唯一同步仓库：**[huangpenguin/pai2026](https://github.com/huangpenguin/pai2026)**。

中文翻译、知识总结、习题解析和工程代码随 Git 同步。日语原件保留在 Mac 原目录，由 `.gitignore` 排除；服务器不会取得原 PDF、日语习题、日语教学 notebook 或课件截图。

## 从这里开始

| 内容 | 入口 | 同步范围 |
|---|---|---|
| 13 章完整中文讲义 | [讲义目录](notes_zh_sumed_up/README.md) | 中文正文、公式、Mermaid、题目与逐选项解析；不含课件原图 |
| 基础篇中文 notebook | [中文版目录](pai_code_part1/ntbk_zh/README.md) | 8 个现有中文版及翻译工具；日文源 notebook 仅在 Mac |
| 应用篇 1，第 1–6 回 | [代码导航](pai_code_part2_roboops/README.md) | 中文导读、工程源码、配置、测试及英文上游示例；日语教学资料仅在 Mac |
| GAN 中文补充 | [知识说明](matsuokenn-handson/5_gan/docs.md) | 中文说明；日语 PPTX、notebook 仅在 Mac |
| 最终课题 | 预留 `final_project/` | 可在服务器迁入源码；凭据、日志、状态、环境及训练产物保持本地 |

原始课件与习题的文件名、页码继续用于溯源，不表示对应原件随仓库分发。所有习题的中文说明、提示及参考解析均在各章内；参考答案为推导结果，不冒充官方答案。

## 在服务器同步

```bash
git clone https://github.com/huangpenguin/pai2026.git
cd pai2026
# 已有此新版本克隆时：
git pull --ff-only
```

这次已重建不含日语原件的提交历史。如果服务器曾克隆旧版，请保留旧目录作为备份并重新 clone，避免把旧历史合并回同步仓库。

本仓库保存学习资料和源码，不包含 Mac 的 Python 环境、Docker 镜像、Google 凭据或运行中的服务。同步文件不会自动迁移最终课题的环境、容器挂载或外部数据。

## 之后加入最终课题

`final_project/` 不再整体忽略，可用于保存 `final_project/pai_control_public/`。`.env`、密钥、`.venv`、`logs/`、`state/` 与常见训练输出继续忽略，不应提交。

如果最终课题已有自己的 `.git`，先保留其独立仓库与完整备份，再明确采用源码快照、Git subtree 或子模块方式接入。直接把嵌套仓库 `git add` 成 gitlink 不会把项目源码一并上传。课程资料同步不代替项目环境迁移。

## 许可与来源

自编原创说明采用 [CC BY 4.0](LICENSE)，自编工具代码采用 [MIT](LICENSE-CODE)，仅限作者有权授权的部分。第三方代码保留各自许可；课程翻译与改述不因根目录许可而改变原作者权利。范围与已核实的许可信息见 [NOTICE.md](NOTICE.md)。

课程出处、固定源码版本和缺失材料记录见[来源索引](pai_code_part2_roboops/SOURCES.md)。整理与本次同步调整仅做文件及静态检查，没有安装依赖、启动 ROS/Docker、训练或提交课程作业。
