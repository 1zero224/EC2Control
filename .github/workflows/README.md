# GitHub Actions 工作流说明

本项目使用基于 **Conventional Commits** 的自动化版本管理和发布系统。

## 📋 工作流概览

### 1. Build and Package (`build.yml`)
**用途:** 自动构建和打包应用

**触发条件:**
- 推送到 `main` 或 `develop` 分支
- 提交 Pull Request 到 `main`
- 手动触发

**功能:**
- ✅ 自动分析 commit 历史，计算语义化版本号
- ✅ 构建 Windows 可执行文件
- ✅ 上传构建产物（保留 30 天）

### 2. Release (`release.yml`)
**用途:** 创建正式版本发布

**触发条件:**
- 推送 tag（格式：`v1.0` 或 `v1.0.0`）

**功能:**
- ✅ 自动生成 changelog
- ✅ 构建发布版本
- ✅ 创建 GitHub Release
- ✅ 上传发布文件

---

## 🎯 版本号格式

本项目使用 **x.x** 格式的语义化版本：

```
MAJOR.MINOR
  |     |
  |     └─ 新功能、修复、其他变更
  └─────── 破坏性变更
```

**示例:**
- 正式版本：`1.0`, `2.3`, `5.12`
- 开发版本：`1.1-dev.5+abc1234`

---

## 🔄 版本自动递增规则

基于 **Conventional Commits** 规范自动计算版本号：

| Commit 类型 | 示例 | 版本递增 |
|------------|------|---------|
| **BREAKING CHANGE** | `feat!: 重构 API` 或包含 `BREAKING CHANGE` | **MAJOR** +1, MINOR 重置为 0 |
| **feat:** | `feat: 添加暗色主题` | **MINOR** +1 |
| **fix:** | `fix: 修复连接超时` | **MINOR** +1 |
| **其他** | `chore:`, `docs:`, `refactor:` 等 | **MINOR** +1 |

**示例流程:**

```bash
# 当前版本: v1.5

# 提交新功能
git commit -m "feat: 添加实例批量操作"
# → 自动计算为 1.6-dev.1+abc1234

# 提交修复
git commit -m "fix: 修复刷新按钮失效"
# → 自动计算为 1.6-dev.2+def5678

# 创建 tag 发布
git tag v1.6
git push origin v1.6
# → 发布 v1.6，自动生成 changelog
```

---

## 📝 Commit Message 规范

遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

### 基本格式

```
<type>(<scope>): <description>

[可选的详细说明]

[可选的 BREAKING CHANGE 说明]
```

### 常用类型

| 类型 | 说明 | 版本影响 |
|------|-----|---------|
| `feat` | 新功能 | MINOR +1 |
| `fix` | Bug 修复 | MINOR +1 |
| `perf` | 性能优化 | MINOR +1 |
| `refactor` | 重构（不改变功能） | MINOR +1 |
| `docs` | 文档变更 | MINOR +1 |
| `style` | 代码格式调整 | MINOR +1 |
| `test` | 测试相关 | MINOR +1 |
| `chore` | 构建/工具配置 | MINOR +1 |

### 示例

```bash
# 新功能
git commit -m "feat(ui): 添加实例搜索过滤功能"

# 修复
git commit -m "fix(core): 修复 EC2 连接超时问题"

# 破坏性变更（方式一）
git commit -m "feat(api)!: 重构配置文件格式

BREAKING CHANGE: 配置文件从 JSON 改为 TOML 格式"

# 破坏性变更（方式二）
git commit -m "refactor!: 移除已废弃的 legacy API"

# 文档更新
git commit -m "docs: 更新安装说明"

# 性能优化
git commit -m "perf(cache): 优化实例列表缓存策略"
```

---

## 🚀 发布流程

### 方式一：自动发布（推荐）

```bash
# 1. 确保所有改动已提交（使用规范的 commit message）
git add .
git commit -m "feat: 添加新功能"

# 2. 推送到 main 分支
git push origin main
# → 触发构建，自动计算下一个版本号（如 1.6）

# 3. 当准备发布时，创建 tag
git tag v1.6
git push origin v1.6
# → 自动构建、生成 changelog、创建 GitHub Release
```

### 方式二：手动指定版本

```bash
# 直接创建并推送 tag
git tag v2.0
git push origin v2.0
# → 触发发布工作流
```

---

## 📊 Changelog 自动生成

发布时自动分析 commit 历史，生成结构化 changelog：

**生成的分类:**
- 🔥 **破坏性变更** - BREAKING CHANGE
- ✨ **新功能** - feat:
- 🐛 **Bug 修复** - fix:
- 📦 **其他变更** - 其他类型

**示例输出:**

```markdown
## EC2 Control v1.6

### 📦 下载
- [EC2-Control-v1.6-Windows.zip](...)

---

### ✨ 新功能

- 添加实例批量操作 (`abc1234`)
- 支持暗色主题切换 (`def5678`)

### 🐛 Bug 修复

- 修复刷新按钮失效 (`ghi9012`)
- 修复连接超时问题 (`jkl3456`)

---

### 📝 安装说明
...
```

---

## 🛠️ 工作流配置

### 修改版本计算逻辑

编辑 `.github/workflows/build.yml` 的 `Calculate semantic version` 步骤：

```yaml
# 修改递增规则
if ($HAS_BREAKING) {
  $MAJOR += 1
  $MINOR = 0
} elseif ($HAS_FEAT) {
  $MINOR += 1
}
```

### 修改 changelog 生成

编辑 `.github/workflows/release.yml` 的 `Generate changelog` 步骤：

```yaml
# 添加新的 commit 类型识别
if ($msg -match '^custom-type(\(.+\))?:\s*(.+)') {
  $CUSTOM += "- $($matches[2]) (``$hash``)"
}
```

---

## 📌 最佳实践

### ✅ 推荐做法

1. **每次提交都使用规范的 commit message**
2. **小步快跑，频繁提交**
3. **定期发布版本（如每周/每月）**
4. **使用 scope 明确变更范围**
5. **重大变更前充分沟通和测试**

### ❌ 避免做法

1. ~~不使用规范的 commit message~~
2. ~~手动修改版本号~~
3. ~~跳过版本发布~~
4. ~~在 commit message 中使用中文类型（如 `新功能:`）~~
5. ~~修改已推送的 tag~~

---

## 🔍 故障排查

### 版本号计算错误

**问题:** 版本号不符合预期

**解决:**
1. 检查 commit message 是否符合规范
2. 查看 GitHub Actions 日志中的 "Calculate semantic version" 步骤
3. 确认 git tags 是否正确

### 发布失败

**问题:** Release 创建失败

**解决:**
1. 检查 tag 格式是否为 `v*.*` 或 `v*.*.*`
2. 确认 GitHub Actions 有 `contents: write` 权限
3. 查看详细错误日志

### Changelog 内容缺失

**问题:** 某些 commit 未出现在 changelog 中

**解决:**
1. 确认 commit message 格式正确
2. 检查是否为 merge commit（已自动过滤）
3. 查看 "Generate changelog" 步骤的统计输出

---

## 📚 相关资源

- [Conventional Commits 规范](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)
- [GitHub Actions 文档](https://docs.github.com/actions)
- [Flet 打包文档](https://flet.dev/docs/guides/python/packaging)

---

## 🤝 贡献指南

提交 PR 时请确保：

1. ✅ Commit message 遵循 Conventional Commits 规范
2. ✅ 通过所有 CI 检查
3. ✅ 在 PR 描述中说明变更内容

**提示:** 工作流会自动在 PR 中显示预计的版本号递增！
