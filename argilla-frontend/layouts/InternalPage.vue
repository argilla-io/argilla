<template>
  <main class="internal-page">
    <div class="internal-page__header">
      <slot name="header">here is the header</slot>
    </div>
    <main class="internal-page__container">
      <slot name="page-header">here is the page header</slot>
      <slot name="page-content">here is the page content</slot>
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
  background: var(--bg-accent-grey-1);
  &__container {
    display: flex;
    flex-direction: column;
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
