# -*- coding: utf-8 -*-
"""站内引用校验：本地资源 / 页内锚点 / 孤儿页面。
用法：python tools/check_refs.py   （在站点根目录运行亦可）
"""
import os, re, sys

root = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
COMMENT = re.compile(r'<!--.*?-->', re.S)
PLACEHOLDER = re.compile(r'\[[^\]]*\]|xxx|XXX')

htmls = []
for dp, dn, fn in os.walk(root):
    if os.sep + '.git' in dp:
        continue
    for f in fn:
        if f.endswith('.html'):
            htmls.append(os.path.join(dp, f))

errs = []
for h in sorted(htmls):
    d = os.path.dirname(h)
    raw = open(h, encoding='utf-8').read()
    s = COMMENT.sub('', raw)                      # 注释里的示例路径不算引用
    rel = os.path.relpath(h, root).replace('\\', '/')
    for m in re.finditer(r'(?:src|href)="([^"]+)"', s):
        u = m.group(1)
        if u.startswith(('http', 'mailto:', '#', 'data:')) or u == '':
            continue
        p = u.split('#')[0].split('?')[0]
        if not p:
            continue
        if PLACEHOLDER.search(p):                 # 模板占位符，跳过
            continue
        if not os.path.exists(os.path.normpath(os.path.join(d, p))):
            errs.append('%s -> MISSING %s' % (rel, u))
    for m in re.finditer(r'href="#([^"]+)"', s):
        if 'id="%s"' % m.group(1) not in s:
            errs.append('%s -> missing anchor #%s' % (rel, m.group(1)))

linked = set()
for h in htmls:
    d = os.path.dirname(h)
    for m in re.finditer(r'href="([^"#?]+\.html)', COMMENT.sub('', open(h, encoding='utf-8').read())):
        linked.add(os.path.normpath(os.path.join(d, m.group(1))).lower())

print('checked %d pages' % len(htmls))
print('\n'.join(errs) if errs else 'OK: 本地引用与页内锚点全部可解析')
orphans = [os.path.relpath(h, root).replace('\\', '/') for h in htmls
           if os.path.normpath(h).lower() not in linked]
print('无入链页面：' + ('、'.join(orphans) if orphans else '（无）'))
