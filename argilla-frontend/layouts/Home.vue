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
  overflow: auto;
  @include media(">tablet") {
    overflow: visible;
  }
  &__container {
    flex-direction: column;
    height: 100%;
    min-height: 0;
    display: flex;
    @include media(">tablet") {
      flex-direction: row;
    }
  }
  &__page-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    height: 100%;
    padding: $base-space * 4;
    background: var(--bg-accent-grey-1);
    @include media(">tablet") {
      overflow: auto;
      padding: $base-space * 4 $base-space * 4 0 $base-space * 4;
    }
  }
  &__sidebar {
    display: flex;
    flex-direction: column;
    gap: $base-space * 4;
    height: 100%;
    width: 100%;
    padding: $base-space * 4;
    background: var(--bg-accent-grey-3);
    @include media(">tablet") {
      width: clamp(300px, 36vw, 600px);
    }
  }
}
</style>
