# WeChat Article Pack

This folder contains publishing material for a Chinese WeChat article about Agent Search Gateway.

## Files

- `article-title.txt`: proposed article title.
- `article-wechat-ready.md`: polished Markdown draft for publishing.
- `article-wechat-ready.html`: full HTML preview with the H1 title included.
- `article-wechat-body.html`: WeChat body paste version without the H1 title.
- `article-wechat-ready-no-images.html`: full HTML preview with image placeholders.
- `article-wechat-body-no-images.html`: WeChat body paste version with image placeholders.
- `article-wechat-copy.html`: copy-only HTML body without the H1 title or helper note.
- `article-wechat-copy-no-images.html`: copy-only HTML body with image placeholders.
- `article-draft.md`: working outline and tone notes.
- `article-wechat-body-plain.txt`: short plain-text handoff note.
- `research-notes.md`: source notes, competitor/provider context, and verified project evidence.
- `image-production-pack.md`: GPT Image prompts for the article visuals.
- `render-wechat-html.mjs`: Markdown-to-inline-HTML renderer for WeChat copy/paste.
- `images/`: target directory for generated PNG images.

## Publishing Flow

1. Generate the images from `image-production-pack.md`.
2. Save them into `docs/wechat-article/images/` with the filenames listed in the prompt pack.
3. Review `article-wechat-ready.md` and update image paths if needed.
4. Regenerate HTML:

   ```bash
   node docs/wechat-article/render-wechat-html.mjs
   ```

5. Open `article-wechat-copy.html` in a browser, use Select All / Copy, and paste it into the WeChat editor body. Fill the WeChat title separately from `article-title.txt`.

If the images are not ready yet, use `article-wechat-copy-no-images.html` first. It keeps styled `图片待补` placeholders in the body so the article can be saved as a WeChat draft and updated later.

Do not include real `.env` values, API keys, Docker Hub tokens, SSH details, or raw server logs in the article.
