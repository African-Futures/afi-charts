# Publishing an AFI chart — the short version

Each chart is **one self-contained HTML file**. Nothing else is needed: no build, no install, no dependencies to manage. Publishing means putting that file somewhere with a web address, and GitHub Pages is where we do that.

If you are covering for someone and have never used GitHub, you can do everything below in a browser. You do not need to install anything or use a command line.

---

## One-time setup (already done — for reference only)

1. The repository `afi-charts` under the `african-futures` account, set to **Public**. Pages requires public on a free plan.
2. In the repository: **Settings → Pages → Source: Deploy from a branch → `main` / root → Save**.
3. The site is live at **https://african-futures.github.io/afi-charts/** — this is the base for every chart URL.

Do not repeat these steps for each chart. They happen once for the whole repository.

---

## Publishing a new chart

1. Go to the `afi-charts` repository on github.com.
2. Click **Add file → Upload files**.
3. Drag the chart's `.html` file in.
4. In the box at the bottom, write one line saying what it is — "Median age chart for Kyle's September blog".
5. Click **Commit changes**.

The chart is live about a minute later at:

```
https://african-futures.github.io/afi-charts/<file-name>.html
```

So `median-age.html` becomes `.../afi-charts/median-age.html`. Open that URL in a browser to check it before embedding.

## Embedding it in OpenCMS

In the article editor, paste this. **Wrap the iframe in a `<div>`** — OpenCMS wraps a bare iframe in a `<p>`, which indents it and adds paragraph spacing. A `<div>` is left alone, so the chart aligns with the body text.

```html
<div style="width:100%;margin:1.6em 0 0.9em;">
<iframe src="https://african-futures.github.io/afi-charts/median-age.html"
        title="Median age in selected African countries, 1960-2050"
        loading="lazy" scrolling="no"
        style="display:block;width:100%;height:660px;border:0;padding:0;margin:0;"></iframe>
</div>
```

Change three things per chart: the URL, the `title`, and the height.

**The height is measured per chart, never guessed.** Ask for it when the chart is built. Too small and it silently clips the source line off the bottom — the article still looks fine, so nobody notices the attribution has gone. 660 suits a standard line chart; a longer subtitle or more series needs more. Measured heights for the bar and column forms are in `afi-bar-and-column-decisions.md`.

`title` matters for screen readers — use the chart's real title.

If the CMS strips `style` attributes, fall back to plain `width` and `height` attributes on the iframe and ask the web team for a CSS rule covering iframes in article bodies.

## Updating a chart

Upload the new file with **exactly the same file name** and commit. The URL does not change, so every article already embedding it picks up the new version automatically. Give it a minute and refresh.

---

## Two rules that matter

**Never rename or delete a published file.** The file name is the web address, and that address is baked into every article that embeds the chart. Renaming `median-age.html` breaks every one of those articles silently — the chart just disappears from the page. If a chart genuinely needs replacing, upload the new one under a new name and leave the old file alone.

**Use plain file names.** Lower case, hyphens instead of spaces, no accents: `median-age.html`, not `Median Age (final v2).html`. Spaces and punctuation break URLs in ways that are annoying to unpick later.

---

## If something looks wrong

- **Chart is blank in the article but fine on GitHub** — OpenCMS has probably stripped the iframe. That is a CMS permissions question for the web team, not a chart problem.
- **Chart is blank on GitHub too** — the file may still be deploying. Wait two minutes and hard-refresh. If it persists, check **Actions** in the repository for a failed deployment.
- **Chart is cut off at the bottom** — increase the iframe `height`.
- **Fonts look wrong** — the page loads Open Sans from Google Fonts. On a network that blocks Google Fonts it falls back to a system face; the chart still works.
