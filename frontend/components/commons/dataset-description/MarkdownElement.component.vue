<template>
  <div v-html="parsedText" />
</template>

<script>
import { marked } from "marked";
import * as DOMPurify from 'dompurify';

export default {
  name: "MarkdownElementComponent",
  props: {
    markdown: {
      type: String,
      required: false,
    },
  },
  computed: {
    parsedText() {
      if (!this.markdown) {
        return ''
      }
      const parsed = marked.parse(this.markdown, {mangle: false, headerIds: false});
      return DOMPurify.sanitize(parsed);
    },
  },
}
</script>
