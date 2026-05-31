const parse = require('html-react-parser').default;
const preHtml = '<pre class="shiki"><code>console.log(1)</code>';
const el = parse(preHtml);
console.log("type:", el.type);
console.log("className:", el.props.className);
