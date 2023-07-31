<template>
  <div class="sidebar__container">
    <SidebarFeedbackTaskPanel v-if="isPanelVisible" @close-panel="closePanel">
      <FeedbackTaskProgress
        v-if="getProgressComponentName === 'FeedbackTaskProgress'"
      />
    </SidebarFeedbackTaskPanel>
    <SidebarFeedbackTask
      @on-click-sidebar-action="onClickSidebarAction"
      :sidebar-items="sidebarItems"
      :active-buttons="[currentMetric, currentMode]"
      :expanded-component="currentMetric"
    />
  </div>
</template>

<script>
import { SIDEBAR_GROUP } from "@/models/feedback-task-model/dataset-filter/datasetFilter.queries";

export default {
  props: {
    datasetId: {
      type: String,
      required: true,
    },
  },
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
      metrics: {
        buttonType: "expandable",
        buttons: [
          {
            id: "metrics",
            tooltip: "Progress",
            icon: "progress",
            action: "show-metrics",
            type: "expandable",
            component: "FeedbackTaskProgress",
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
      switch (group.toUpperCase()) {
        case SIDEBAR_GROUP.METRICS:
          this.toggleMetrics(info);
          break;
        case SIDEBAR_GROUP.MODE:
          console.log("change-view-mode", info);
          break;
        case SIDEBAR_GROUP.REFRESH:
          this.$emit("refresh");
          break;
        default:
          console.warn(info);
      }
    },
    toggleMetrics(panelContent) {
      this.currentMetric =
        this.currentMetric !== panelContent ? panelContent : null;
      $nuxt.$emit("on-sidebar-toggle-metrics", !!this.currentMetric);
    },
    closePanel() {
      this.currentMetric = null;
      $nuxt.$emit("on-sidebar-toggle-metrics", null);
    },
  },
};
</script>

<style lang="scss" scoped>
.sidebar {
  &__container {
    position: fixed;
    display: flex;
    right: 0;
    z-index: 1;
    pointer-events: none;
  }
}
</style>
