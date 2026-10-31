# MSG gripper documentation

The documentation of the MSG compliant AI stepper gripper by [Source Robotics](https://source-robotics.com): the
manual (safety, technical data, installation, setup, operation, firmware), the gripper's CAN and UART reference,
and guides.

**Read it at [docs.source-robotics.com/MSG-gripper-docs](https://docs.source-robotics.com/MSG-gripper-docs/).**

The hardware files are in
[Source-Robotics/MSG-compliant-AI-stepper-gripper](https://github.com/Source-Robotics/MSG-compliant-AI-stepper-gripper);
the gripper runs the firmware of the STEPFOC driver,
[Source-Robotics/STEPFOC-stepper-controller](https://github.com/Source-Robotics/STEPFOC-stepper-controller).

## What is in this repository

| | |
|---|---|
| `docs/` | the pages: the manual chapters at the top level, `build/`, `reference/`, `guides/`, `support/`, `appendix/` |
| `docs/build/bill-of-materials.md`, `docs/assets/bom/` | written by `tools/sync_bom.py` from the gripper repository's BOM and its reference images. Never edit |
| `docs/includes/` | text shared by pages (glossary, symbols, abbreviations) and the data the reference pages are built from |
| `docs/includes/can_commands.yml`, `uart_commands.yml` | the hand-written descriptions of the CAN messages and UART commands a gripper needs (`partial: true`: the rest of the driver's commands are on the STEPFOC site) |
| `docs/includes/generated/` | written by `tools/sync_firmware.py` from the firmware's release tag: `firmware_facts.json`, `firmware_release_notes.md`. Never edit |
| `versions.yml` | every version fact: the gripper release the site is versioned by, the firmware release it describes, the manual's number and revision |
| `compatibility.yml` | which firmware release works with which bootloader, gripper hardware, Python library and ROS 2 driver |
| `hooks/` | `versions.py` writes the version facts into the pages; `firmware_pages.py` builds the reference pages; `llms.py` writes the Markdown twin of every page, `llms.txt` and `llms-full.txt` |
| `tools/` | `sync_firmware.py`, `sync_bom.py`, `test_tools.py`, `root_404.html` |
| `overrides/` | the theme changes: the older-version banner, the edit/report line, the header's repository card |

The site is built with [MkDocs](https://www.mkdocs.org/) and the
[Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) theme, in the same form as the
[STEPFOC](https://github.com/Source-Robotics/STEPFOC-docs) and [PAR6](https://github.com/Source-Robotics/par6)
documentation; the hooks and tools are the same files.

## Preview it locally

You need Python 3.11 or newer.

```bash
git clone https://github.com/Source-Robotics/MSG-gripper-docs.git
cd MSG-gripper-docs
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt      # Linux and macOS: .venv/bin/pip
mkdocs serve
```

Open `http://127.0.0.1:8000/MSG-gripper-docs/`. The page reloads by itself when you save a file.

Every push and pull request runs `python tools/test_tools.py` and `mkdocs build --strict`, which fails on a broken
link or a missing page. Run both before you open a pull request.

## The reference is generated from the firmware

The command IDs, the frame lengths the firmware accepts, the responses it sends, the list of UART commands with
their kind, argument type and what they print are read from the STEPFOC firmware's source **at its release tag**
by `tools/sync_firmware.py`. The descriptions, units and byte layouts are written by hand in
`docs/includes/can_commands.yml` and `uart_commands.yml`, for the commands a gripper needs. The build fails when
the two disagree: a command the descriptions name and the firmware does not have, or a byte layout that does not
fit the frame.

```bash
python tools/sync_firmware.py            # write docs/includes/generated/ from firmware.tag in versions.yml
python tools/sync_firmware.py --check    # exit 1 if they are out of date
```

The tool needs a clone of the STEPFOC firmware repository with its tags, next to this repository or named by
`--firmware PATH` / `FIRMWARE_DIR`, and the network for the release notes (`--no-network` keeps the file that is
there). The CI build does not run it; the generated files are committed.

## The bill of materials is copied from the gripper repository

`docs/build/bill-of-materials.md` is the gripper repository's BOM, as it is, with its reference images shown
inline: `tools/sync_bom.py` reads a clone of the repository named in `versions.yml` (`--repo PATH`,
`$GRIPPER_REPO_DIR`, a sibling folder or `../../projects/<name>`), converts the note blocks, copies and scales the
images into `docs/assets/bom/`, and writes a header naming the commit it copied. A wrong part or a broken link is
fixed in the repository's file, then:

```bash
python tools/sync_bom.py            # rewrite the page and the images from the clone
python tools/sync_bom.py --check    # exit 1 if the page is out of date
```

## The 3D model, the Markdown twins and the "Last update" dates

`tools/build_model.py` builds `docs/assets/models/msg/` from the gripper repository's URDF (the same `--repo`
as the BOM tool; needs `trimesh` with `fast-simplification`): the body, the jaws and `viewer.json`. The landing
and dimensions pages show them in the configurator `docs/javascripts/gripper-viewer.js` (three.js from a CDN,
through the import map in `overrides/main.html`, loaded only on those pages): turn and zoom, open the jaws,
choose the colours. Run the tool again when the meshes change.

`hooks/llms.py` writes, at every build, a Markdown twin of every page next to its HTML (`…/index.md`), `llms.txt`
(an index of the twins by tab) and `llms-full.txt` (every page in one file), with links pinned to the documented release (including when publishing with mike). The "Copy this page as Markdown" button in the page header reads the twin.

The "Last update" date under every page comes from the `git-revision-date-localized` plugin (the page's last
commit; the CI checks out the whole history for it). The calculator on the Force and speed page is
`docs/javascripts/gripper-calculator.js`, driven by the data attributes and the selects of its block.

## Analytics and comments

The "Was this page helpful?" widget at the end of every page is configured under `extra.analytics.feedback`.
With `provider: google` (the Google Analytics property all the docs sites share, loaded only after the reader
accepts the cookie banner of `extra.consent`), Material's own integration records the page views and sends each
vote as an event named `feedback`.

Comments under every page come from Giscus, wired in `overrides/partials/comments.html` and configured under
`extra.comments`: all the docs sites share one Discussions home, the hub repository
`Source-Robotics/source-robotics.github.io`, with one thread per site and page. A page opts out with
`comments: false` in its front matter (the landing page does).

## The PDF of the manual

The `print-site` plugin (the last plugin in `mkdocs.yml`) builds one page with every chapter in order, a cover and
a table of contents, at `print_page/`. `hooks/pdf.py` prints that page to `site/assets/MSG-gripper-manual.pdf` with headless
Chrome when the environment variable `DOCS_PDF` is set, which the publish workflow does; a local build sets it on
demand (`DOCS_PDF=1 mkdocs build`). While the hook is on, the page-help line of every page links the PDF.

## Versions and releases

The site is versioned by **gripper release**: the version the product repository tags (`V1.1`, ...), published
under that name (`1.1`, ...). The version selector in the site's header switches between releases, and a page of
an older release says so in a bar at the top. The versions are built with [mike](https://github.com/jimporter/mike)
and kept in the `gh-pages` branch; `latest` points at the newest.

The gripper runs the STEPFOC driver's firmware, and the pages describe one firmware release (the version box
on the landing page names it). A new firmware release for the same gripper does not make a new version of the
site: the pages are updated in place, with a new revision letter.

**All version facts live in `versions.yml`, never in a page**: `docs_version` (the gripper release, which is also
the name the version is published under) with `product.tag` (`V` + `docs_version`), `firmware.version` with
`firmware.tag` (`V` + `firmware.version`), and the manual's number, title, revision, status and publication date.
`hooks/versions.py` writes them into the version box on the landing page and into the list of documents on the
About page; a malformed or missing fact stops the build.

### When the firmware releases a new version

1. Set `firmware.version` and `firmware.tag` in `versions.yml`; add a row to `compatibility.yml`, with the docs
   cell naming this site's version.
2. Run `python tools/sync_firmware.py`. If the firmware changed a gripper command, the build now fails until
   `can_commands.yml` / `uart_commands.yml` describe it: write the description.
3. Update the pages for what changed, using the release notes; give the manual a new revision letter in
   `versions.yml` and a line in its *Document history* on `docs/about.md`.
4. Commit and push to `main`. The site republishes the current version with the new firmware.

### When the gripper releases a new version

1. Set `docs_version`, `product.tag` and `product.released` in `versions.yml`, and the manual's `applies_to` if
   the hardware the manual applies to changed.
2. Update the pages for what changed in the hardware; a new revision letter and a *Document history* line.
3. Commit and push to `main`. The site publishes the new version, `latest` moves to it, and the previous
   gripper release's pages stay as they were.

### Publishing

`.github/workflows/publish.yml` publishes on every push to `main`: the tests, a strict build, then `mike deploy`
for `docs_version` with the alias `latest`. In the repository's Settings, under Pages, the source must be "Deploy
from a branch", branch `gh-pages`, folder `/ (root)`. Never run `mkdocs gh-deploy` on this repository: it would
overwrite every version mike keeps there.

The root of `gh-pages` also carries `404.html` (source: `tools/root_404.html`). It forwards addresses from before
the versioning, such as `/MSG-gripper-docs/page3_control/`, to the same page under `latest/`, where the `redirects`
plugin in `mkdocs.yml` maps the old page names to the new pages. To preview the published versions locally, with
the version selector, run `mike serve`.

## The site's address

The site is served at `https://docs.source-robotics.com/MSG-gripper-docs/`: the organisation's docs domain plus this
repository's name. Never rename this repository (its address would change and GitHub does not forward the old one),
and never add a `CNAME` file or a custom domain to it (that would take it out of the shared domain).

## License

- **Text and images:** [Creative Commons Attribution-ShareAlike 4.0](https://creativecommons.org/licenses/by-sa/4.0/),
  see [LICENSE](LICENSE). You may copy, adapt and share them, also commercially, if you credit Source Robotics and
  share your changes under the same license.
- **Code:** the [MIT license](LICENSE-CODE). This covers the code examples in the pages and the site's own code
  (hooks, tools, overrides, scripts), so you can use an example in your own program without other conditions.
- **Names and logos:** the Source Robotics name, the product names and the logos are not covered by either license.
  The gripper's hardware design is licensed separately, in the product repository.

By contributing you agree that your contribution is published under these licenses.

## Contributing

A small fix can be made from the browser: every page ends with a link to edit it on GitHub. For anything larger,
open an issue first, then a pull request. The *Contributing* page on the site has the house rules. Questions about
the gripper itself go to the product repository's issue tracker.

## Checking the page features

`python tools/test_site_features.py` checks release-pinned Markdown asset links, the prefilled issue body,
and the syntax of Python examples without running them or connecting to hardware. The CI build runs it.

`hooks/can_tools.py` generates the firmware-specific JSON/DBC downloads and the CAN frame tool from the
same `can_commands.yml` and tagged firmware facts as the reference. Keep the hook, browser codec and tests
in step across the four driver/gripper sites. The gripper status pair marks `bit_order: lsb_first` explicitly;
do not replace it with normal big-endian bit ordering.

Run `python tools/test_can_tools.py` for the schema, DBC and known wire vectors (Node.js runs the browser codec
without a browser). With `cantools==40.7.1` installed, it also loads and decodes the DBC independently; the
CI build installs this test dependency. DBC cannot select a command layout from its DLC, so the driver sites
ship separate position, velocity and current files. Never merge those into a single invented wire layout.

Motor GUI screenshots under `docs/assets/motor-gui/` were captured from the live tool on 2026-10-31.
The captions distinguish the real connection screen from simulated CAN hardware. Numbered annotations
are HTML/CSS over the original capture; refresh the captures and captions when the controls change.
