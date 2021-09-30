<template>
  <p class="tag" :style="{backgroundColor: bgColor}">{{ name }}</p>
</template>
<script>
export default {
  data: () => ({}),
  props: {
    name: {
      type: String,
      required: true
    },
    bgColor: {
      type: String,
      required: true
    },
  }
};
</script>
<style lang="scss" scoped>
.tag {
  text-align: left;
  display: inline-block;
  border: none;
  display: inline-block;
  border-radius: 10px;
  padding: 0.3em 1em;
  margin-bottom: 0.5em;
  margin-top: 0;
  word-break: break-all;
}
</style>
