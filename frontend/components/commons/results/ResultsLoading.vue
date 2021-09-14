<template>
    <div class="loading">
      <span class="line" :style="{width: `${width}%`}"></span>
    </div>
</template>
<script>
export default {
  props: {
    width: {
      type: Number,
      default: 0
    }
  },
};
</script>
<style lang="scss" scoped>
.loading {
  min-height: 100vh;
  background: white;
  position: relative;
}
.line {
  height: 2px;
  position: absolute;
  top: 0;
  left: 0;
  background: $primary-color;
  animation: load 0.5s linear infinite;
}
@keyframes load {
  0% {
      width: 0%;
  }

  100% {
      width: 100%;
  }
}
</style>
