"""Record how long each rendered episode is, by reading the file itself.

The Watch block on every entry page used to call its video "the fifty-second
version". That was wrong for all three episodes that exist - 42.0s, 53.7s and
63.4s - and nothing noticed, because the block only renders once a YouTube URL
is pasted into an entry, and no entry has one yet. A string that only executes
after the thing it describes changes is a string nobody checks.

So the length is read from the rendered mp4 rather than typed. An mp4 carries
its own duration in the mvhd atom: a timescale and a duration in those units,
which needs no codec, no decode and no ffmpeg on the path. The first version of
this reader took its offsets four bytes early, read timescale as 0 for every
file, and divided by zero on all eight - a failure that at least announced
itself rather than returning wrong numbers.

    python tools\\set_video_seconds.py            # report
    python tools\\set_video_seconds.py --apply    # write video_seconds
    python tools\\set_video_seconds.py --check    # gate: published video must state a length

Pairs the episode directory with the entry of the same id and only writes where
a rendered file exists, so a field is never invented for an episode that has not
been cut.
"""
import json
import pathlib
import struct
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
ENC = ROOT / "data" / "encyclopedia.json"
EP = ROOT / "episode"

APPLY = "--apply" in sys.argv
CHECK = "--check" in sys.argv


def mp4_seconds(path):
    """Duration in seconds, from the mvhd atom. None if it is not there."""
    data = pathlib.Path(path).read_bytes()
    i = data.find(b"mvhd")
    if i < 0:
        return None
    # box: size(4) type(4) version(1) flags(3), then v0 gives
    # creation(4) modification(4) timescale(4) duration(4)
    version = data[i + 4]
    if version == 1:
        ts = struct.unpack(">I", data[i + 20:i + 24])[0]
        dur = struct.unpack(">Q", data[i + 24:i + 32])[0]
    else:
        ts = struct.unpack(">I", data[i + 16:i + 20])[0]
        dur = struct.unpack(">I", data[i + 20:i + 24])[0]
    if not ts:
        raise ValueError("timescale is 0 - the offsets are wrong, not the file")
    return round(dur / ts, 1)


found = {}
if EP.is_dir():
    for d in sorted(p for p in EP.iterdir() if p.is_dir()):
        if d.name.startswith("."):
            continue
        for mp4 in sorted(d.glob("*.mp4")):
            if "16x9" in mp4.name:
                continue                  # the landscape cut is not the link
            try:
                found[d.name] = mp4_seconds(mp4)
            except Exception as e:
                print(f"  {d.name}/{mp4.name}: {e}")

enc = json.loads(ENC.read_text(encoding="utf-8"))
byid = {e["id"]: e for e in enc["entries"]}

if CHECK:
    problems = []
    for e in enc["entries"]:
        if (e.get("video") or "").strip() and not e.get("video_seconds"):
            problems.append(f"{e['id']}: has a video url but no video_seconds, "
                            "so the Watch block cannot state a length")
    for p in problems:
        print("  PROBLEM:", p)
    if problems:
        raise SystemExit(f"{len(problems)} entr(ies) with an unstated runtime")
    n = sum(1 for e in enc["entries"] if (e.get("video") or "").strip())
    print(f"every entry with a published video states its length ({n} published)")
    raise SystemExit(0)

print(f"{len(found)} rendered episode(s)\n")
changed = []
for eid, secs in found.items():
    e = byid.get(eid)
    if not e:
        print(f"  {eid:<10} {secs:>6.1f}s   (no entry with that id)")
        continue
    cur = e.get("video_seconds")
    mark = "" if cur == secs else f"   <- was {cur}"
    url = (e.get("video") or "").strip()
    print(f"  {eid:<10} {secs:>6.1f}s   video={'set' if url else '(none)'}{mark}")
    if cur != secs:
        changed.append((eid, secs))

if not changed:
    print("\nnothing to change")
elif not APPLY:
    print(f"\n{len(changed)} would change. re-run with --apply")
else:
    for eid, secs in changed:
        byid[eid]["video_seconds"] = secs
    ENC.write_text(json.dumps(enc, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\nwritten: " + ", ".join(f"{e}={s}" for e, s in changed))