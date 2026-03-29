"""
从 tophub.today 爬取热搜数据，输出 JSON。
兼容 GitHub Actions 和本地运行。
"""
import json
import re
import sys
import urllib.request
from datetime import datetime, timezone, timedelta

SITES = {
    "weibo": {"url": "https://tophub.today/n/KqndgxeLl9", "name": "微博"},
    "bilihot": {"url": "https://tophub.today/n/74KvxwokxM", "name": "哔哩哔哩"},
    "douyin": {"url": "https://tophub.today/n/DpQvNABoNE", "name": "抖音"},
}

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


def extract_items(html):
    """从 tophub HTML 提取热搜条目"""
    items = []
    rows = re.findall(r'<tr[^>]*>[\s\S]*?</tr>', html, re.IGNORECASE)

    for row in rows:
        link_match = re.search(r'<a[^>]*href="([^"]*)"[^>]*>([^<]{4,})</a>', row)
        if not link_match:
            continue

        url = link_match.group(1)
        title = link_match.group(2).strip()
        title = (
            title.replace("&amp;", "&")
            .replace("&lt;", "<")
            .replace("&gt;", ">")
            .replace("&quot;", '"')
            .replace("&#39;", "'")
        )
        if len(title) < 4 or len(title) > 100:
            continue

        # 提取热度
        hot = ""
        # 微博: <td class="ws">105万</td>
        hot_td = re.search(r'<td class="ws">([^<]+)</td>', row)
        if hot_td:
            hot = hot_td.group(1).strip()
        else:
            # B站/抖音: td[2] 里的播放量，如 "228.3万" 或 "49367285次播放"
            all_tds = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
            if len(all_tds) > 2:
                td2_text = re.sub(r'<[^>]+>', ' ', all_tds[2]).strip()
                # 找最后一个数字+单位
                hot_m = re.findall(r'([\d.]+\s*[万亿]?\s*(?:次播放)?)', td2_text)
                if hot_m:
                    raw = hot_m[-1].strip()
                    if '次播放' in raw:
                        num_str = raw.replace('次播放', '').strip()
                        try:
                            n = float(num_str)
                            if n >= 10000:
                                hot = f"{n/10000:.0f}万"
                            else:
                                hot = raw
                        except:
                            hot = raw
                    else:
                        hot = raw

        items.append({
            "index": len(items) + 1,
            "title": title,
            "url": url if url.startswith("http") else "https://tophub.today" + url,
            "hot": hot,
        })

        if len(items) >= 50:
            break

    return items


def fetch_site(key):
    """获取单个平台热搜"""
    site = SITES[key]
    req = urllib.request.Request(site["url"], headers={"User-Agent": UA})
    resp = urllib.request.urlopen(req, timeout=20)
    html = resp.read().decode("utf-8", errors="replace")

    items = extract_items(html)
    if not items:
        raise ValueError(f"No items found for {key}")

    now = datetime.now(timezone(timedelta(hours=8)))
    return {
        "success": True,
        "title": site["name"] + "热搜榜",
        "subtitle": f"Top {len(items)}",
        "update_time": now.strftime("%Y-%m-%d %H:%M:%S"),
        "data": items,
    }


def main():
    all_data = {}
    for key in SITES:
        try:
            data = fetch_site(key)
            all_data[key] = data
            print(f"  OK  {data['title']} - {len(data['data'])} items")
        except Exception as e:
            print(f"  ERR {key}: {e}")

    now = datetime.now(timezone(timedelta(hours=8)))
    out = {"success": len(all_data) > 0, "update_time": now.strftime("%Y-%m-%d %H:%M:%S"), "data": all_data}

    output_path = sys.argv[1] if len(sys.argv) > 1 else "hot-data.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"\n  -> {output_path} ({len(all_data)}/{len(SITES)} platforms)")
    return len(all_data) > 0


if __name__ == "__main__":
    ok = main()
    sys.exit(0 if ok else 1)
