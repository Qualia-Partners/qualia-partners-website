# Qualia Partners website

Live: https://qualiapartners.com.au/

## Peopling

The full book is published at https://qualiapartners.com.au/peopling/.
The manuscript remains in **Dixie-Flatl1ne/peopling-book**, on `main`.
Edit `peopling_book.md` and the figures there, then commit and push normally.

The website's **Deploy to GitHub Pages** workflow checks out the latest book,
runs its existing Python builder, and publishes the reading page alongside the
website. No generated book copy is committed here. No cross-repository write
token, account transfer, or book-side workflow is required: the book is public.

The audiobook is generated in the book repository. The workflow fetches its
`audio/` directory; the site build publishes only the manifest and the MP3 it
references, and only when the book builder includes the audio player. Narration
is not regenerated in CI. The book builder hides narration after a manuscript
change until a matching recording has been generated and committed.

Deployment runs:

- On a push to this website's `main` branch.
- Hourly, at minute 17, to pick up book-only changes. GitHub may delay scheduled runs.
- On demand: Actions > Deploy to GitHub Pages > Run workflow. Dixie has Maintain
  access to this repository and can run it.

GitHub can disable scheduled workflows after 60 days without activity in a public
repository. If that happens, re-enable the workflow in Actions. Manual runs and
website pushes also provide a way to publish updates.

The deployed book commit is recorded in `/peopling/source.json`. Build or validation
failures stop deployment and leave the previous live site in place. The old book
repository and its GitHub Pages site remain available.

## Local build

Use Python 3.12 (as in CI) and a local book checkout:

```sh
python3 -m venv .venv
.venv/bin/pip install -r scripts/requirements.txt
.venv/bin/python scripts/build_site.py --book ../peopling-book --output _site
python3 -m http.server 8769 --directory _site
```

The output directory must not already exist; use a new directory for a subsequent
build. The script copies only explicit website files and assets into the output,
then adds the rendered book. Manuscript working material, Git metadata and build
tools are never part of the Pages artifact. It checks local links, chapter anchors
and figures before publishing. The book's source checkout is not modified.

`site/build.py` in the book repository owns the reading layout. This website's
`scripts/build_site.py` adds the canonical URL, social metadata and links back to
Qualia; `scripts/peopling.css` styles those links.
