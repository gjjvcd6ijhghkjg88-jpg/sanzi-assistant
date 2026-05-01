# Git 协作规范

<!-- 作用：定义 main 分支管理、功能分支命名、PR 合并和代码审核规则。 -->

## 分支策略

- `main`：稳定分支，只接收通过审核的 PR。
- `feat/project-init`：项目初始化、架构文档、公共配置。
- `feat/pc-ui`：PC 端页面和交互。
- `feat/mobile-ui`：移动端布局和信息流。
- `feat/knowledge-graph`：知识库整合、知识图谱和检索能力。

## 日常流程

```powershell
git checkout main
git pull origin main
git checkout -b feat/你的功能名
```

开发完成后：

```powershell
git status
git add .
git commit -m "feat: 完成某某功能"
git push origin feat/你的功能名
```

然后发起 Pull Request 到 `main`。

## PR 审核标准

- 后端接口能启动，`/api/health` 正常。
- 前端页面能启动，问答流程可点击可返回。
- 新增文件有说明性注释或文档说明。
- 不提交 `.env`、`node_modules`、`.venv`、构建产物。
- 修改公共接口时，同步更新 `docs/ARCHITECTURE.md` 或接口文档。

## main 分支管理建议

成员 A 负责：

- 合并 PR 前检查冲突和运行状态。
- 控制公共目录改动，避免成员互相覆盖。
- 每次合并后通知其他成员从 `main` 同步。
- 保持 `README.md` 和 `docs/` 与代码一致。

