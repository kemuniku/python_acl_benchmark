"""Dependency-free SVG, Markdown, and HTML benchmark reports."""

from __future__ import annotations

import hashlib
import html
import json
import math
import re
import shutil
import textwrap
from collections import defaultdict
from pathlib import Path
from urllib.parse import quote, urlsplit


COLORS = ("#2563eb", "#dc2626", "#059669", "#9333ea", "#d97706", "#0891b2", "#db2777", "#475569")


def _escape(value: object) -> str:
    return html.escape(str(value), quote=True)


def _markdown(value: object) -> str:
    value = _escape(value).replace("\n", " ").replace("\r", " ")
    return re.sub(r"([\\`*_{\[\]}()|])", r"\\\1", value)


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "-", value).strip("-")[:80]
    if slug != value:
        slug = (slug or "case") + "-" + hashlib.sha256(value.encode()).hexdigest()[:10]
    return slug


def _runtime_name(record: dict) -> str:
    runtime = record.get("runtime", {})
    return " ".join(str(part) for part in (runtime.get("implementation", runtime.get("id", "unknown")), runtime.get("version", "")) if part)


def _point(point: dict) -> dict | None:
    try:
        size, median = float(point["size"]), float(point["median"])
        low, high = float(point.get("min", median)), float(point.get("max", median))
    except (KeyError, TypeError, ValueError, OverflowError):
        return None
    if not all(math.isfinite(value) and value >= 0 for value in (size, median, low, high)):
        return None
    return {"size": size, "median": median, "min": min(low, median), "max": max(high, median)}


def _number(value: float) -> str:
    if value == 0:
        return "0"
    if abs(value) >= 1e6 or abs(value) < 0.001:
        return f"{value:.2g}"
    if abs(value) >= 1000:
        return f"{value:,.0f}"
    return f"{value:.3g}"


def _scale(values: list[float], start: float, end: float) -> tuple:
    """Return a coordinate function, ticks, and scale name; zero uses linear."""
    low, high = min(values), max(values)
    logarithmic = low > 0
    if logarithmic:
        lower, upper = math.log10(low), math.log10(high)
        padding = max((upper - lower) * 0.06, 0.08)
        lower, upper = lower - padding, upper + padding
        transform = math.log10
        ticks = []
        exponent_start, exponent_end = math.floor(lower), math.ceil(upper)
        for exponent in range(exponent_start, exponent_end + 1):
            for multiple in (1, 2, 5):
                value = multiple * 10.0**exponent
                if lower <= math.log10(value) <= upper:
                    ticks.append(value)
        if len(ticks) > 12:
            ticks = [value for value in ticks if abs(math.log10(value) - round(math.log10(value))) < 1e-8]
            ticks = ticks[:: max(1, math.ceil(len(ticks) / 10))]
        if len(ticks) < 2:
            ticks = sorted(set((low, high)))
    else:
        lower, upper = 0.0, high * 1.08 if high else 1.0
        transform = lambda value: value
        ticks = [upper * index / 5 for index in range(6)]

    def coordinate(value: float) -> float:
        return start + (transform(value) - lower) / (upper - lower) * (end - start)

    return coordinate, ticks, "log" if logarithmic else "linear"


def _marker(x: float, y: float, color: str, index: int) -> str:
    if index % 3 == 1:
        return f'<rect x="{x - 3.8:.2f}" y="{y - 3.8:.2f}" width="7.6" height="7.6" fill="white" stroke="{color}" stroke-width="2"/>'
    if index % 3 == 2:
        return f'<path d="M{x:.2f},{y - 5:.2f} L{x + 5:.2f},{y:.2f} L{x:.2f},{y + 5:.2f} L{x - 5:.2f},{y:.2f} Z" fill="white" stroke="{color}" stroke-width="2"/>'
    return f'<circle cx="{x:.2f}" cy="{y:.2f}" r="3.8" fill="white" stroke="{color}" stroke-width="2"/>'


def _chart(records: list[dict], title: str) -> str:
    lines = []
    for record in records:
        for series in record.get("series", []):
            points = [_point(point) for point in series.get("points", [])]
            points = sorted((point for point in points if point is not None), key=lambda point: point["size"])
            if points:
                lines.append({"id": str(series["id"]), "label": str(series.get("label", series["id"])), "runtime": _runtime_name(record), "points": points})
    if not lines:
        return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1040 220" role="img">'
                f'<title>{_escape(title)}</title><rect width="1040" height="220" fill="white"/>'
                '<text x="520" y="110" text-anchor="middle" font-family="sans-serif" fill="#64748b">No measurements available</text></svg>')

    library_ids = sorted({line["id"] for line in lines})
    runtime_ids = sorted({line["runtime"] for line in lines})
    legend = [textwrap.wrap(f'{line["label"]} / {line["runtime"]}', width=55, break_long_words=True) for line in lines]
    legend_rows = []
    for offset in range(0, len(legend), 2):
        legend_rows.append(max(len(entry) for entry in legend[offset:offset + 2]) * 18 + 16)
    height = 500 + sum(legend_rows)
    all_points = [point for line in lines for point in line["points"]]
    x, x_ticks, x_mode = _scale([point["size"] for point in all_points], 100, 998)
    max_time = max(point["max"] for point in all_points)
    unit, multiplier = ("ns", 1e9) if max_time < 1e-6 else (("µs", 1e6) if max_time < 1e-3 else (("ms", 1e3) if max_time < 1 else ("s", 1)))
    y, y_ticks, y_mode = _scale([point[key] * multiplier for point in all_points for key in ("min", "max")], 406, 94)
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="1040" height="{height}" viewBox="0 0 1040 {height}" role="img" aria-labelledby="title desc">',
           f'<title id="title">{_escape(title)} benchmark</title>',
           f'<desc id="desc">Median elapsed time versus input size. Bands and whiskers show the observed minimum and maximum. X axis: {x_mode}. Y axis: {y_mode}. Lower is faster.</desc>',
           '<rect width="100%" height="100%" rx="12" fill="white"/>',
           '<g font-family="-apple-system, BlinkMacSystemFont, Segoe UI, sans-serif" fill="#0f172a">',
           f'<text x="40" y="36" font-size="23" font-weight="700">{_escape(title)}</text>',
           '<text x="40" y="61" font-size="13" fill="#64748b">Lower is faster · median line · observed min–max range</text>']
    for tick in x_ticks:
        position = x(tick)
        svg.extend((f'<line x1="{position:.2f}" y1="94" x2="{position:.2f}" y2="406" stroke="#e2e8f0"/>',
                    f'<text x="{position:.2f}" y="431" font-size="12" text-anchor="middle" fill="#475569">{_number(tick)}</text>'))
    for tick in y_ticks:
        position = y(tick)
        svg.extend((f'<line x1="100" y1="{position:.2f}" x2="998" y2="{position:.2f}" stroke="#e2e8f0"/>',
                    f'<text x="87" y="{position + 4:.2f}" font-size="12" text-anchor="end" fill="#475569">{_number(tick)}</text>'))
    svg.extend(('<path d="M100 94 V406 H998" fill="none" stroke="#94a3b8"/>',
                f'<text x="549" y="461" font-size="14" text-anchor="middle">Input size n ({x_mode} scale)</text>',
                f'<text transform="translate(25 250) rotate(-90)" font-size="14" text-anchor="middle">Elapsed time [{unit}] ({y_mode} scale)</text>'))
    for line in lines:
        color = COLORS[library_ids.index(line["id"]) % len(COLORS)]
        runtime_index = runtime_ids.index(line["runtime"])
        dash = ('', ' stroke-dasharray="7 4"', ' stroke-dasharray="2 4"')[runtime_index % 3]
        points = line["points"]
        upper = [(x(point["size"]), y(point["max"] * multiplier)) for point in points]
        lower = [(x(point["size"]), y(point["min"] * multiplier)) for point in reversed(points)]
        polygon = " ".join(f"{px:.2f},{py:.2f}" for px, py in upper + lower)
        svg.append(f'<polygon points="{polygon}" fill="{color}" fill-opacity="0.09"/>')
        for point in points:
            px, low_y, high_y = x(point["size"]), y(point["min"] * multiplier), y(point["max"] * multiplier)
            svg.append(f'<path d="M{px:.2f},{high_y:.2f} V{low_y:.2f} M{px - 3:.2f},{high_y:.2f} H{px + 3:.2f} M{px - 3:.2f},{low_y:.2f} H{px + 3:.2f}" stroke="{color}" stroke-opacity="0.5" fill="none"/>')
        polyline = " ".join(f'{x(point["size"]):.2f},{y(point["median"] * multiplier):.2f}' for point in points)
        svg.append(f'<polyline points="{polyline}" fill="none" stroke="{color}" stroke-width="2.5"{dash}/>')
        for point in points:
            svg.append(_marker(x(point["size"]), y(point["median"] * multiplier), color, runtime_index))
    legend_y = 493
    for index, line in enumerate(lines):
        if index and index % 2 == 0:
            legend_y += legend_rows[index // 2 - 1]
        legend_x = 42 + index % 2 * 510
        color = COLORS[library_ids.index(line["id"]) % len(COLORS)]
        runtime_index = runtime_ids.index(line["runtime"])
        dash = ('', ' stroke-dasharray="7 4"', ' stroke-dasharray="2 4"')[runtime_index % 3]
        svg.append(f'<line x1="{legend_x}" y1="{legend_y - 4}" x2="{legend_x + 31}" y2="{legend_y - 4}" stroke="{color}" stroke-width="2.5"{dash}/>')
        svg.append(_marker(legend_x + 15, legend_y - 4, color, runtime_index))
        for row, label in enumerate(legend[index]):
            svg.append(f'<text x="{legend_x + 41}" y="{legend_y + row * 18}" font-size="12">{_escape(label)}</text>')
    svg.append("</g></svg>")
    return "\n".join(svg) + "\n"


def _source_html(sources: dict) -> str:
    entries = []
    for name, source in sorted(sources.items()):
        url = str(source.get("url", ""))
        label = _escape(name)
        if urlsplit(url).scheme in {"https", "http"}:
            label = f'<a href="{_escape(url)}">{label}</a>'
        entries.append(f'{label}: <code>{_escape(source.get("rev", "local"))}</code>')
    return "<br>".join(entries) or "—"


def _provenance_html(record: dict) -> str:
    runtime, settings = record.get("runtime", {}), record.get("settings", {})
    coverage = ", ".join(str(size) for size in settings.get("sizes", [])) or "?"
    mode = ' <span class="badge">quick</span>' if settings.get("quick") else ""
    return (f'<tr><td><strong>{_escape(_runtime_name(record))}</strong>{mode}<br><span class="muted">{_escape(runtime.get("build") or runtime.get("id", ""))}</span></td>'
            f'<td>{_escape(record.get("measured_at", "unknown"))}<br><code>{_escape(record.get("commit") or "unknown")}</code></td>'
            f'<td>{_escape(runtime.get("cpu") or "unknown CPU")}<br><span class="muted">{_escape(runtime.get("platform", ""))}<br>image: {_escape(runtime.get("runner_image", "unknown"))} / {_escape(runtime.get("runner_image_version", "unknown"))}</span></td>'
            f'<td>n={_escape(coverage)}<br>repeat={_escape(settings.get("repeat", "?"))}<br>warmup={_escape(settings.get("warmup", "?"))}<br>warmup_seconds={_escape(settings.get("warmup_seconds", "?"))}<br>sample_seconds={_escape(settings.get("sample_seconds", "?"))}<br>seed={_escape(settings.get("seed", "?"))}</td>'
            f'<td>{_source_html(record.get("sources", {}))}</td></tr>')


CSS = """
:root{color-scheme:light;--ink:#0f172a;--muted:#64748b;--line:#e2e8f0;--blue:#2563eb}
*{box-sizing:border-box}body{margin:0;background:#f5f7fb;color:var(--ink);font:15px/1.7 system-ui,-apple-system,sans-serif}
a{color:var(--blue);text-decoration:none}a:hover{text-decoration:underline}header{background:linear-gradient(125deg,#0f172a,#1e3a8a);color:white;padding:48px max(24px,calc((100vw - 1160px)/2)) 40px}
header p{color:#cbd5e1;max-width:800px}.eyebrow{letter-spacing:.15em;font-size:12px;font-weight:700;color:#93c5fd}h1{font-size:clamp(27px,4vw,40px);line-height:1.25;margin:12px 0 18px}h2{font-size:24px;margin:0}p{margin:10px 0}
main{max-width:1208px;margin:auto;padding:28px 24px 48px}.stats{display:flex;gap:28px;flex-wrap:wrap;margin-top:24px}.stat strong{font-size:26px;display:block}.stat span{font-size:12px;color:#cbd5e1}
nav{display:flex;gap:10px;flex-wrap:wrap;margin:0 0 28px}nav a{background:white;border:1px solid var(--line);padding:6px 15px;border-radius:100px;color:#334155}
.card{background:white;border:1px solid var(--line);border-radius:16px;margin-bottom:26px;overflow:hidden;box-shadow:0 4px 18px #0f172a04;scroll-margin-top:20px}.card-head{padding:24px 28px 8px}.description,.muted{color:var(--muted)}.chart{display:block;width:100%;height:auto}.downloads{display:flex;gap:16px;flex-wrap:wrap;padding:0 28px 20px;font-size:13px}
.runtime-chart h3{margin:0;padding:16px 28px 0;font-size:18px}.runtime-chart+.runtime-chart{border-top:1px solid var(--line)}
details{border-top:1px solid var(--line);padding:16px 28px}summary{cursor:pointer;font-size:13px;font-weight:600}.table-wrap{overflow-x:auto}table{border-collapse:collapse;width:100%;font-size:12px;margin-top:14px}th,td{text-align:left;padding:10px 12px;vertical-align:top;border-bottom:1px solid var(--line)}th{color:var(--muted);font-weight:600}code{font-family:ui-monospace,monospace;font-size:11px;overflow-wrap:anywhere}td{min-width:130px}footer{font-size:12px;color:var(--muted);padding:4px 2px}.empty{padding:32px}
.badge{display:inline-block;border-radius:5px;background:#fef3c7;color:#92400e;padding:2px 7px;font-size:12px;font-weight:600}
@media(max-width:640px){header{padding:32px 20px}main{padding:20px 10px}.card-head{padding:20px 16px 8px}.downloads,details,.runtime-chart h3{padding-left:16px;padding-right:16px}.chart{min-width:720px}.chart-wrap{overflow-x:auto}.stats{gap:22px}}
"""


def render(results_dir: Path, output_dir: Path) -> None:
    """Rebuild a portable report from all available runtime/case JSON files.

    Results from runtimes that have not run yet are simply absent. This function
    owns ``charts/`` and ``data/`` beneath the output directory; stale generated
    files in those directories are removed when a case is deleted.
    """
    results_dir, output_dir = Path(results_dir), Path(output_dir)
    if results_dir.resolve() == output_dir.resolve() or results_dir.resolve().is_relative_to(output_dir.resolve()):
        raise ValueError("The report output directory must not contain the input results directory")
    grouped = defaultdict(list)
    records = []
    for source in sorted(results_dir.rglob("*.json")):
        if source.resolve().is_relative_to(output_dir.resolve()):
            continue
        with source.open(encoding="utf-8") as stream:
            record = json.load(stream)
        if not isinstance(record, dict) or "case" not in record or "series" not in record:
            raise ValueError(f"Not a benchmark result: {source}")
        relative = source.relative_to(results_dir)
        entry = {"record": record, "source": source, "relative": relative, "href": "data/" + quote(relative.as_posix())}
        grouped[str(record["case"])].append(entry)
        records.append(record)

    output_dir.mkdir(parents=True, exist_ok=True)
    for directory in (output_dir / "charts", output_dir / "data"):
        if directory.is_dir():
            shutil.rmtree(directory)
        directory.mkdir()
    for entries in grouped.values():
        for entry in entries:
            target = output_dir / "data" / entry["relative"]
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(entry["source"], target)

    sections, navigation = [], []
    markdown = ["# Python ACL ベンチマーク", "", "各実装を CPython / PyPy で比較します。グラフはランタイムごとに分け、軸の範囲を個別に調整します。グラフは小さいほど高速です。線は中央値、帯・ひげは観測された最小値から最大値です。正の値には対数軸を使い、0 を含む軸には線形軸を使います。", "", "[HTML レポート](index.html) · [生データ](data/)", ""]
    for case, entries in sorted(grouped.items()):
        case_records = [entry["record"] for entry in entries]
        title = str(case_records[0].get("title", case))
        description = str(case_records[0].get("description", ""))
        quick = any(record.get("settings", {}).get("quick") for record in case_records)
        quick_notice = '<p><span class="badge">動作確認用 (--quick) の結果を含みます</span></p>' if quick else ""
        slug = _slug(case)
        runtime_groups = defaultdict(list)
        for entry in entries:
            runtime = entry["record"].get("runtime", {})
            runtime_id = str(runtime.get("id") or runtime.get("implementation") or "unknown")
            runtime_groups[runtime_id].append(entry)
        (output_dir / "charts" / slug).mkdir()
        runtime_charts = []
        markdown.extend([f"## {_markdown(title)}", "", _markdown(description), ""])
        for runtime_id, runtime_entries in sorted(runtime_groups.items()):
            runtime_records = [entry["record"] for entry in runtime_entries]
            runtime_label = ", ".join(sorted({_runtime_name(record) for record in runtime_records}))
            chart_title = f"{title} / {runtime_label}"
            chart_href = f"charts/{slug}/{_slug(runtime_id)}.svg"
            (output_dir / chart_href).write_text(_chart(runtime_records, chart_title), encoding="utf-8")
            downloads = [f'<a href="{chart_href}" download>SVG を保存</a>']
            for entry in runtime_entries:
                downloads.append(f'<a href="{_escape(entry["href"])}" download>{_escape(_runtime_name(entry["record"]))} JSON</a>')
            runtime_charts.append(f'<div class="runtime-chart"><h3>{_escape(runtime_label)}</h3>'
                                  f'<div class="chart-wrap"><img class="chart" src="{chart_href}" alt="{_escape(chart_title)} の入力サイズ別実行時間" loading="lazy"></div>'
                                  f'<div class="downloads">{"".join(downloads)}</div></div>')
            markdown.extend([f"### {_markdown(runtime_label)}", "", f"![{_markdown(chart_title)}]({chart_href})", "", f"[SVG を保存]({chart_href})", ""])
        sections.append(f'<section class="card" id="{slug}"><div class="card-head"><h2>{_escape(title)}</h2><p class="description">{_escape(description)}</p>{quick_notice}</div>'
                        + "".join(runtime_charts) + '<details><summary>計測環境・ソース・計測日時</summary><div class="table-wrap">'
                        '<table><thead><tr><th>ランタイム</th><th>計測日時 / commit</th><th>CPU / OS</th><th>設定</th><th>ソース / revision</th></tr></thead><tbody>'
                        + "".join(_provenance_html(record) for record in case_records) + '</tbody></table></div></details></section>')
        navigation.append(f'<a href="#{slug}">{_escape(title)}</a>')
        markdown.extend(["### 計測情報", "", "| ランタイム | 計測日時 | CPU | repeat / warmup / seed | JSON |", "| --- | --- | --- | --- | --- |"])
        for entry in entries:
            record = entry["record"]
            settings = record.get("settings", {})
            config = " / ".join(str(settings.get(key, "?")) for key in ("repeat", "warmup", "seed"))
            runtime_label = _runtime_name(record) + (" [quick]" if settings.get("quick") else "")
            markdown.append(f'| {_markdown(runtime_label)} | {_markdown(record.get("measured_at", "unknown"))} | {_markdown(record.get("runtime", {}).get("cpu", "unknown"))} | {_markdown(config)} | [data]({entry["href"]}) |')
        markdown.append("")
        if quick:
            markdown.extend(["**動作確認用 (`--quick`) の結果を含みます。**", ""])
        for record in case_records:
            markdown.append(f'- {_markdown(_runtime_name(record))}: commit `{_markdown(record.get("commit") or "unknown")}`; OS: {_markdown(record.get("runtime", {}).get("platform", "unknown"))}')
            settings = record.get("settings", {})
            markdown.append(f'  - n={_markdown(settings.get("sizes", []))}; warmup_seconds={_markdown(settings.get("warmup_seconds", "?"))}; sample_seconds={_markdown(settings.get("sample_seconds", "?"))}')
            if record.get("runtime", {}).get("build"):
                markdown.append(f'  - build: {_markdown(record["runtime"]["build"])}')
            for name, source in sorted(record.get("sources", {}).items()):
                markdown.append(f'  - {_markdown(name)}: {_markdown(source.get("url", "local"))} @ `{_markdown(source.get("rev", "local"))}`')
        markdown.append("")

    if not sections:
        sections.append('<section class="card empty"><h2>計測結果はまだありません</h2><p class="muted">ベンチマークを実行すると、ここにグラフと計測情報が表示されます。</p></section>')
        markdown.extend(["計測結果はまだありません。ベンチマークを実行するとグラフが表示されます。", ""])
    runtime_count = len({_runtime_name(record) for record in records})
    point_count = sum(len(series.get("points", [])) for record in records for series in record.get("series", []))
    timestamps = [str(record.get("measured_at", "")) for record in records if record.get("measured_at")]
    last_updated = max(timestamps) if timestamps else "—"
    caution = "CI の CPU・負荷・ランタイムのバージョンによって実行時間は変動します。増分計測ではケースやランタイムごとに計測日時が異なります。各グラフの計測情報と JSON を併せて確認してください。"
    page = ('<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>Python ACL ベンチマーク</title><style>{CSS}</style></head><body><header><div class="eyebrow">PYTHON ACL BENCHMARKS</div>'
            '<h1>実装とランタイムの性能を、入力サイズで比較。</h1><p>CPython と PyPy による AtCoder Library の実行時間。グラフはランタイムごとに分け、軸の範囲を個別に調整します。線は中央値、帯・ひげは最小値から最大値を示します。グラフは小さいほど高速です。</p>'
            f'<div class="stats"><div class="stat"><strong>{len(grouped)}</strong><span>比較ケース</span></div><div class="stat"><strong>{runtime_count}</strong><span>ランタイム</span></div>'
            f'<div class="stat"><strong>{point_count}</strong><span>計測ポイント</span></div></div></header><main><nav aria-label="比較ケース">{"".join(navigation)}</nav>'
            + "".join(sections) + f'<footer><p>{caution}</p><p>最新の計測: {_escape(last_updated)} · <a href="README.md">Markdown</a> · 外部サービス不要の静的レポート</p></footer></main></body></html>\n')
    markdown.extend([caution, ""])
    (output_dir / "index.html").write_text(page, encoding="utf-8")
    (output_dir / "README.md").write_text("\n".join(markdown), encoding="utf-8")
    (output_dir / ".nojekyll").write_text("", encoding="utf-8")
