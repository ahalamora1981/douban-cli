# 豆瓣 CLI & Skill

通过命令行工具或 AI Agent 自然语言交互，查询豆瓣正在上映、即将上映的电影信息及电影详情。

## 项目组成

```
douban-cli-project/
├── src/main.py                        # CLI 核心代码
├── .agents/skills/douban-movie/SKILL.md  # Agent Skill 定义
├── douban-movie.skill                 # Skill 安装包（二进制）
├── pyproject.toml                     # Python 项目配置
└── README.md
```

- **CLI 工具**：`douban` 命令，提供 `movie-now`、`movie-later`、`movie-info` 三个子命令
- **Agent Skill**：让 AI 编程助手（如 opencode）理解自然语言意图，自动调用 CLI 获取电影信息

## 环境要求

- Python >= 3.10
- [uv](https://docs.astral.sh/uv/) 包管理器

## 安装

```bash
# 克隆项目
git clone <repo-url>
cd douban-cli-project

# 创建虚拟环境并安装依赖
uv sync

# 以可编辑模式安装 CLI 工具（注册 douban 命令）
uv pip install -e .
```

安装完成后，`douban` 命令即可全局使用。

## CLI 使用指南

### 1. 正在上映的电影

```bash
douban movie-now [选项]
```

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `--city <城市拼音>` | `shanghai` | 城市，如 `beijing`、`guangzhou`、`chengdu` |
| `--score <分数>` | `0` | 最低评分筛选，结果按评分降序排列 |
| `--name <关键词>` | 无 | 按片名模糊搜索 |
| `--format <格式>` | `csv` | 输出格式：`json`、`csv`、`md`、`text` |

示例：

```bash
# 查看北京正在上映的所有电影（CSV 格式）
douban movie-now --city beijing

# 查看评分 8 分以上的电影（JSON 格式）
douban movie-now --city shanghai --score 8.0 --format json

# 搜索片名包含"流浪"的电影
douban movie-now --name "流浪" --format md
```

输出字段：`id`、`title`、`score`、`duration`、`region`、`director`、`actors`、`vote_count`

### 2. 即将上映的电影

```bash
douban movie-later [选项]
```

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `--city <城市拼音>` | `shanghai` | 城市 |
| `--name <关键词>` | 无 | 按片名模糊搜索 |
| `--format <格式>` | `csv` | 输出格式：`json`、`csv`、`md`、`text` |

示例：

```bash
douban movie-later --city shanghai --format json
douban movie-later --name "地球" --format text
```

输出字段：`id`、`title`、`release_date`、`genre`、`region`、`want_count`

### 3. 电影详情

```bash
douban movie-info --id <电影ID> [选项]
```

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `--id <ID>` | 必填 | 电影 ID（从 `movie-now` 或 `movie-later` 获取） |
| `--format <格式>` | `json` | 输出格式：`json`、`md`、`text` |

示例：

```bash
douban movie-info --id 36697078 --format md
douban movie-info --id 36697078 --format json
```

输出包含：
- **基本信息**：`id`、`title`、`year`、`genres`、`languages`、`pubdate`、`rating`、`intro`、`comment_count`、`review_count`、`forum_topic_count`
- **导演**：`id`、`name`、`latin_name`
- **演员**：`id`、`name`、`latin_name`、`character`
- **热门短评**（前 20 条）：`user`、`rating`、`comment`、`create_time`、`vote_count`
- **热门影评**（前 20 条）：`user`、`rating`、`title`、`abstract`、`useful_count`、`comments_count`、`create_time`

### 城市名称说明

城市参数使用拼音，不加空格：

| 城市 | 参数 |
|------|------|
| 北京 | `beijing` |
| 上海 | `shanghai` |
| 广州 | `guangzhou` |
| 深圳 | `shenzhen` |
| 成都 | `chengdu` |
| 杭州 | `hangzhou` |
| 武汉 | `wuhan` |
| 南京 | `nanjing` |

## Agent Skill 使用指南

本项目附带一个 Agent Skill，安装后可让 AI 编程助手通过自然语言查询电影信息。

### 什么是 Agent Skill

Agent Skill 是一段指令描述文件（SKILL.md），告诉 AI 助手如何将用户的自然语言请求翻译为对应的 CLI 命令。当用户说"北京有什么电影在上映"时，Agent 会自动执行 `douban movie-now --city beijing` 并整理结果返回。

### Skill 触发词

以下自然语言表述会触发 Skill：

- **正在上映**：`正在上映`、`上映`、`影讯`、`now playing`、`what's showing`
- **即将上映**：`即将上映`、`upcoming`、`movie schedule`
- **电影详情**：`电影`、`豆瓣电影`、`电影信息`

### 典型对话示例

```
用户：北京正在上映什么电影？
Agent：[自动执行 douban movie-now --city beijing --format json，返回电影列表]

用户：有没有评分 8 分以上的？
Agent：[执行 douban movie-now --city beijing --score 8.0 --format json]

用户：给我看一下"密探"的详细信息
Agent：[先通过 movie-now 搜索获取 ID，再执行 movie-info 获取详情]

用户：杭州最近有什么电影快上了？
Agent：[执行 douban movie-later --city hangzhou --format json]
```

### 工作原理

```
用户自然语言 ──→ AI Agent ──→ 解析意图 ──→ 调用 douban CLI ──→ 整理返回结果
                   │                          │
                   └── 读取 SKILL.md ──────────┘
                       获得命令格式和参数说明
```

## 开发

```bash
# 安装开发依赖
uv sync

# 代码检查（使用 ruff）
uv run ruff check src/

# 运行 CLI（开发模式）
uv run douban movie-now --city shanghai --format json
```

## 技术栈

- Python 3.12+
- [requests](https://docs.python-requests.org/)：HTTP 请求
- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/)：HTML 解析
- [uv](https://docs.astral.sh/uv/)：包管理与虚拟环境
- 数据来源：豆瓣电影（PC 端页面 + 移动端 API）
