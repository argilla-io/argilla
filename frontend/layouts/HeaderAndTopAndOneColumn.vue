<template>
  <div class="layout" :class="layoutClass">
    <div class="header-area">
      <slot name="header">here is the header</slot>
    </div>
    <div class="sidebar-area">
      <slot name="sidebar-right">here is the sidebar content left</slot>
    </div>
    <div class="center-area">
      <slot name="center">here is the center content</slot>
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
  grid-template-rows: auto minmax(0, 1fr) auto;
  grid-column-gap: 0px;
  grid-row-gap: 0px;
  grid-template-areas:
    "header header"
    "center sidebar";
  height: 100vh;
  transition: 0.4s ease-in-out;
  &.--panel {
    @include media(">desktop") {
      grid-template-columns: 1fr $sidebarWidth;
      transition: 0.4s ease-out;
    }
  }
}

.header-area {
  grid-area: header;
}
.sidebar-area {
  grid-area: sidebar;
}
.center-area {
  grid-area: center;
  min-width: 0;
}
</style>
