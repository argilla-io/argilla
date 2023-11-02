<template>
  <div
    class="circle-progress"
    :style="{ width: `${size}px`, height: `${size}px` }"
  >
    <div class="circle-progress__circle">
      <div
        class="circle-progress__progress"
        :style="{ transform: 'rotate(' + rotation + 'deg)' }"
      ></div>
      <div class="circle-progress__value">{{ value }}</div>
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
    size: {
      type: Number,
      default: 28,
    },
  },
  computed: {
    rotation() {
      return (this.value / 100) * 360;
    },
  },
};
</script>

<style lang="scss" scoped>
.circle-progress {
  display: flex;
  justify-content: center;
  align-items: center;
  &__circle {
    position: relative;
    width: 100%;
    height: 100%;
    border-radius: 50%;
  }
  &__progress {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    border-radius: 50%;
    border: 3px solid darken($similarity-color, 15%);
    border-top-color: transparent;
    box-sizing: border-box;
    transform-origin: center center;
  }
  &__value {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    @include font-size(12px);
    font-weight: 500;
    color: $black-54;
  }
}
</style>
