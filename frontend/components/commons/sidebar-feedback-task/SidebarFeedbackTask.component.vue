<template>
  <div
    class="sidebar__container"
    :class="areMetricsVisible ? '--metrics' : null"
    v-if="datasetName"
  >
    <sidebar-panel
      :class="[currentMetric ? 'visible' : '']"
      @close-panel="onClosePanel"
    >
      <transition name="fade" appear duration="500">
        <SidebarProgress :dataset-name="datasetName" />
      </transition>
    </sidebar-panel>
    <sidebar-menu
      :current-metric="currentMetric"
      :view-mode="viewMode"
      :sidebar-items="sidebarItems"
      @click-sidebar-action="onClickSidebarAction"
    />
  </div>
</template>

<script>
import { mapActions } from "vuex";
import { DatasetViewSettings } from "@/models/DatasetViewSettings";
export default {
  name: "SidebarFeedbaskTaskComponent",
  data: () => ({
    currentMetric: undefined,
  }),
  computed: {
    workspace() {
      return this.$route.params.workspace;
    },
    datasetName() {
      return this.$route.params.dataset;
    },
    viewMode() {
      return "annotate";
    },
  },
  created() {
    this.sidebarItems = [
      {
        id: "annotate",
        tooltip: "Hand labeling",
        icon: "hand-labeling",
        group: "Mode",
        action: "change-view-mode",
        relatedMetrics: ["progress", "stats"],
      },
      {
        id: "progress",
        tooltip: "Progress",
        icon: "progress",
        action: "show-metrics",
        group: "Metrics",
      },
      {
        id: "refresh",
        tooltip: "Refresh",
        icon: "refresh",
        group: "Refresh",
        action: "refresh",
      },
    ];
  },
  methods: {
    ...mapActions({
      refresh: "entities/datasets/refresh",
    }),
    onClosePanel() {
      this.currentMetric = undefined;
      DatasetViewSettings.update({
        where: this.datasetName,
        data: {
          visibleMetrics: false,
        },
      });
    },
    onClickSidebarAction(action, value) {
      switch (action) {
        case "show-metrics":
          this.onShowSidebarInfo(value);
          break;
        case "refresh":
          this.onRefresh();
          break;
        default:
          console.warn(action);
      }
    },
    onRefresh() {
      this.refresh({
        dataset: this.dataset,
      });
    },
    areMetricsVisible() {
      return this.viewSettings.visibleMetrics;
    },
    onShowSidebarInfo(info) {
      if (this.currentMetric !== info) {
        this.currentMetric = info;
      } else {
        this.currentMetric = undefined;
      }
      DatasetViewSettings.update({
        where: this.datasetName,
        data: {
          visibleMetrics: this.currentMetric,
        },
      });
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