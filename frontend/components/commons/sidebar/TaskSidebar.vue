<template>
  <div class="sidebar__container">
    <component
      ref="menu"
      v-if="dataset"
      :is="currentTaskSidebar"
      :dataset="dataset"
      :current-metric="currentMetric"
      @refresh="onRefresh"
      @show-metrics="onShowSidebarInfo"
      @change-view-mode="onChangeViewMode"
    />
    <SidebarPanel
      v-if="currentMetric"
      :dataset="dataset"
      :class="dataset.task"
      @close-panel="onClosePanel"
    >
      <div
        v-for="metric in metricsByViewMode"
        :key="metric"
        v-show="currentMetric === metric"
      >
        <component :is="componentName(metric)" :dataset="dataset" />
      </div>
    </SidebarPanel>
  </div>
</template>

<script>
import { mapActions } from "vuex";
import { DatasetViewSettings } from "@/models/DatasetViewSettings";
import SidebarMenu from "./SidebarMenu";
import SidebarPanel from "./SidebarPanel";
export default {
  components: { SidebarMenu, SidebarPanel },
  props: {
    dataset: {
      type: Object,
      required: true,
    },
  },
  data: () => ({
    currentMetric: undefined,
  }),
  computed: {
    currentTaskSidebar() {
      return this.currentTask + "Sidebar";
    },
    currentTask() {
      return this.dataset.task;
    },
    metricsByViewMode() {
      return this.sidebarItems.find(
        (item) => item.id === this.dataset.viewSettings.viewMode
      ).relatedMetrics;
    },
    sidebarItems() {
      return this.$refs.menu.sidebarItems;
    },
  },
  methods: {
    ...mapActions({
      changeViewMode: "entities/datasets/changeViewMode",
      refresh: "entities/datasets/refresh",
    }),
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
    },
    onShowSidebarInfo(info) {
      if (this.currentMetric !== info) {
        this.currentMetric = info;
      } else {
        this.currentMetric = undefined;
      }
      DatasetViewSettings.update({
        where: this.dataset.name,
        data: {
          visibleMetrics: this.currentMetric,
        },
      });
    },
    onClosePanel() {
      this.currentMetric = undefined;
      DatasetViewSettings.update({
        where: this.dataset.name,
        data: {
          visibleMetrics: false,
        },
      });
    },
    componentName(metric) {
      return `${this.currentTask}${this.$options.filters.capitalize(metric)}`;
    },
  },
};
</script>

<style lang="scss" scoped>
.sidebar {
  &__container {
    z-index: 1;
  }
}
</style>
