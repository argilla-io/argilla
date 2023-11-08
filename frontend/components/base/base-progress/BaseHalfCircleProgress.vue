<template>
  <div class="half-circle-progree-wrapper">
    <div class="half-circle-progress">
      <div
        class="half-circle-progress__fill"
        :style="{ transform: `rotate(${rotation}deg)` }"
      ></div>
      <div class="half-circle-progress__text">{{ value }}</div>
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
  computed: {
    rotation() {
      return 45 + this.value * 1.8;
    },
  },
};
</script>
<style scoped lang="scss">
$progress-color: palette(orange-red-crayola);
$size: 34px;
$progress-size: 2px;
.half-circle-progress {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: flex-end;
  width: $size;
  height: calc($size / 2);
  border-radius: calc($size / 2) calc($size / 2) 0 0;
  overflow: hidden;
  &__fill {
    position: absolute;
    top: 0;
    left: 0;
    width: $size;
    height: $size;
    border-radius: 50%;
    box-sizing: border-box;
    border: $progress-size solid #eee;
    border-bottom-color: $progress-color;
    border-right-color: $progress-color;
  }
  &__text {
    @include font-size(10px);
    color: $black-54;
    line-height: 1;
  }
}
</style>
