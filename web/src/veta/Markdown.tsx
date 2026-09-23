import type { ReactNode } from "react";

// A small markdown renderer for the tenets document -- paragraphs, headings,
// block quotes, nested lists, tables, fenced code and the inline marks the
// document actually uses (`code`, **bold**, *italic*, [links](url)). It builds
// React elements; no HTML string is ever injected.
//
// A code span naming a V_eta class the tree really has is rendered as a link
// to that class, so a tenet's examples lead straight to their schemas. Whether
// a name is a class is the caller's question (`isClass`), answered from the
// schema tree -- this file knows no class names.

interface Props {
  source: string;
  isClass?: (name: string) => boolean;
  onClass?: (name: string) => void;
}

export function Markdown({ source, isClass, onClass }: Props) {
  const ctx = { isClass, onClass };
  return <>{blocks(source.split(/\r?\n/), ctx, "b")}</>;
}

type Ctx = Pick<Props, "isClass" | "onClass">;

const LIST_RE = /^(\s*)([-*+]|\d+\.)\s+(.*)$/;

function blocks(lines: string[], ctx: Ctx, keyBase: string): ReactNode[] {
  const out: ReactNode[] = [];
  let i = 0;
  let k = 0;
  const key = () => `${keyBase}-${k++}`;
  while (i < lines.length) {
    const line = lines[i];
    if (!line.trim()) {
      i++;
      continue;
    }
    // fenced code
    if (/^\s*```/.test(line)) {
      const body: string[] = [];
      i++;
      while (i < lines.length && !/^\s*```/.test(lines[i])) body.push(lines[i++]);
      i++;
      out.push(
        <pre key={key()} className="md-pre">
          {body.join("\n")}
        </pre>,
      );
      continue;
    }
    // heading
    const h = /^(#{1,6})\s+(.*)$/.exec(line);
    if (h) {
      const level = Math.min(6, h[1].length + 1);
      const Tag = `h${level}` as "h4";
      out.push(
        <Tag key={key()} className="md-heading">
          {inline(h[2], ctx)}
        </Tag>,
      );
      i++;
      continue;
    }
    // horizontal rule
    if (/^\s*-{3,}\s*$/.test(line)) {
      out.push(<hr key={key()} />);
      i++;
      continue;
    }
    // block quote
    if (/^\s*>/.test(line)) {
      const body: string[] = [];
      while (i < lines.length && /^\s*>/.test(lines[i]))
        body.push(lines[i++].replace(/^\s*> ?/, ""));
      out.push(
        <blockquote key={key()} className="md-quote">
          {blocks(body, ctx, key())}
        </blockquote>,
      );
      continue;
    }
    // table
    if (/^\s*\|/.test(line)) {
      const rows: string[][] = [];
      while (i < lines.length && /^\s*\|/.test(lines[i])) {
        const cells = lines[i]
          .trim()
          .replace(/^\||\|$/g, "")
          .split("|")
          .map((c) => c.trim());
        if (!cells.every((c) => /^:?-+:?$/.test(c))) rows.push(cells);
        i++;
      }
      const [head, ...body] = rows;
      out.push(
        <table key={key()} className="fields-table md-table">
          <thead>
            <tr>
              {head.map((c, j) => (
                <th key={j}>{inline(c, ctx)}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {body.map((r, ri) => (
              <tr key={ri}>
                {r.map((c, j) => (
                  <td key={j}>{inline(c, ctx)}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>,
      );
      continue;
    }
    // list
    if (LIST_RE.test(line)) {
      const start = i;
      while (
        i < lines.length &&
        lines[i].trim() &&
        (LIST_RE.test(lines[i]) || /^\s+\S/.test(lines[i]))
      )
        i++;
      // A blank line followed by another item continues the same list.
      while (i + 1 < lines.length && !lines[i]?.trim() && LIST_RE.test(lines[i + 1])) {
        i++;
        while (
          i < lines.length &&
          lines[i].trim() &&
          (LIST_RE.test(lines[i]) || /^\s+\S/.test(lines[i]))
        )
          i++;
      }
      out.push(list(lines.slice(start, i).filter((l) => l.trim()), ctx, key()));
      continue;
    }
    // paragraph
    const para: string[] = [];
    while (
      i < lines.length &&
      lines[i].trim() &&
      !/^\s*(```|>|\||#{1,6}\s)/.test(lines[i]) &&
      !(para.length > 0 && LIST_RE.test(lines[i]))
    )
      para.push(lines[i++].trim());
    out.push(
      <p key={key()} className="md-p">
        {inline(para.join(" "), ctx)}
      </p>,
    );
  }
  return out;
}

interface Item {
  indent: number;
  ordered: boolean;
  text: string[];
  children: Item[];
}

function list(lines: string[], ctx: Ctx, keyBase: string): ReactNode {
  const root: Item = { indent: -1, ordered: false, text: [], children: [] };
  const stack: Item[] = [root];
  let last: Item | null = null;
  for (const line of lines) {
    const m = LIST_RE.exec(line);
    if (!m) {
      if (last) last.text.push(line.trim());
      continue;
    }
    const indent = m[1].length;
    while (stack.length > 1 && stack[stack.length - 1].indent >= indent) stack.pop();
    const item: Item = {
      indent,
      ordered: /\d/.test(m[2]),
      text: [m[3]],
      children: [],
    };
    stack[stack.length - 1].children.push(item);
    stack.push(item);
    last = item;
  }
  return renderItems(root.children, ctx, keyBase);
}

function renderItems(items: Item[], ctx: Ctx, keyBase: string): ReactNode {
  const ordered = items[0]?.ordered;
  const Tag = ordered ? "ol" : "ul";
  return (
    <Tag key={keyBase} className="md-list">
      {items.map((it, j) => (
        <li key={j}>
          {inline(it.text.join(" "), ctx)}
          {it.children.length > 0 && renderItems(it.children, ctx, `${keyBase}-${j}`)}
        </li>
      ))}
    </Tag>
  );
}

// `code` | **bold** | *italic* | [text](url)
const INLINE_RE = /(`[^`]+`)|(\*\*[^*]+?\*\*)|(\*[^*\s][^*]*?\*)|(\[[^\]]+\]\([^)\s]+\))/g;

function inline(text: string, ctx: Ctx): ReactNode[] {
  const out: ReactNode[] = [];
  let last = 0;
  let k = 0;
  for (const m of text.matchAll(INLINE_RE)) {
    const idx = m.index ?? 0;
    if (idx > last) out.push(text.slice(last, idx));
    const tok = m[0];
    if (m[1]) {
      const code = tok.slice(1, -1);
      if (ctx.isClass?.(code) && ctx.onClass) {
        out.push(
          <button
            key={k++}
            type="button"
            className="md-class-link"
            title={`Open V_eta class ${code}`}
            onClick={() => ctx.onClass!(code)}
          >
            <code>{code}</code>
          </button>,
        );
      } else out.push(<code key={k++}>{code}</code>);
    } else if (m[2]) out.push(<strong key={k++}>{inline(tok.slice(2, -2), ctx)}</strong>);
    else if (m[3]) out.push(<em key={k++}>{inline(tok.slice(1, -1), ctx)}</em>);
    else if (m[4]) {
      const lm = /^\[([^\]]+)\]\(([^)\s]+)\)$/.exec(tok)!;
      const href = /^https?:\/\//.test(lm[2]) ? lm[2] : undefined;
      out.push(
        href ? (
          <a key={k++} href={href} target="_blank" rel="noreferrer">
            {inline(lm[1], ctx)}
          </a>
        ) : (
          <span key={k++}>{inline(lm[1], ctx)}</span>
        ),
      );
    }
    last = idx + tok.length;
  }
  if (last < text.length) out.push(text.slice(last));
  return out;
}
