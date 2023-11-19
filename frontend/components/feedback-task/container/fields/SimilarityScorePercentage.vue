<template>
  <div>
    <div class="similarity-score">
      <div class="similarity-score__text">{{ value }}<span>%</span></div>
    </div>
  </div>
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
$size: 36px;
.similarity-score {
  width: $size;
  display: flex;
  align-items: flex-end;
  height: calc($size / 2);
  overflow: hidden;
  &__text {
    @include font-size(12px);
    line-height: 1;
    font-weight: 600;
    span {
      @include font-size(10px);
      font-weight: 400;
    }
  }
}
</style>
