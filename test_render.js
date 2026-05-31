import { renderMarkdown } from './src/lib/markdown-renderer.ts';
async function test() {
  const md = "```js\nconsole.log(1)\n```\n\n```mermaid\ngraph TD\nA-->B\n```";
  const res = await renderMarkdown(md);
  console.log(res.html);
}
test();
