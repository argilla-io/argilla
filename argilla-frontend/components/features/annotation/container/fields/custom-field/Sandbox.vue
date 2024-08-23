<template>
  <iframe
    :srcdoc="content"
    ref="iframe"
    frameborder="0"
    scrolling="no"
    @load="resize"
  />
</template>

<script>
export default {
  props: {
    content: {
      type: String,
      required: true,
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
};
</script>

<style>
iframe {
  border: none;
  width: 100%;
}
</style>
