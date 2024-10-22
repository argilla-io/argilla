<template>
  <div class="home">
    <div class="home__header">
      <slot name="header">here is the header</slot>
    </div>
    <div class="home__container">
      <main class="home__page-content">
        <slot name="page-content">here is the page content</slot>
      </main>
      <aside class="home__sidebar">
        <slot name="page-sidebar">here is the page sidebar</slot>
      </aside>
    </div>
  </div>
</template>

<script>
export default {
  name: "Home",
};
</script>

<style lang="scss" scoped>
.home {
  display: flex;
  flex-direction: column;
  height: 100vh;
  &__container {
    height: 100%;
    min-height: 0;
    display: flex;
  }
  &__page-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    height: 100%;
    overflow: auto;
    padding: $base-space * 4 $base-space * 4 0 $base-space * 4;
  }
  &__sidebar {
    height: 100%;
    width: 500px;
    overflow: auto;
    padding: $base-space * 4;
    background: var(--bg-opacity-4);
  }
}
</style>
