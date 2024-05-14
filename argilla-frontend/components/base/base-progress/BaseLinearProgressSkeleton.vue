<template>
  <div class="progress__wrapper">
    <div class="progress__skeleton"></div>
  </div>
</template>

<script>
export default {};
</script>

<styles lang="scss" scoped>
$progressHeight: 12px;
$progressBackgroundColor: #f2f2f2;
$borderRadius: 10px;

.progress__wrapper {
  height: $progressHeight;
  border-radius: $borderRadius;
}
.progress__skeleton {
  position: absolute;
  left: 0;
  top: 0;
  width: 100%;
  height: $progressHeight;
  animation-duration: 1s;
  animation-fill-mode: forwards;
  animation-iteration-count: infinite;
  animation-name: skeletonBg;
  animation-timing-function: cubic-bezier(0.2, 0.7, 0.8, 0.7);
  background: $progressBackgroundColor;
  background: linear-gradient(
    to right,
    $progressBackgroundColor 0%,
    darken($progressBackgroundColor, 10%) 50%,
    $progressBackgroundColor 100%
  );
  background-size: 200% 100%;
  border-radius: $borderRadius;
}

@keyframes skeletonBg {
  0% {
    background-position: 100% 0;
  }
  100% {
    background-position: -100% 0;
  }
}
</styles>
