import argparse
import csv
import io
import json
import re

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

MOBILE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15",
    "Referer": "https://m.douban.com/",
}

REXXAR_BASE = "https://m.douban.com/rexxar/api/v2/movie"


def fetch_movie_nowplaying_html(city: str = "shanghai") -> str:
    url = f"https://movie.douban.com/cinema/nowplaying/{city}/"
    response = requests.get(url, headers=HEADERS)
    return response.text


def fetch_movie_later_html(city: str = "shanghai") -> str:
    url = f"https://movie.douban.com/cinema/later/{city}/"
    response = requests.get(url, headers=HEADERS)
    return response.text


def fetch_movie_detail(movie_id: str) -> dict:
    url = f"{REXXAR_BASE}/{movie_id}"
    return requests.get(url, headers=MOBILE_HEADERS).json()


def fetch_movie_celebrities(movie_id: str) -> dict:
    url = f"{REXXAR_BASE}/{movie_id}/celebrities"
    return requests.get(url, headers=MOBILE_HEADERS).json()


def fetch_movie_interests(movie_id: str, count: int = 20) -> dict:
    url = f"{REXXAR_BASE}/{movie_id}/interests"
    return requests.get(
        url,
        headers=MOBILE_HEADERS,
        params={"start": 0, "count": count, "sort": "new_score"},
    ).json()


def fetch_movie_reviews(movie_id: str, count: int = 20) -> dict:
    url = f"{REXXAR_BASE}/{movie_id}/reviews"
    return requests.get(
        url, headers=MOBILE_HEADERS, params={"start": 0, "count": count}
    ).json()


def parse_movie_info(
    detail: dict, celebrities: dict, interests: dict, reviews: dict
) -> dict:
    info = {
        "id": detail.get("id", ""),
        "title": detail.get("title", ""),
        "year": detail.get("year", ""),
        "genres": detail.get("genres", []),
        "languages": detail.get("languages", []),
        "pubdate": detail.get("pubdate", []),
        "rating": detail.get("rating", {}),
        "intro": detail.get("intro", ""),
        "comment_count": detail.get("comment_count", 0),
        "review_count": detail.get("review_count", 0),
        "forum_topic_count": detail.get("forum_topic_count", 0),
    }

    directors = []
    for d in celebrities.get("directors", []):
        directors.append(
            {
                "id": d.get("id", ""),
                "name": d.get("name", ""),
                "latin_name": d.get("latin_name", ""),
            }
        )
    actors = []
    for a in celebrities.get("actors", []):
        actors.append(
            {
                "id": a.get("id", ""),
                "name": a.get("name", ""),
                "latin_name": a.get("latin_name", ""),
                "character": a.get("character", ""),
            }
        )
    info["directors"] = directors
    info["actors"] = actors

    comments = []
    for i in interests.get("interests", []):
        comments.append(
            {
                "user": i.get("user", {}).get("name", ""),
                "rating": i.get("rating", {}).get("value", ""),
                "comment": i.get("comment", ""),
                "create_time": i.get("create_time", ""),
                "vote_count": i.get("vote_count", 0),
            }
        )
    info["comments"] = comments

    review_list = []
    for r in reviews.get("reviews", []):
        review_list.append(
            {
                "user": r.get("user", {}).get("name", ""),
                "rating": r.get("rating", {}).get("value", ""),
                "title": r.get("title", ""),
                "abstract": r.get("abstract", ""),
                "useful_count": r.get("useful_count", 0),
                "comments_count": r.get("comments_count", 0),
                "create_time": r.get("create_time", ""),
            }
        )
    info["reviews"] = review_list

    return info


def parse_movie_nowplaying(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    movies = []
    for li in soup.select("#nowplaying li.list-item"):
        movie = {
            "id": li.get("id", ""),
            "title": li.get("data-title", ""),
            "score": li.get("data-score", "0"),
            "duration": li.get("data-duration", ""),
            "region": li.get("data-region", ""),
            "director": li.get("data-director", ""),
            "actors": li.get("data-actors", ""),
            "vote_count": li.get("data-votecount", "0"),
        }
        movies.append(movie)
    return movies


def parse_movie_later(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    movies = []
    for item in soup.select("#showing-soon div.item"):
        title_el = item.select_one("div.intro h3 a")
        href = title_el.get("href", "") if title_el else ""
        id_match = re.search(r"subject/(\d+)", href)
        li_tags = item.select("div.intro ul li.dt")
        release = li_tags[0].get_text(strip=True) if len(li_tags) > 0 else ""
        genre = li_tags[1].get_text(strip=True) if len(li_tags) > 1 else ""
        region = li_tags[2].get_text(strip=True) if len(li_tags) > 2 else ""
        want_match = (
            re.search(r"(\d+)", li_tags[3].get_text()) if len(li_tags) > 3 else None
        )
        movie = {
            "id": id_match.group(1) if id_match else "",
            "title": title_el.get_text(strip=True) if title_el else "",
            "release_date": release,
            "genre": genre,
            "region": region,
            "want_count": want_match.group(1) if want_match else "0",
        }
        movies.append(movie)
    return movies


def format_movies(movies: list[dict], fmt: str) -> str:
    if fmt == "json":
        return json.dumps(movies, ensure_ascii=False, indent=2)
    if fmt == "csv":
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=movies[0].keys() if movies else [])
        writer.writeheader()
        writer.writerows(movies)
        return buf.getvalue()
    if fmt == "md":
        if not movies:
            return ""
        keys = movies[0].keys()
        header = "| " + " | ".join(keys) + " |"
        sep = "| " + " | ".join("---" for _ in keys) + " |"
        rows = []
        for m in movies:
            rows.append("| " + " | ".join(str(m[k]) for k in keys) + " |")
        return "\n".join([header, sep, *rows])
    lines = []
    for m in movies:
        lines.append("  ".join(str(v) for v in m.values()))
    return "\n".join(lines)


def format_movie_info_md(info: dict) -> str:
    lines = []
    lines.append(f"# {info['title']} ({info['year']})")
    r = info.get("rating", {})
    lines.append(
        f"评分: {r.get('value', '-')} / {r.get('max', 10)} ({r.get('count', 0)}人评价)"
    )
    lines.append(f"类型: {' / '.join(info.get('genres', []))}")
    lines.append(f"语言: {' / '.join(info.get('languages', []))}")
    lines.append(f"上映: {' / '.join(info.get('pubdate', []))}")
    lines.append(
        f"短评数: {info.get('comment_count', 0)} | 影评数: {info.get('review_count', 0)} | 讨论数: {info.get('forum_topic_count', 0)}"
    )
    lines.append(f"\n## 简介\n{info.get('intro', '')}")
    directors = info.get("directors", [])
    if directors:
        lines.append("\n## 导演")
        for d in directors:
            lines.append(f"- {d['name']} ({d['latin_name']}) [id:{d['id']}]")
    actors = info.get("actors", [])
    if actors:
        lines.append("\n## 演员")
        for a in actors:
            lines.append(
                f"- {a['name']} ({a['latin_name']}) - {a['character']} [id:{a['id']}]"
            )
    comments = info.get("comments", [])
    if comments:
        lines.append("\n## 短评")
        for c in comments:
            stars = "★" * int(c.get("rating", 0)) + "☆" * (5 - int(c.get("rating", 0)))
            lines.append(
                f"- [{stars}] {c['user']} ({c['create_time']}) [{c['vote_count']}有用]"
            )
            lines.append(f"  {c['comment']}")
    reviews = info.get("reviews", [])
    if reviews:
        lines.append("\n## 影评")
        for rv in reviews:
            lines.append(
                f"- 《{rv['title']}》 {rv['user']} ★{rv['rating']} ({rv['create_time']}) [{rv['useful_count']}有用 / {rv['comments_count']}回复]"
            )
            lines.append(f"  {rv['abstract'][:100]}...")
    return "\n".join(lines)


def format_movie_info_text(info: dict) -> str:
    lines = []
    lines.append(f"{info['title']} ({info['year']})")
    r = info.get("rating", {})
    lines.append(
        f"评分: {r.get('value', '-')}/{r.get('max', 10)} ({r.get('count', 0)}人)"
    )
    lines.append(f"类型: {' / '.join(info.get('genres', []))}")
    lines.append(f"上映: {' / '.join(info.get('pubdate', []))}")
    lines.append(f"简介: {info.get('intro', '')}")
    directors = info.get("directors", [])
    if directors:
        lines.append(f"导演: {', '.join(d['name'] for d in directors)}")
    actors = info.get("actors", [])
    if actors:
        lines.append(f"演员: {', '.join(a['name'] for a in actors)}")
    comments = info.get("comments", [])
    if comments:
        lines.append("--- 短评 ---")
        for c in comments:
            lines.append(
                f"  {c['user']} ★{c['rating']} [{c['vote_count']}有用] {c['comment']}"
            )
    reviews = info.get("reviews", [])
    if reviews:
        lines.append("--- 影评 ---")
        for rv in reviews:
            lines.append(
                f"  《{rv['title']}》 {rv['user']} ★{rv['rating']} [{rv['useful_count']}有用]"
            )
            lines.append(f"  {rv['abstract'][:80]}...")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(prog="douban", description="Douban CLI tool")
    subparsers = parser.add_subparsers(dest="command")

    now_parser = subparsers.add_parser("movie-now", help="Get now playing movies")
    now_parser.add_argument(
        "--city",
        default="shanghai",
        help="City name (default: shanghai)",
    )
    now_parser.add_argument(
        "--score",
        type=float,
        default=0.0,
        help="Minimum score filter (default: 0)",
    )
    now_parser.add_argument(
        "--format",
        default="csv",
        choices=["json", "md", "csv", "text"],
        help="Output format (default: csv)",
    )
    now_parser.add_argument(
        "--name",
        default="",
        help="Filter movies by name (substring match)",
    )

    later_parser = subparsers.add_parser("movie-later", help="Get upcoming movies")
    later_parser.add_argument(
        "--city",
        default="shanghai",
        help="City name (default: shanghai)",
    )
    later_parser.add_argument(
        "--format",
        default="csv",
        choices=["json", "md", "csv", "text"],
        help="Output format (default: csv)",
    )
    later_parser.add_argument(
        "--name",
        default="",
        help="Filter movies by name (substring match)",
    )

    info_parser = subparsers.add_parser("movie-info", help="Get movie detail by id")
    info_parser.add_argument(
        "--id",
        required=True,
        help="Movie ID (required)",
    )
    info_parser.add_argument(
        "--format",
        default="json",
        choices=["json", "md", "text"],
        help="Output format (default: json)",
    )

    args = parser.parse_args()

    if args.command == "movie-now":
        html = fetch_movie_nowplaying_html(args.city)
        movies = parse_movie_nowplaying(html)
        filtered = [
            m
            for m in movies
            if float(m["score"]) >= args.score
            and (not args.name or args.name in m["title"])
        ]
        filtered.sort(key=lambda m: float(m["score"]), reverse=True)
        print(format_movies(filtered, args.format))
    elif args.command == "movie-later":
        html = fetch_movie_later_html(args.city)
        movies = parse_movie_later(html)
        movies = [m for m in movies if not args.name or args.name in m["title"]]
        movies.sort(key=lambda m: int(m["want_count"]), reverse=True)
        print(format_movies(movies, args.format))
    elif args.command == "movie-info":
        detail = fetch_movie_detail(args.id)
        celebrities = fetch_movie_celebrities(args.id)
        interests = fetch_movie_interests(args.id)
        reviews = fetch_movie_reviews(args.id)
        info = parse_movie_info(detail, celebrities, interests, reviews)
        if args.format == "json":
            print(json.dumps(info, ensure_ascii=False, indent=2))
        elif args.format == "md":
            print(format_movie_info_md(info))
        else:
            print(format_movie_info_text(info))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
