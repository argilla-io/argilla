<template>
  <div class="container">
    <p class="badge" v-for="id in range" :key="id" />
  </div>
</template>

<script>
export default {
  props: {
    quantity: {
      type: Number,
      default: 1,
    },
  },
  computed: {
    range() {
      return Array.from({ length: this.quantity }, (_, i) => i);
    },
  },
};
</script>

<style lang="scss" scoped>
$progressBackgroundColor: #f2f2f2;

.container {
  display: flex;
  align-items: center;
  gap: 5px;
}

.badge {
  height: $base-space * 3;
  width: 5em;
  padding: 1em;
  border-radius: $border-radius-rounded;
  margin: 0;
  color: $black-54;
  @include font-size(12px);
  @include line-height(12px);
  border: unset;

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
}

@keyframes skeletonBg {
  0% {
    background-position: 100% 0;
  }
  100% {
    background-position: -100% 0;
  }
}
</style>
