<template>
  <div class="donut-chart" :style="pieStyles"></div>
</template>

<script>
export default {
  props: {
    size: {
      type: Number,
      default: 60,
    },
    slices: {
      type: Array,
      default: () => [],
    },
  },
  computed: {
    pieStyles() {
      let acum = 0;
      const styles = this.slices.map(
        (slice) => `${slice.color} 0 ${(acum += slice.percent)}%`
      );

      return {
        background: `radial-gradient(#fafafa 40%, transparent 41%), conic-gradient( ${styles.join(
          ","
        )} )`,
      };
    },
    sizeStyles() {
      return `${this.size}px`;
    },
  },
};
</script>

<style scoped lang="scss">
@property --a {
  syntax: "<angle>";
  inherits: false;
  initial-value: 360deg;
}
.donut-chart {
  position: relative;
  width: v-bind(sizeStyles);
  height: v-bind(sizeStyles);
  border-radius: 50%;
  overflow: hidden;
  &:before {
    --a: 360deg;
    content: "";
    position: absolute;
    width: 102%;
    height: 102%;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-image: conic-gradient(
      transparent var(--a),
      var(--bg-accent-grey-1) 0deg
    );
    animation: progress 0.5s ease-in-out;
  }
}

@keyframes progress {
  1% {
    --a: 0deg;
  }
  100% {
    --a: 360deg;
  }
}
</style>
