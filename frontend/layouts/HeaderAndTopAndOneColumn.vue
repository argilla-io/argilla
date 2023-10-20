<template>
  <div class="layout" :class="layoutClass">
    <div class="header-area">
      <slot name="header">here is the header</slot>
    </div>
    <div class="sidebar-area">
      <slot name="sidebar-right">here is the sidebar content left</slot>
    </div>
    <div class="top-area container">
      <slot name="top">here is the top content</slot>
    </div>
    <div class="center-area container">
      <slot name="center">here is the center content</slot>
    </div>
    <div class="footer-area">
      <slot name="footer">here is the footer</slot>
    </div>
  </div>
</template>

<script>
export default {
  name: "HeaderAndTopAndOneColumnsLayout",
  data: () => {
    return {
      showPanel: false,
    };
  },
  computed: {
    layoutClass() {
      return this.showPanel ? "--panel" : null;
    },
  },
  created() {
    this.$nuxt.$on("on-sidebar-toggle-panel", (value) => {
      this.showPanel = value;
    });
  },
  beforeDestroy() {
    this.$nuxt.$off("on-sidebar-toggle-panel");
  },
};
</script>

<style lang="scss" scoped>
$gap-width: $base-space * 2;
.layout {
  display: grid;
  grid-template-columns: 1fr $sidebarMenuWidth;
  grid-template-rows: auto auto minmax(0, 1fr) $base-space * 2 auto;
  grid-column-gap: 0px;
  grid-row-gap: 0px;
  height: 100vh;
  transition: 0.4s ease-in-out;
  &.--panel {
    @include media(">desktop") {
      grid-template-columns: $gap-width 1fr calc($gap-width / 2) $sidebarWidth;
      transition: 0.4s ease-out;
    }
  }
}

.header-area {
  grid-area: 1 / 1 / 2 / 3;
}
.footer-area {
  grid-area: 5 / 1 / 5 / 2;
}
.sidebar-area {
  grid-area: 2 / 2 / 5 / 3;
}
.top-area {
  grid-area: 2 / 1 / 3 / 2;
}
.center-area {
  grid-area: 3 / 1 / 4 / 2;
  min-width: 0;
}
.container {
  max-width: min(calc(100% - $base-space * 8), 1700px);
  width: 100%;
  margin: 0 auto;
  @include media("<desktopLarge") {
    max-width: min(calc(100% - $base-space * 4), 1700px);
  }
}
</style>
