---
name: douban-movie
description: Query Douban movie information via the douban CLI tool. Use when the user asks about now-playing movies, upcoming movies, movie schedules, or cinema listings in a Chinese city. Triggers on phrases like "正在上映", "即将上映", "电影", "影讯", "豆瓣电影", "now playing movies", "upcoming movies", "movie schedule", "what's showing".
---

# Douban Movie

Query Douban (豆瓣) movie data using the `douban` CLI tool.

## Prerequisites

The tool must be installed in the project. Run first if not available:

```bash
uv pip install -e .
```

This registers the `douban` command from `pyproject.toml` `[project.scripts]`.

## Commands

### Now Playing Movies

```bash
douban movie-now [options]
```

Returns movies currently in theaters.

| Option | Default | Description |
|--------|---------|-------------|
| `--city <name>` | `shanghai` | City name (pinyin, e.g. `beijing`, `guangzhou`) |
| `--score <float>` | `0` | Minimum rating filter; results sorted by score descending |
| `--name <text>` | (none) | Filter movies by title (substring match) |
| `--format <fmt>` | `csv` | Output format: `json`, `csv`, `md`, `text` |

Example:

```bash
douban movie-now --city beijing --score 8.0 --name "流浪" --format json
```

Output fields: `id`, `title`, `score`, `duration`, `region`, `director`, `actors`, `vote_count`.

### Upcoming Movies

```bash
douban movie-later [options]
```

Returns movies coming soon. Results sorted by `want_count` descending.

| Option | Default | Description |
|--------|---------|-------------|
| `--city <name>` | `shanghai` | City name (pinyin) |
| `--name <text>` | (none) | Filter movies by title (substring match) |
| `--format <fmt>` | `csv` | Output format: `json`, `csv`, `md`, `text` |

Note: `movie-later` has no `--score` parameter.

Example:

```bash
douban movie-later --city shanghai --name "地球" --format text
```

Output fields: `id`, `title`, `release_date`, `genre`, `region`, `want_count`.

### Movie Detail

```bash
douban movie-info --id <movie_id> [options]
```

Returns movie detail including basic info, celebrities, top 20 short comments, and top 20 reviews.

| Option | Default | Description |
|--------|---------|-------------|
| `--id <id>` | (required) | Movie ID (from `movie-now` or `movie-later` output) |
| `--format <fmt>` | `json` | Output format: `json`, `md`, `text` |

Example:

```bash
douban movie-info --id 35010610 --format md
```

Output sections:
- **Basic info**: `id`, `title`, `year`, `genres`, `languages`, `pubdate`, `rating`, `intro`, `comment_count`, `review_count`, `forum_topic_count`
- **Directors**: `id`, `name`, `latin_name`
- **Actors**: `id`, `name`, `latin_name`, `character`
- **Comments** (top 20): `user`, `rating`, `comment`, `create_time`, `vote_count`
- **Reviews** (top 20): `user`, `rating`, `title`, `abstract`, `useful_count`, `comments_count`, `create_time`

## Usage Tips

- Default format is `csv`. Use `--format json` for programmatic parsing.
- City names use pinyin without spaces: `shanghai`, `beijing`, `guangzhou`, `shenzhen`, `chengdu`, `hangzhou`, etc.
- For natural-language queries, translate the user's intent into the appropriate command and options before running.
