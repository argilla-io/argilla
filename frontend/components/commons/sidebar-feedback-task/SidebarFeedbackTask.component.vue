<template>
  <div class="sidebar__container">
    <SidebarFeedbackTaskPanel
      :visible-panel="currentMetric"
      :sidebar-items="sidebarItems"
      @close-panel="closePanel"
    />
    <SidebarFeedbackTask
      @on-click-sidebar-action="onClickSidebarAction"
      :sidebar-items="sidebarItems"
      :active-buttons="[currentMetric, currentMode]"
      :expanded-component="currentMetric"
    />
  </div>
</template>

<script>
export default {
  data: () => ({
    currentMetric: null,
    currentMode: "annotate",
  }),
  created() {
    this.sidebarItems = [
      {
        id: "annotate",
        tooltip: "Hand labeling",
        icon: "hand-labeling",
        group: "Mode",
        action: "change-view-mode",
        type: "non-expandable",
        relatedMetrics: ["progress", "stats"],
      },
      {
        id: "explore",
        tooltip: "Exploration",
        icon: "exploration",
        group: "Mode",
        action: "change-view-mode",
        type: "non-expandable",
        relatedMetrics: ["progress", "stats"],
      },
      {
        id: "progress",
        tooltip: "Progress",
        icon: "progress",
        action: "show-metrics",
        group: "Metrics",
        type: "expandable",
        component: "FeedbackTaskProgress",
      },
      {
        id: "stats",
        tooltip: "Stats",
        icon: "stats",
        action: "show-metrics",
        type: "expandable",
        group: "Metrics",
      },
      {
        id: "refresh",
        tooltip: "Refresh",
        icon: "refresh",
        group: "Refresh",
        type: "non-expandable",
        action: "refresh",
      },
    ];
  },
  methods: {
    onClickSidebarAction(action, info) {
      console.log(action, info);
      switch (action) {
        case "show-metrics":
          this.showMetrics(info);
          break;
        case "change-view-mode":
          console.log("change-view-mode", info);
          break;
        case "refresh":
          console.log("refresh dataset");
          break;
        default:
          console.warn(action);
      }
    },
    showMetrics(info) {
      this.currentMetric = this.currentMetric !== info ? info : null;
    },
    closePanel() {
      this.currentMetric = null;
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
  }
}
</style>
