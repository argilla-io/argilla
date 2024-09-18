<template>
  <p :title="name" class="tag">{{ name }}</p>
</template>
<script>
export default {
  data: () => ({}),
  props: {
    name: {
      type: String,
      required: true,
    },
  },
};
</script>
<style lang="scss" scoped>
.tag {
  text-align: left;
  border: 1px solid var(--bg-opacity-10);
  display: inline-block;
  border-radius: 20px;
  padding: 0.2em 0.8em;
  margin: 3.5px;
  max-width: 175px;
  vertical-align: top;
  color: var(--fg-secondary);
  word-break: break-word;
  hyphens: auto;
  @include font-size(12px);
  @include media(">desktopLarge") {
    max-width: 200px;
  }
}
</style>
