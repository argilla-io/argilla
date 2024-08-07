<template>
  <div class="status-counter"></div>
</template>

<style scoped lang="scss">
$progressBackgroundColor: #f2f2f2;
.status-counter {
  background: $black-3;
  border-radius: $border-radius;
  animation-duration: 0.5s;
  animation-fill-mode: forwards;
  animation-iteration-count: infinite;
  animation-name: skeletonBg;
  animation-timing-function: cubic-bezier(0.2, 0.7, 0.8, 0.7);
  background: linear-gradient(
    to right,
    $progressBackgroundColor 0%,
    darken($progressBackgroundColor, 3%) 50%,
    $progressBackgroundColor 100%
  );
  background-size: 200% 100%;

  @keyframes skeletonBg {
    0% {
      background-position: 100% 0;
    }
    100% {
      background-position: -100% 0;
    }
  }
}
</style>