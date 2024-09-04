<template>
  <div class="similarity-score">{{ value }}<span>%</span></div>
</template>

<script>
export default {
  props: {
    value: {
      type: Number,
      required: true,
      validator: (value) => value >= 0 && value <= 100,
    },
  },
};
</script>
<style scoped lang="scss">
.similarity-score {
  color: var(--fg-similarity);
  @include font-size(12px);
  line-height: 1;
  font-weight: 600;
  span {
    @include font-size(10px);
    font-weight: 400;
  }
}
</style>
