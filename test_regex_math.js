const html = `<span class="ag-math-container"><!--ag-math-start--><span class="katex">...</span><!--ag-math-end--></span>`;
const replaced = html.replace(/<(div|span) class="ag-math-container"><!--ag-math-start-->([\s\S]*?)<!--ag-math-end--><\/\1>/g, (m, tag, content) => {
  return `__MATH__${tag}__${content}__`;
});
console.log(replaced);
