<template>
  <div class="code">
    <pre>
      <code v-highlight class="python">{{ code }}</code>
    </pre>
    <base-action-tooltip class="code__button" tooltip="Copied">
      <a href="#" @click.prevent="copy(code)">
        <svgicon name="copy" width="16" height="16" />
      </a>
    </base-action-tooltip>
  </div>
</template>

<script>
import "assets/icons/copy";
export default {
  props: {
    code: {
      type: String,
      required: true,
    },
  },
  methods: {
    copy(code) {
      this.$copyToClipboard(code);
    },
  },
};
</script>

<style lang="scss" scoped>
.code {
  position: relative;
  white-space: normal;
  :deep(pre) {
    white-space: normal;
  }
  :deep(code) {
    white-space: pre-line;
  }
  &__button {
    position: absolute;
    top: 1em;
    right: 1em;
    svg {
      fill: palette(white);
    }
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
:deep() {
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
}
</style>
