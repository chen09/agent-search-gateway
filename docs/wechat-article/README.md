# WeChat Article Pack

This folder contains publishing material for a Chinese WeChat article about Agent Search Gateway.

## Files

- `article-title.txt`: proposed article title.
- `article-wechat-ready.md`: polished Markdown draft for publishing.
- `article-draft.md`: working outline and tone notes.
- `article-wechat-body-plain.txt`: short plain-text handoff note.
- `research-notes.md`: source notes, competitor/provider context, and verified project evidence.
- `image-production-pack.md`: GPT Image prompts for the article visuals.
- `images/`: target directory for generated PNG images.

## Publishing Flow

1. Generate the images from `image-production-pack.md`.
2. Save them into `docs/wechat-article/images/` with the filenames listed in the prompt pack.
3. Review `article-wechat-ready.md` and update image paths if needed.
4. Copy the final article body into WeChat editor.

Do not include real `.env` values, API keys, Docker Hub tokens, SSH details, or raw server logs in the article.
