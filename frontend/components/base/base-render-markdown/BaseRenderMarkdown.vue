<template>
  <div class="markdown-render" v-html="markdownToHtml" />
</template>
<script>
import { marked } from "marked";
import * as DOMPurify from "dompurify";
export default {
  props: {
    markdown: {
      type: String,
      required: true,
    },
  },
  computed: {
    markdownToHtml() {
      const parsed = marked.parse(this.markdown);
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
</style>
