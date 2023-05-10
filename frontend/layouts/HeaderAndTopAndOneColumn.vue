<template>
  <div class="layout" :class="layoutClass">
    <div class="header-area">
      <slot name="header">here is the header</slot>
    </div>
    <div class="empty-content-left"></div>
    <div class="footer-area">
      <slot name="footer">here is the footer</slot>
    </div>
    <div class="sidebar-area">
      <slot name="sidebar-right">here is the sidebar content left</slot>
    </div>
    <div class="top-area">
      <slot name="top">here is the top content</slot>
    </div>
    <div class="center-area">
      <slot name="center">here is the center content</slot>
    </div>
    <div class="empty-content-right"></div>
  </div>
</template>

<script>
export default {
  name: "HeaderAndTopAndOneColumnsLayout",
  data: () => {
    return {
      visibleMetrics: false,
    };
  },
  computed: {
    layoutClass() {
      return this.visibleMetrics ? "--visible-metrics" : null;
    },
  },
  created() {
    this.$nuxt.$on("on-sidebar-toggle-metrics", (value) => {
      this.visibleMetrics = value;
    });
  },
  beforeDestroy() {
    this.$nuxt.$off("on-sidebar-toggle-metrics");
  },
};
</script>

<style lang="scss" scoped>
$gap-width: $base-space * 7;
.layout {
  display: grid;
  grid-template-columns: $gap-width 1fr $gap-width $sidebarMenuWidth;
  grid-template-rows: auto auto minmax(0, 1fr) $base-space * 2 auto;
  grid-column-gap: 0px;
  grid-row-gap: 0px;
  height: 100vh;
  transition: 0.4s ease-in-out;
  &.--visible-metrics {
    @include media(">desktop") {
      grid-template-columns: $gap-width 1fr calc($gap-width / 2) $sidebarWidth;
      transition: 0.4s ease-out;
    }
  }
}

.header-area {
  grid-area: 1 / 1 / 2 / 6;
}
.empty-content-left {
  grid-area: 2 / 1 / 4 / 2;
}
.footer-area {
  grid-area: 5 / 1 / 5 / 4;
}
.sidebar-area {
  grid-area: 2 / 4 / 5 / 5;
}
.empty-content-right {
  grid-area: 2 / 3 / 4 / 4;
}
.top-area {
  grid-area: 2 / 2 / 3 / 3;
}
.center-area {
  grid-area: 3 / 2 / 4 / 3;
}
</style>
