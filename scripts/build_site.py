#!/usr/bin/env python3
"""Stage the Qualia website and build /peopling/ from the book's public inputs."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent.parent
CANONICAL = 'https://qualiapartners.com.au/peopling/'


def replace_once(text, old, new):
    if text.count(old) != 1:
        raise ValueError(f'Book layout changed: expected one {old!r}')
    return text.replace(old, new, 1)


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.ids, self.links = set(), []
        self.figures = 0
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.add(attrs['id'])
        if tag == 'figure':
            self.figures += 1
        for key in ('href', 'src'):
            if key in attrs:
                self.links.append(attrs[key])


def validate(output):
    output = output.resolve()
    pages = {p: Page(p.read_text()) for p in output.rglob('*.html')}
    for path, page in pages.items():
        for link in page.links:
            url = urlsplit(link)
            if url.scheme or url.netloc:
                continue
            target = (output / unquote(url.path).lstrip('/') if url.path.startswith('/')
                      else path.parent / unquote(url.path)) if url.path else path
            if target.is_dir():
                target /= 'index.html'
            target = target.resolve()
            if not target.is_relative_to(output) or not target.is_file():
                raise ValueError(f'Broken local link in {path.name}: {link}')
            if url.fragment and target in pages and unquote(url.fragment) not in pages[target].ids:
                raise ValueError(f'Broken section link in {path.name}: {link}')
    book = pages[output / 'peopling/index.html']
    required = {f'ch{i}' for i in range(1, 9)} | {'overview', 'epilogue', 'appendix'}
    if not required <= book.ids or book.figures < 10:
        raise ValueError('Book is missing chapters or figures')
    print(f'Validated {len(pages)} pages, all local links, 8 chapters and {book.figures} figures')


def build(book, output):
    book, output = book.resolve(), output.resolve()
    # Refuse to mix generated output with sources or a previous build.
    output.mkdir(parents=True, exist_ok=False)
    # Explicit public site files only: never publish Git data, build tools or working notes.
    for name in ('index.html', 'people.html', 'case-studies.html', 'style.css', 'script.js', 'CNAME'):
        shutil.copy2(ROOT / name, output / name)
    shutil.copytree(ROOT / 'assets', output / 'assets')
    with tempfile.TemporaryDirectory(prefix='peopling-build-') as tmp:
        source = Path(tmp)
        shutil.copy2(book / 'peopling_book.md', source / 'peopling_book.md')
        shutil.copytree(book / 'images', source / 'images')
        (source / 'site').mkdir()
        for name in ('build.py', 'style.css', 'app.js'):
            shutil.copy2(book / 'site' / name, source / 'site' / name)
        subprocess.run([sys.executable, str(source / 'site/build.py')], check=True)
        text = (source / 'peopling_book.html').read_text()
    text = replace_once(text, '<title>Peopling</title>', '<title>Peopling by Stefan van der Wel | Qualia Partners</title>')
    text = replace_once(text, '</head>', f'''<link rel="canonical" href="{CANONICAL}">
<meta property="og:title" content="Peopling by Stefan van der Wel">
<meta property="og:description" content="How Minds Stay in Sync, and Why Everything Depends on It. Read the complete book.">
<meta property="og:type" content="book">
<meta property="og:url" content="{CANONICAL}">
<link rel="icon" href="/assets/favicon-32.png" type="image/png">
<link rel="stylesheet" href="./qualia.css">
</head>''')
    home = '<a class="qualia-home" href="/">&larr; Qualia Partners</a>'
    text = replace_once(text, '<div class="rail-in">', '<div class="rail-in">\n' + home)
    text = replace_once(text, '<p class="tp-author">Stefan van der Wel</p>', '<p class="tp-author">Stefan van der Wel</p>\n' + home)
    if '@@FIGURE' in text:
        raise ValueError('Unrendered figure token in book')
    (output / 'peopling').mkdir()
    (output / 'peopling/index.html').write_text(text)
    shutil.copy2(ROOT / 'scripts/peopling.css', output / 'peopling/qualia.css')
    revision = subprocess.check_output(['git', '-C', str(book), 'rev-parse', 'HEAD'], text=True).strip()
    (output / 'peopling/source.json').write_text(json.dumps({'repository': 'Dixie-Flatl1ne/peopling-book', 'commit': revision}) + '\n')
    validate(output)
    print(f'Built {CANONICAL} from book commit {revision}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--book', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True, help='New, empty output directory')
    args = parser.parse_args()
    build(args.book.resolve(), args.output.resolve())
