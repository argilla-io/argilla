<template>
  <div
    class="circle-progress"
    :style="{ width: `${size}px`, height: `${size}px` }"
  >
    <div class="circle-progress__circle">
      <div
        class="circle-progress__progress"
        :style="{
          'background-image': `conic-gradient(${progressColor} ${
            value * 3.6
          }deg,#fafafa 0deg)`,
        }"
      ></div>
      <div class="circle-progress__value">{{ value }}</div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    progressColor: {
      type: String,
      default: "#ff675f",
    },
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
    box-sizing: border-box;
    transform-origin: center center;
  }
  &__value {
    position: absolute;
    height: calc(100% - 6px);
    width: calc(100% - 6px);
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    display: flex;
    align-items: center;
    justify-content: center;
    @include font-size(11px);
    font-weight: 500;
    color: $black-54;
    background: palette(white);
    border-radius: 50%;
  }
}
</style>
