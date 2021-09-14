<template>
  <div class="loading">
    <span class="line" :style="{ minWidth: 100 }"></span>
    <div v-for="i in size" :key="i">
      <div class="record"></div>
    </div>
  </div>
</template>
<script>
export default {
  props: {
    size: {
      type: Number,
      default: 0,
    },
  },
};
</script>
<style lang="scss" scoped>
.loading {
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
.record {
  min-height: 150px;
  display: block;
  width: 100%;
  background: white;
  margin-bottom: 2px;
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
