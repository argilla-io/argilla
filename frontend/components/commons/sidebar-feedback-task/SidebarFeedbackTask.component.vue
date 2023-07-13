<template>
  <div class="sidebar__container">
    <SidebarFeedbackTaskPanel v-if="isPanelVisible" @close-panel="closePanel">
      <HelpShortcut v-if="currentPanel === 'help-shortcut'" />
      <FeedbackTaskProgress
        v-else-if="currentPanel === 'metrics'"
        :userIdToShowMetrics="userId"
      />
    </SidebarFeedbackTaskPanel>
    <SidebarFeedbackTask
      @on-click-sidebar-action="onClickSidebarAction"
      :sidebar-items="sidebarItems"
      :active-buttons="[currentPanel, currentMode]"
      :expanded-component="currentPanel"
    />
  </div>
</template>

<script>
import { SIDEBAR_GROUP } from "@/models/feedback-task-model/dataset-filter/datasetFilter.queries";
import { isDatasetExistsByDatasetIdAndUserId } from "@/models/feedback-task-model/dataset-metric/datasetMetric.queries";

export default {
  props: {
    datasetId: {
      type: String,
      required: true,
    },
  },
  data: () => ({
    currentPanel: null,
    currentMode: "annotate",
    isPanelVisible: false,
  }),
  computed: {
    userId() {
      return this.$auth.user.id;
    },
    datasetExists() {
      return isDatasetExistsByDatasetIdAndUserId({
        userId: this.userId,
        datasetId: this.datasetId,
      });
    },
  },
  created() {
    this.sidebarItems = {
      metrics: {
        buttonType: "expandable",
        buttons: [
          {
            id: "help-shortcut",
            tooltip: "Help",
            icon: "support",
            action: "show-help",
            type: "expandable",
            component: "HelpShortcut",
          },
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
          this.togglePanel(info);
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
    togglePanel(panelContent) {
      if (!this.datasetExists) return;

      this.currentPanel =
        this.currentPanel !== panelContent ? panelContent : null;

      this.isPanelVisible = !!this.currentPanel;

      $nuxt.$emit("on-sidebar-toggle-panel", this.isPanelVisible);
    },
    closePanel() {
      this.isPanelVisible = false;
      this.currentPanel = null;
      $nuxt.$emit("on-sidebar-toggle-panel", null);
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
