<template>
  <div class="container">
    <h2 class="title">
      {{ title }} records ({{ dataset.results.total }})
    </h2>
  </div>
</template>

<script>
export default {
  props: {
    dataset: {
      default: () => {},
      type: Object,
    },
    title: {
      type: String,
      required: true,
    }
  }
};
</script>
<style lang="scss" scoped>
.container {
  @extend %container;
  padding-top: 1em;
  padding-bottom: 0;
  .fixed-header & {
    display: none;
  }
}
.title {
  font-weight: normal;
  @include font-size(16px);
  color: $font-secondary-dark;
  white-space: nowrap;
  display: flex;
  margin: 0.5em 0;
  align-items: center;
}
</style>
