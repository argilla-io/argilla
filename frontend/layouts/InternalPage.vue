<template>
  <main class="internal-page">
    <div class="internal-page__header">
      <slot name="header">here is the header</slot>
    </div>
    <main class="internal-page__container">
      <slot name="container">here is the header</slot>
    </main>
  </main>
</template>

<script>
export default {
  name: "InternalPage",
};
</script>

<style lang="scss" scoped>
.internal-page {
  background: palette(white);
  &__container {
    height: calc(100vh - $topbarHeight);
    overflow: auto;
    max-width: 1500px;
    padding: 0 $base-space * 8;
    margin: 0 auto;
    @include media("<desktop") {
      padding: 0 $base-space * 2;
    }
  }
}
</style>
