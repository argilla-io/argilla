<template>
  <div class="sidebar__container">
    <SidebarFeedbackTaskPanel v-if="isPanelVisible" @close-panel="closePanel">
      <component v-if="getProgressComponentName" :is="getProgressComponentName"
    /></SidebarFeedbackTaskPanel>
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
  computed: {
    getProgressComponentName() {
      return (
        this.sidebarItems.metrics.buttons.find(
          ({ id }) => id === this.currentMetric
        )?.component || null
      );
    },
    isPanelVisible() {
      return !!this.currentMetric;
    },
  },
  created() {
    this.sidebarItems = {
      mode: {
        buttonType: "non-expandable",
        buttons: [
          {
            id: "annotate",
            tooltip: "Hand labeling",
            icon: "hand-labeling",
            action: "change-view-mode",
            relatedMetrics: ["progress", "stats"],
          },
          {
            id: "explore",
            tooltip: "Exploration",
            icon: "exploration",
            action: "change-view-mode",
            relatedMetrics: ["progress", "stats"],
          },
        ],
      },
      metrics: {
        buttonType: "expandable",
        buttons: [
          {
            id: "progress",
            tooltip: "Progress",
            icon: "progress",
            action: "show-metrics",
            type: "expandable",
            component: "FeedbackTaskProgress",
          },
          {
            id: "stats",
            tooltip: "Stats",
            icon: "stats",
            action: "show-metrics",
            type: "expandable",
          },
        ],
      },
      refresh: {
        buttonType: "default",
        buttons: [
          {
            id: "refresh",
            tooltip: "Refresh",
            icon: "refresh",
            group: "Refresh",
            type: "non-expandable",
            action: "refresh",
          },
        ],
      },
    };
  },
  methods: {
    onClickSidebarAction(group, info) {
      switch (group) {
        case "metrics":
          this.toggleMetrics(info);
          break;
        case "mode":
          console.log("change-view-mode", info);
          break;
        case "refresh":
          console.log("refresh dataset");
          break;
        default:
          console.warn(info);
      }
    },
    toggleMetrics(panelContent) {
      this.currentMetric =
        this.currentMetric !== panelContent ? panelContent : null;
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
    display: flex;
    right: 0;
    z-index: 1;
    pointer-events: none;
  }
}
</style>
