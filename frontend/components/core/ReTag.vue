<template>
  <p :title="name" class="tag" :style="{backgroundColor: bgColor}">{{ name }}</p>
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
  border: none;
  display: inline-block;
  border-radius: 10px;
  padding: 0.3em 1em;
  margin-bottom: 0.5em;
  margin-left: 0.5em;
  margin-top: 0;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
