<template>
  <div class="markdown-render" v-html="markdownToHtml" />
</template>
<script>
import { marked } from "marked";
import { markedHighlight } from "marked-highlight";
import hljs from "highlight.js";
import * as DOMPurify from "dompurify";
marked.use(
  markedHighlight({
    langPrefix: "hljs language-",
    highlight(code, lang) {
      const language = hljs.getLanguage(lang) ? lang : "plaintext";
      return hljs.highlight(code, { language }).value;
    },
  })
);
export default {
  props: {
    markdown: {
      type: String,
      required: true,
    },
  },
  computed: {
    markdownToHtml() {
      const parsed = marked.parse(this.markdown, {
        headerIds: false,
        mangle: false,
      });
      return DOMPurify.sanitize(parsed);
    },
  },
};
</script>
<style lang="scss">
.markdown-render {
  pre {
    overflow: scroll;
    white-space: pre-wrap;
    word-break: break-all;
  }
  a,
  p {
    word-break: break-all;
  }
  h1,
  h2,
  h3,
  h4,
  h5 {
    line-height: 1.4em;
  }
  p,
  strong,
  em,
  h1,
  h2,
  h3,
  h4,
  h5 {
    margin-top: 0;
  }
}
.hljs {
  position: relative;
  font-family: monospace, serif;
  margin: 0;
  background-color: #333346;
  color: white;
  padding: 2em !important;
  border-radius: $border-radius;
  text-align: left;
  font-weight: 500;
  @include font-size(13px);
}

.hljs-keyword,
.hljs-selector-tag,
.hljs-literal,
.hljs-section,
.hljs-link {
  color: #3ef070;
  font-weight: bold;
}
.hljs-deletion,
.hljs-number,
.hljs-quote,
.hljs-selector-class,
.hljs-selector-id,
.hljs-string,
.hljs-template-tag,
.hljs-type {
  color: #febf96;
}
.hljs-string,
.hljs-title,
.hljs-name,
.hljs-type,
.hljs-attribute,
.hljs-symbol,
.hljs-bullet,
.hljs-addition,
.hljs-variable,
.hljs-template-tag,
.hljs-template-variable {
  color: #a0c7ee;
}
.hljs-built_in {
  color: #8fbb62;
}
.hljs-tag,
.hljs-tag .hljs-attr,
.hljs-tag .hljs-name {
  color: #c0a5a5;
}
</style>
