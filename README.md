# 📊 经济周期与股票分析

基于 Python + React 的量化分析网站。

## 功能

- 🔍 股票代码搜索
- 📈 日频股价K线图（支持自定义日期范围）
- 📊 技术指标（MA5、MA10、MA20、成交量）
- 💹 基本面数据展示

## 技术栈

- **前端**: HTML5 + ECharts
- **后端**: Python + akshare + 阿里云函数计算
- **数据**: akshare（免费开源）

## 快速部署

### 前端部署（GitHub Pages）

1. 将 `src` 目录推送到 GitHub
2. 在仓库 Settings → Pages 中启用
3. 选择 `main` 分支和 `/src` 文件夹

### 后端部署（阿里云函数计算）

1. 登录阿里云函数计算控制台
2. 创建函数，选择 Python 3.9
3. 上传 `cloudfunctions/stock_data/index.py`
4. 配置触发器为 HTTP 触发器

## 使用方法

1. 输入股票代码（如 600519、000001）
2. 选择日期范围
3. 点击查询

## 数据来源

- 股票数据：[akshare](https://github.com/akfamily/akshare)
- 技术指标：MA5、MA10、MA20

---

*本工具仅供参考，不构成投资建议。*
