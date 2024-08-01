<template>
  <iframe
    v-if="isHTML"
    :srcdoc="fieldText"
    ref="iframe"
    frameborder="0"
    scrolling="no"
  />
  <RenderMarkdownBaseComponent v-else :markdown="fieldText" />
</template>

<script>
export default {
  props: {
    fieldText: {
      type: String,
      required: true,
    },
    record: {
      type: Object,
      required: true,
    },
  },
  computed: {
    isHTML() {
      return /<([A-Za-z][A-Za-z0-9]*)\b[^>]*>(.*?)<\/\1>/.test(this.fieldText);
    },
  },
  methods: {
    resize() {
      this.$refs.iframe.style.height =
        this.$refs.iframe.contentWindow.document.documentElement.scrollHeight +
        450 +
        "px";
    },
  },
  mounted() {
    this.$refs.iframe.addEventListener("load", this.resize);

    setTimeout(() => {
      this.$refs.iframe.contentWindow.postMessage(
        JSON.stringify({
          ...this.record,
        }),
        "*"
      );
    }, 200);

    window.addEventListener("resize", this.resize);
  },
};
</script>

<style>
iframe {
  border: none;
  width: 100%;
}
</style>
