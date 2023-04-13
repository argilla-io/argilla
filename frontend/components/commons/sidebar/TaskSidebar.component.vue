<template>
  <div
    class="sidebar__container"
    :class="areMetricsVisible ? '--metrics' : null"
    v-if="dataset"
  >
    <BaseSidebarPanel
      :class="[datasetTask, currentMetric ? 'visible' : '']"
      @close-panel="onClosePanel"
    >
      <transition name="fade" appear duration="500">
        <span v-if="currentMetric">
          <div
            v-for="metric in metricsByViewMode"
            :key="metric"
            v-if="currentMetric === metric"
          >
            <component
              :is="componentName(metric)"
              :datasetId="dataset.id"
              :datasetName="datasetName"
            />
          </div>
        </span>
      </transition>
    </BaseSidebarPanel>
    <BaseSidebarMenu
      :current-metric="currentMetric"
      :sidebar-items="sidebarItems"
      :view-mode="viewMode"
      @click-sidebar-action="onClickSidebarAction"
    />
  </div>
</template>

<script>
import { mapActions } from "vuex";
import { DatasetViewSettings } from "@/models/DatasetViewSettings";
import { getViewSettingsByDatasetName } from "@/models/viewSettings.queries";
import { getDatasetModelPrimaryKey } from "@/models/Dataset";
import { getDatasetTaskById } from "@/models/dataset.utilities";
import { getDatasetFromORM } from "@/models/dataset.utilities";
import { SIDEBAR_ITEMS } from "./sidebarItems.config";
import BaseSidebarMenu from "@/components/base/sidebar/BaseSidebarMenu";
import BaseSidebarPanel from "@/components/base/sidebar/BaseSidebarPanel";
export default {
  components: { BaseSidebarMenu, BaseSidebarPanel },
  data: () => ({
    currentMetric: undefined,
  }),
  computed: {
    datasetId() {
      return getDatasetModelPrimaryKey({
        name: this.datasetName,
        workspace: this.workspace,
      });
    },
    workspace() {
      return this.$route.params.workspace;
    },
    datasetName() {
      return this.$route.params.dataset;
    },
    dataset() {
      return getDatasetFromORM(this.datasetId, this.datasetTask);
    },
    datasetTask() {
      return getDatasetTaskById(this.datasetId);
    },
    metricsByViewMode() {
      return this.sidebarItems.find((item) => item.id === this.viewMode)
        .relatedMetrics;
    },
    viewMode() {
      return this.viewSettings.viewMode;
    },
    areMetricsVisible() {
      return this.viewSettings.visibleMetrics;
    },
    viewSettings() {
      return getViewSettingsByDatasetName(this.datasetName);
    },
  },
  created() {
    this.sidebarItems = SIDEBAR_ITEMS[this.datasetTask.toUpperCase()];
  },
  methods: {
    ...mapActions({
      changeViewMode: "entities/datasets/changeViewMode",
      refresh: "entities/datasets/refresh",
    }),
    onSetSidebarItems(items) {
      this.sidebarItems = items;
    },
    onRefresh() {
      this.refresh({
        dataset: this.dataset,
      });
    },
    async onChangeViewMode(value) {
      await this.changeViewMode({
        dataset: this.dataset,
        value: value,
      });
      this.currentMetric = this.metricsByViewMode.includes(this.currentMetric)
        ? this.currentMetric
        : this.onShowSidebarInfo(false);
      this.$emit("view-mode-changed", value);
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
    onClosePanel() {
      this.currentMetric = undefined;
      DatasetViewSettings.update({
        where: this.datasetName,
        data: {
          visibleMetrics: false,
        },
      });
    },
    componentName(metric) {
      return `${this.datasetTask}${this.$options.filters.capitalize(metric)}`;
    },
    onClickSidebarAction(action, value) {
      switch (action) {
        case "show-metrics":
          this.onShowSidebarInfo(value);
          break;
        case "change-view-mode":
          this.onChangeViewMode(value);
          break;
        case "refresh":
          this.onRefresh();
          break;
        default:
          console.warn(`Unknown ${action}`);
      }
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
