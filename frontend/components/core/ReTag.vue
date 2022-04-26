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
  border: none;
  display: inline-block;
  border-radius: 8px;
  padding: 0.3em 1em;
  margin: 3.5px;
  max-width: 175px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  vertical-align: top;
  background: palette(grey, bg);
  @include media(">desktopLarge") {
    max-width: 200px;
  }
}
</style>
