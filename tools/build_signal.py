"""Build Friday Signal email (copy-paste into Buttondown/Mailchimp) from radar.json + cases.json.
Usage: python tools/build_signal.py
Outputs: signal/latest.html (email-safe tables) + signal/latest.txt
Rule: top 5 by intensity desc, 1 studio pick forced in slot 4, 1 sponsor slot top.
"""
import json, pathlib, datetime
ROOT = pathlib.Path(__file__).resolve().parents[1]
radar = json.loads((ROOT/"radar.json").read_text(encoding="utf-8"))
cases = json.loads((ROOT/"cases.json").read_text(encoding="utf-8"))
try:
    index = json.loads((ROOT/"index.json").read_text(encoding="utf-8"))
    index_items = index.get("items", [])[:5]
    index_week = index.get("week", "")
except Exception:
    index_items, index_week = [], ""
top = sorted(radar, key=lambda d: float(d.get("intensity",0)), reverse=True)[:4]
studio = next((d for d in radar if d.get("affiliate")), radar[-1])
picks = top[:3] + [studio] + top[3:4]
rows = "\n".join(
  f'''<tr><td style="padding:14px 0;border-bottom:1px solid #222020;">
  <p style="margin:0;font-family:monospace;font-size:11px;letter-spacing:2px;color:#b71c1c;">{d.get("type","").upper()} · INTENSITY {d.get("intensity")} · {d.get("read_minutes")} MIN</p>
  <h3 style="margin:6px 0;font-family:Georgia,serif;font-size:20px;color:#111;">{d.get("emoji","")} {d.get("title","")}</h3>
  <p style="margin:0;color:#444;font-size:14px;">{d.get("dek","")}</p>
  <p style="margin:8px 0 0;"><a href="{d.get("link","#")}" style="color:#b71c1c;font-size:13px;">{d.get("link_label","READ →")}</a></p></td></tr>'''
  for d in picks)
case = cases[0]
index_rows = ""
if index_items:
    lis = "".join(f'<li style="margin:4px 0;font-size:13px;color:#111;"><b>{m.get("rank")}. {m.get("title")}</b> <span style="color:#666;">[{m.get("lens")}]</span></li>' for m in index_items)
    index_rows = f'''<tr><td style="padding:18px 28px;background:#fff;border-top:2px solid #07070c;">
  <p style="margin:0;font-family:monospace;font-size:11px;letter-spacing:2px;color:#b71c1c;">THE PARASOCIAL INDEX · {index_week} · SCREENSHOT THIS</p>
  <ol style="margin:8px 0 4px;padding-left:20px;">{lis}</ol>
  <p style="margin:6px 0 0;"><a href="https://www.parasocialize.com/#index" style="color:#b71c1c;font-size:13px;">Full Index + sponsor slot →</a></p></td></tr>'''
html = f"""<html><body style="margin:0;background:#0b0b12;padding:24px;">
<center><table width="600" cellpadding="0" cellspacing="0" style="background:#f4f1e8;border-radius:12px;overflow:hidden;">
<tr><td style="background:#07070c;color:#fff;padding:22px 28px;">
<p style="margin:0;font-family:monospace;font-size:11px;letter-spacing:3px;color:#ff4d2e;">PARASOCIALIZE · FRIDAY SIGNAL · {datetime.date.today().isoformat()}</p>
<h1 style="margin:8px 0 0;font-family:Georgia,serif;font-size:30px;">5 signals. 1 take. No algorithm.</h1></td></tr>
<tr><td style="padding:8px 28px 4px;"><p style="font-family:monospace;font-size:11px;color:#888;">PRESENTED BY [SPONSOR — $250/issue] · <a href="#">Become sponsor →</a></p></td></tr>
{rows}
{index_rows}
<tr><td style="padding:20px 28px;background:#16131a;color:#ffcf5c;font-family:Georgia,serif;">
<b>ENAN'S TAKE:</b> The industry now sells the one-sided contract directly — bubble apps, paid DMs, memory-wiped companions. I ran a video store before the feed; clerks did this with rentals. Full decode in File {case.get("file_no")}: {case.get("title")} — <a href="https://www.parasocialize.com/#cases" style="color:#ffcf5c;">members unlock full →</a></td></tr>
<tr><td style="padding:20px 28px;text-align:center;">
<a href="https://www.parasocialize.com/#circle" style="background:#ff4d2e;color:#14030a;padding:14px 28px;border-radius:99px;text-decoration:none;font-family:monospace;font-size:13px;">JOIN INNER CIRCLE — $7/MO</a>
<p style="font-family:monospace;font-size:11px;color:#888;margin-top:12px;">Free? Forward this. Tip a signal → iNNERdreamers@gmail.com · <a href="#">Unsubscribe</a></p></td></tr>
</table></center></body></html>"""
(ROOT/"signal"/"latest.html").write_text(html, encoding="utf-8")
(ROOT/"signal"/"latest.txt").write_text(f"PARASOCIALIZE FRIDAY SIGNAL\n\n" + "\n\n".join(f'- {d.get("title")} ({d.get("intensity")}): {d.get("dek")}' for d in picks) + (f'\n\nINDEX {index_week}:\n' + "\n".join(f'{m.get("rank")}. {m.get("title")} [{m.get("lens")}]' for m in index_items) if index_items else "") + f'\n\nENAN TAKE: File {case.get("file_no")} {case.get("title")}\nJoin: https://www.parasocialize.com/#circle\n', encoding="utf-8")
print(f"wrote signal/latest.html + .txt with {len(picks)} picks + {len(index_items)} index")
