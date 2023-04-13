<template>
  <div class="sidebar__container" :class="visibleMetric ? '--metrics' : null">
    <BaseSidebarPanel
      :class="[visibleMetric ? 'visible' : null]"
      @close-panel="onClosePanel"
    >
      <transition name="fade" appear duration="500">
        <span v-if="visibleMetric">
          <div
            v-for="metric in getMetricsByViewMode"
            :key="metric"
            v-if="visibleMetric === metric"
          >
            <component :is="getMetricComponent" />
          </div>
        </span>
      </transition>
    </BaseSidebarPanel>
    <BaseSidebarMenu
      class="sidebar__menu"
      :current-metric="visibleMetric"
      :view-mode="viewMode"
      :sidebar-items="sidebarItems"
      @click-sidebar-action="onClickSidebarAction"
    />
  </div>
</template>

<script>
export default {
  name: "SidebarFeedbaskTaskComponent",
  data: () => ({
    visibleMetric: null,
  }),
  props: {
    viewMode: {
      type: String,
      required: true,
    },
    sidebarItems: {
      type: Array,
      required: true,
    },
  },
  computed: {
    getMetricsByViewMode() {
      return (
        this.sidebarItems.find((item) => item.id === this.viewMode)
          .relatedMetrics || []
      );
    },
    getMetricComponent() {
      return (
        this.sidebarItems.find((item) => item.id === this.visibleMetric)
          ?.component || null
      );
    },
  },
  methods: {
    onClosePanel() {
      this.visibleMetric = null;
    },
    onClickSidebarAction(action, value) {
      if (action === "show-metrics") {
        this.onShowSidebarInfo(value);
      } else {
        this.$emit("on-click-sidebar-action", action, value);
      }
    },
    onShowSidebarInfo(info) {
      this.visibleMetric = this.visibleMetric !== info ? info : null;
    },
  },
};
</script>
<style lang="scss" scoped>
.sidebar {
  &__container {
    z-index: 1;
    position: fixed;
    display: flex;
    right: 0;
    pointer-events: none;
    &.--metrics {
      pointer-events: all;
    }
  }
}
</style>
