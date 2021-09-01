<template>
  <div class="pie" :style="{ animationDelay: `${-percent}s` }">
    {{ percent }}%
  </div>
</template>
<script>
export default {
  props: {
    percent: {
      type: Number,
      required: true,
    },
  },
};
</script>

<style lang="scss" scoped>
@keyframes spin {
  to {
    transform: rotate(0.5turn);
  }
}
@keyframes bg {
  50% {
    background: #ff541e;
  }
}
.pie {
  position: relative;
  width: 100px;
  line-height: 100px;
  border-radius: 50%;
  background: #50cb88;
  color: transparent;
  text-align: center;
  background-image: linear-gradient(to right, transparent 50%, #ff541e 0);
  transform-origin: left;
  &:before {
    content: "";
    position: absolute;
    top: 0;
    left: 50%;
    width: 50%;
    height: 100%;
    border-radius: 0 100% 100% 0 / 50%;
    background-color: inherit;
    transform-origin: left;
    animation: spin 50s linear infinite, bg 100s step-end infinite;
    animation-play-state: paused;
    animation-delay: inherit;
  }
}
</style>
