<template>
  <iframe
    :srcdoc="template"
    ref="iframe"
    frameborder="0"
    scrolling="no"
    @load="load"
  />
</template>
<script>
/* eslint-disable */
const STYLES = `
<script>
if (parent) {
  const currentHead = document.getElementsByTagName("head")[0];
  const styles = parent.document.getElementsByTagName("style");
  for (const style of styles) {
    currentHead.appendChild(style.cloneNode(true));
  }
  const links = parent.document.querySelectorAll('link[href$=".css"]');
  for (const link of links) {
    currentHead.appendChild(link.cloneNode(true));
  }
  const html = parent.document.getElementsByTagName("html")[0];
  document.getElementsByTagName("html")[0].setAttribute("data-theme", html.getAttribute("data-theme"));
}
<\/script>
<style>
  body {
    background-color: var(--bg-field);
  }
<\/style>
`;

export default {
  props: {
    content: {
      type: String,
      required: true,
    },
  },
  methods: {
    load() {
      this.resize();
    },
    resize() {
      this.$refs.iframe.style.height =
        this.$refs.iframe.contentWindow.document.documentElement.scrollHeight +
        "px";
    },
  },
  computed: {
    template() {
      return `${STYLES}${this.content}`;
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
