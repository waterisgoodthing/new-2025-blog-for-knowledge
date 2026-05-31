const html = '<pre data-code="123"><pre class="shiki"><code>code</code></pre></pre>';
const processed = html.replace(/<pre\s+data-code="([^"]*)"([^>]*)>([\s\S]*?)<\/pre>/g, (match, code, attrs, content) => {
  console.log("MATCH:", match);
  console.log("CONTENT:", content);
  return "REPLACED";
});
console.log("PROCESSED:", processed);
