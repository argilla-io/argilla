<template>
  <div>
    <NuxtChild />
  </div>
</template>

<script>
export default {
  head() {
    return {
      bodyAttrs: {
        class: [ "theme-exploration"],
      },
    };
  },
};
</script>

<style lang="scss">
.theme-exploration {
  background: $line-light-color;
}
.fixed-header {
  ::v-deep .sidebar__wrapper {
    position: fixed;
    width: 100%;
    max-width: 270px;
    max-height: calc(100% - 45px);
    overflow: auto;
    top: 3.1em;
    transition: top 0.2s ease-in-out;
    padding-right: 1em;
  }
  ::v-deep .sidebar__content {
    &:first-child {
      margin-top: 2em;
    }
  }
}
</style>
