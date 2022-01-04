<template>
  <div class="code">
    <pre>
      <code v-highlight class="python">{{code}}</code>
    </pre>
    <re-action-tooltip class="code__button" tooltip="Copied">
      <a class="breadcrumbs__copy" href="#" @click.prevent="copy(code)">
        <svgicon name="copy" width="12" height="13" />
      </a>
    </re-action-tooltip>
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
      const myTemporaryInputElement = document.createElement("textarea");
      myTemporaryInputElement.className = "hidden-input";
      myTemporaryInputElement.value = code;
      document.body.appendChild(myTemporaryInputElement);
      myTemporaryInputElement.select();
      document.execCommand("Copy");
    },
  },
};
</script>

<style lang="scss" scoped>
.code {
  position: relative;
  &__button {
    position: absolute;
    bottom: 4em;
    right: 1em;
    svg {
      fill: $lighter-color;
    }
  }
}
.hljs {
  font-family: monospace, serif;
  margin: 0;
  background-color: #333346;
  color: white;
  padding: 2em !important;
  border-radius: 5px;
  text-align: left;
  font-weight: 600;
  @include font-size(12px);
}
::v-deep {
  .hljs-keyword,
  .hljs-selector-tag,
  .hljs-literal,
  .hljs-section,
  .hljs-link {
    color: #3ef070;
    font-weight: bold;
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
