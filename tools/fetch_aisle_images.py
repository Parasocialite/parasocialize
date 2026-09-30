import sys, pathlib, json
sys.path.insert(0, 'tools')
import images as im

p = pathlib.Path('data/images.json')
man = json.loads(p.read_text(encoding='utf-8'))

ok = 0
for a, v in man['sections'].items():
    got = im.from_flickr(v['topic'])
    if not got:
        print(f"  MISS {a}")
        continue
    slug = 'section-' + a
    stored, err = im.store(slug, got, 'illustrative')
    if not stored:
        print(f"  FAIL {a}: {err}")
        continue
    man['items'].append({
        'slug': slug, 'for': 'section', 'section': a, 'topic': v['topic'],
        'caption': v['caption'], 'local': stored['local'],
        'src': stored['src'], 'cached': stored['cached']})
    print(f"  ok  {a:<10} {got['author'][:28]:<28} {got['licence']}")
    ok += 1

p.write_text(json.dumps(man, indent=2, ensure_ascii=False), encoding='utf-8')
print(f"{ok}/10 section images cached")
