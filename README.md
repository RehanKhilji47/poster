# poster — image host for published articles

## ⚠️ DO NOT DELETE, RENAME, OR MOVE ANYTHING IN `images/`

Every file in this repo is **hotlinked from live, published articles** on external
platforms (WordPress, Medium, LinkedIn, client sites). These are not backups or
drafts. They are production assets.

If a file here is deleted, renamed, or moved, **images silently break in already
published articles** that can no longer be edited or re-uploaded easily. There is
no warning and no error — the image just disappears for every reader.

### The rules

1. **Never delete a file.** Even if an article is unpublished. Even if it looks unused.
2. **Never rename or move a file.** The URL is the filename. Change it, break it.
3. **Never make this repository private.** Private repos do not serve raw URLs.
   Every image in every article dies instantly.
4. **Never rename the `main` branch.** The branch name is in every URL.
5. **Never force-push.** It can orphan the commits the URLs point at.
6. **Additions only.** New article? New folder. Wrong image? Upload a *new* file
   under a *new* name and update the article — do not overwrite in place.

### To update an image that is already live

Do not replace the file. Instead:

- Upload the corrected image under a new name (e.g. `-v2` suffix), **or**
- If you must reuse the same filename, bump the cache-buster in the article URL
  (`?v=1` → `?v=2`) so platforms re-fetch instead of serving a stale copy.

### URL format

```
https://raw.githubusercontent.com/RehanKhilji47/poster/main/images/<folder>/<file>?v=1
```

If an article gets heavy traffic, switch the host to jsDelivr (a real CDN, free,
mirrors any public GitHub repo). Same path, different domain:

```
https://cdn.jsdelivr.net/gh/RehanKhilji47/poster@main/images/<folder>/<file>
```

### Contents

| Folder | Used by |
|---|---|
| `images/national-teams-anime/` | national teams anime article |
| `images/photo-to-soccer-anime/` | "I Tried to Turn a Photo Into a Soccer Anime Character" |
| `images/pixai-prompt-troubleshooting/` | "Why Your AI Anime Prompt Is Not Working — and How to Fix It in PixAI" |
