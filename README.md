# AWS EC2 实例管理器

一个基于 Python Flet 和 Boto3 构建的 AWS EC2 实例管理桌面应用程序，提供简洁易用的图形界面来管理 EC2 实例的启动和停止。

## 功能特性

✅ **多区域自动扫描** - 自动扫描所有 AWS 区域的实例
✅ **智能区域筛选** - 按区域筛选实例，显示每个区域的实例数量
✅ **启动/停止实例** - 一键启动或停止实例，按钮根据状态智能切换
✅ **自动刷新** - 30秒自动刷新实例状态，可通过开关控制
✅ **实时状态同步** - 操作后立即更新本地状态，自动刷新同步真实状态
✅ **自适应字体** - 根据屏幕分辨率和 DPI 自动调整字体大小
✅ **暗色模式支持** - 自动跟随系统主题，完美适配暗色模式
✅ **命令行风格控制台** - 实时显示操作日志和系统状态

## 项目结构

```
aws_ec2_gui/
├── main.py              # GUI 主程序（包含自适应字体系统）
├── ec2_service.py       # EC2 服务层（多区域支持）
├── screen_utils.py      # 屏幕分辨率检测工具
├── requirements.txt     # Python 依赖
├── .env.example         # 环境变量配置示例
├── .gitignore          # Git 忽略规则
├── run.bat             # Windows 快速启动脚本
└── README.md           # 项目说明文档
```

## 技术栈

- **Python 3.8+** - 编程语言
- **Flet** - 跨平台 GUI 框架
- **Boto3** - AWS SDK for Python
- **python-dotenv** - 环境变量管理

## 安装步骤

### 1. 克隆或下载项目

```bash
cd D:\work\aws_ec2_gui
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置 AWS 凭证

**方式一：使用 AWS CLI 配置（推荐）**

```bash
aws configure
```

按提示输入：
- AWS Access Key ID
- AWS Secret Access Key
- Default region name
- Default output format

**方式二：使用环境变量**

复制 `.env.example` 为 `.env` 并填入凭证：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```
AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
AWS_DEFAULT_REGION=us-east-1
```

### 4. 运行应用

```bash
python main.py
```

## 使用指南

### 界面说明

1. **区域选择** - 下拉菜单选择要管理的 AWS 区域
2. **刷新按钮** - 点击获取最新的实例列表
3. **实例表格** - 显示实例的详细信息：
   - 实例名称
   - 实例 ID
   - 当前状态
   - 实例类型
   - 公网 IP
   - 私有 IP
4. **操作按钮** - 每个实例都有启动/停止按钮

### 操作流程

1. **选择区域** - 在顶部选择你的 EC2 实例所在的 AWS 区域
2. **刷新列表** - 点击"刷新实例列表"按钮加载实例
3. **启动实例** - 点击绿色播放按钮启动已停止的实例
4. **停止实例** - 点击红色停止按钮停止运行中的实例

### 状态说明

- 🟢 **running** - 实例正在运行
- 🔴 **stopped** - 实例已停止
- 🟡 **pending** - 实例正在启动
- 🟠 **stopping** - 实例正在停止
- ⚪ **terminated** - 实例已终止

## 注意事项

⚠️ **重要提示：**

1. **权限要求** - 确保 AWS 凭证具有以下 IAM 权限：
   - `ec2:DescribeInstances`
   - `ec2:StartInstances`
   - `ec2:StopInstances`

2. **安全建议**：
   - 不要将 AWS 凭证硬编码在代码中
   - 不要将 `.env` 文件提交到版本控制系统
   - 使用 IAM 角色时遵循最小权限原则

3. **操作确认**：
   - 启动/停止实例可能需要几秒到几分钟时间
   - 操作后会自动刷新状态，请稍等片刻

4. **费用提醒**：
   - 运行中的 EC2 实例会产生费用
   - 停止的实例仅收取存储费用
   - 请根据实际需要管理实例状态

## 故障排除

### 常见问题

**问题 1：提示"未找到 AWS 凭证"**

解决方法：
- 检查是否已运行 `aws configure`
- 检查 `.env` 文件是否正确配置
- 验证环境变量是否已设置

**问题 2：无法连接到 AWS**

解决方法：
- 检查网络连接
- 验证 AWS 凭证是否有效
- 确认选择的区域是否正确

**问题 3：权限不足**

解决方法：
- 检查 IAM 用户是否具有必要的 EC2 权限
- 联系 AWS 管理员分配权限

## 系统要求

- Python 3.8 或更高版本
- Windows / macOS / Linux
- 稳定的网络连接
- 有效的 AWS 账户和凭证

## 📦 打包为桌面程序

本应用支持打包成独立的可执行文件,无需安装 Python 即可运行。

### 快速打包

```bash
# Windows
build_pyinstaller.bat

# Linux/macOS
chmod +x build_pyinstaller.sh
./build_pyinstaller.sh
```

打包后的可执行文件位于 `dist/` 目录。

### 详细文档

- **快速入门:** [QUICK_BUILD.md](QUICK_BUILD.md) - 3 步完成打包
- **完整指南:** [BUILD_GUIDE.md](BUILD_GUIDE.md) - 详细配置和最佳实践

## 开发计划

未来可能添加的功能：

- [ ] 实例重启功能
- [ ] 批量操作支持
- [ ] 实例详情查看
- [ ] 安全组管理
- [ ] 实例监控指标
- [ ] 操作日志记录

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

如有问题或建议，请通过 GitHub Issues 反馈。

---

**免责声明**：本工具仅供学习和个人使用，使用者需自行承担 AWS 资源管理的责任和费用。
