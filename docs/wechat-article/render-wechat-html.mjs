import fs from "node:fs";
import path from "node:path";

const root = new URL(".", import.meta.url).pathname;
const sourcePath = path.join(root, "article-wechat-ready.md");
const fullOutputPath = path.join(root, "article-wechat-ready.html");
const bodyOutputPath = path.join(root, "article-wechat-body.html");

const md = fs.readFileSync(sourcePath, "utf8");
const title =
  md
    .split(/\r?\n/)
    .find((line) => line.startsWith("# "))
    ?.slice(2)
    .trim() || "Agent Search Gateway";

function escapeHtml(text) {
  return text
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function inlineMarkdown(text) {
  let out = escapeHtml(text);
  out = out.replace(/\[([^\]]+)\]\((https?:\/\/[^)]+)\)/g, "$1：$2");
  out = out.replace(
    /`([^`]+)`/g,
    '<code style="font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; background: #f3f4f6; color: #0f172a; border-radius: 4px; padding: 1px 5px; font-size: 0.92em;">$1</code>',
  );
  out = out.replace(
    /\*\*([^*]+)\*\*/g,
    '<strong style="font-weight: 700; color: #111827;">$1</strong>',
  );
  return out;
}

function paragraphHtml(text) {
  if (
    text.includes("GitHub：chen09") ||
    text.includes("Docker Hub：chen920") ||
    text.includes("docker.io/chen920/agent-search-gateway") ||
    text.includes("api.agentsearchgateway.com")
  ) {
    return `<p style="margin: 22px 0; padding: 14px 16px; line-height: 1.8; font-size: 16px; color: #1e3a8a; background: #eff6ff; border: 1px solid #bfdbfe; border-left: 5px solid #2563eb; border-radius: 8px;">${inlineMarkdown(text)}</p>`;
  }
  return `<p style="margin: 18px 0; line-height: 1.95; font-size: 16px; color: #263244;">${inlineMarkdown(text)}</p>`;
}

function imageHtml(alt, src) {
  const cleanAlt = escapeHtml(alt);
  const cleanSrc = escapeHtml(src);
  return [
    '<figure style="margin: 30px 0 18px; padding: 0;">',
    `<img src="${cleanSrc}" alt="${cleanAlt}" style="display: block; width: 100%; max-width: 100%; height: auto; border-radius: 8px; border: 1px solid #e5e7eb; box-shadow: 0 10px 28px rgba(15, 23, 42, 0.08);" />`,
    "</figure>",
  ].join("\n");
}

function codeBlockHtml(code, language) {
  const label = language ? `<span style="display: block; margin: 0 0 8px; color: #94a3b8; font-size: 13px;">${escapeHtml(language)}</span>` : "";
  return [
    '<pre style="box-sizing: border-box; margin: 20px 0; padding: 14px 16px; overflow-x: auto; white-space: pre-wrap; word-break: break-word; background: #0f172a; color: #e5e7eb; border-radius: 8px; font-size: 13px; line-height: 1.75; font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;">',
    `${label}<code>${escapeHtml(code)}</code>`,
    "</pre>",
  ].join("\n");
}

function flushParagraph(buffer, html) {
  if (buffer.length) {
    html.push(paragraphHtml(buffer.join(" ")));
    buffer.length = 0;
  }
}

function closeList(listOpen, html) {
  if (listOpen.value) {
    html.push("</ul>");
    listOpen.value = false;
  }
}

function renderMarkdown(markdown, { includeTitle }) {
  const html = [];
  const paragraph = [];
  const listOpen = { value: false };
  let skippingComment = false;
  let skippedFirstH1 = false;
  let inCodeBlock = false;
  let codeLanguage = "";
  let codeLines = [];

  for (const rawLine of markdown.split(/\r?\n/)) {
    const line = rawLine.trim();

    if (inCodeBlock) {
      if (line.startsWith("```")) {
        html.push(codeBlockHtml(codeLines.join("\n"), codeLanguage));
        inCodeBlock = false;
        codeLanguage = "";
        codeLines = [];
      } else {
        codeLines.push(rawLine);
      }
      continue;
    }

    if (line.startsWith("```")) {
      flushParagraph(paragraph, html);
      closeList(listOpen, html);
      inCodeBlock = true;
      codeLanguage = line.slice(3).trim();
      codeLines = [];
      continue;
    }

    if (skippingComment) {
      if (line.includes("-->")) skippingComment = false;
      continue;
    }
    if (line.startsWith("<!--")) {
      if (!line.includes("-->")) skippingComment = true;
      continue;
    }

    if (!line) {
      flushParagraph(paragraph, html);
      closeList(listOpen, html);
      continue;
    }

    const image = line.match(/^!\[([^\]]*)\]\(([^)]+)\)$/);
    if (image) {
      flushParagraph(paragraph, html);
      closeList(listOpen, html);
      html.push(imageHtml(image[1], image[2]));
      continue;
    }

    if (line.startsWith("# ")) {
      flushParagraph(paragraph, html);
      closeList(listOpen, html);
      if (!includeTitle && !skippedFirstH1) {
        skippedFirstH1 = true;
        continue;
      }
      html.push(`<h1 style="margin: 0 0 18px; line-height: 1.25; font-size: 30px; font-weight: 800; color: #0f172a;">${inlineMarkdown(line.slice(2))}</h1>`);
      continue;
    }

    if (line.startsWith("## ")) {
      flushParagraph(paragraph, html);
      closeList(listOpen, html);
      html.push(`<h2 style="margin: 42px 0 16px; padding-left: 12px; border-left: 5px solid #2563eb; line-height: 1.35; font-size: 22px; font-weight: 800; color: #102a43;">${inlineMarkdown(line.slice(3))}</h2>`);
      continue;
    }

    if (line.startsWith("### ")) {
      flushParagraph(paragraph, html);
      closeList(listOpen, html);
      html.push(`<h3 style="margin: 28px 0 12px; line-height: 1.4; font-size: 18px; font-weight: 800; color: #1f2937;">${inlineMarkdown(line.slice(4))}</h3>`);
      continue;
    }

    if (line.startsWith("- ")) {
      flushParagraph(paragraph, html);
      if (!listOpen.value) {
        html.push('<ul style="margin: 16px 0 20px; padding-left: 22px; color: #263244; line-height: 1.9; font-size: 16px;">');
        listOpen.value = true;
      }
      html.push(`<li style="margin: 6px 0;">${inlineMarkdown(line.slice(2))}</li>`);
      continue;
    }

    const numbered = line.match(/^\d+\.\s+(.+)$/);
    if (numbered) {
      flushParagraph(paragraph, html);
      closeList(listOpen, html);
      html.push(`<p style="margin: 10px 0; line-height: 1.9; font-size: 16px; color: #263244;">${inlineMarkdown(line)}</p>`);
      continue;
    }

    paragraph.push(line);
  }

  if (inCodeBlock) {
    html.push(codeBlockHtml(codeLines.join("\n"), codeLanguage));
  }
  flushParagraph(paragraph, html);
  closeList(listOpen, html);
  return html.join("\n");
}

function page(content, pageTitle, copyHint) {
  return `<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>${escapeHtml(pageTitle)}</title>
</head>
<body style="margin: 0; background: #f8fafc; color: #263244;">
  <div style="max-width: 760px; margin: 0 auto; padding: 24px 18px 48px;">
    <div style="margin: 0 0 20px; padding: 12px 14px; border: 1px solid #dbeafe; background: #eff6ff; border-radius: 8px; color: #1e3a8a; font-size: 14px; line-height: 1.7; font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', sans-serif;">
      ${escapeHtml(copyHint)}
    </div>
    <article id="wechat-article" style="box-sizing: border-box; max-width: 680px; margin: 0 auto; padding: 0; background: #ffffff; font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', sans-serif;">
${content}
    </article>
  </div>
</body>
</html>
`;
}

const fullHtml = page(
  renderMarkdown(md, { includeTitle: true }),
  title,
  "预览版：包含正文标题。若粘贴到公众号正文，请从白色正文区域开始选择复制。",
);

const bodyHtml = page(
  renderMarkdown(md, { includeTitle: false }),
  "公众号正文粘贴版",
  "推荐粘贴版：不包含 H1 标题。公众号标题请单独填写，正文从头图开始复制。",
);

fs.writeFileSync(fullOutputPath, fullHtml);
fs.writeFileSync(bodyOutputPath, bodyHtml);

console.log(`wrote ${fullOutputPath}`);
console.log(`wrote ${bodyOutputPath}`);
