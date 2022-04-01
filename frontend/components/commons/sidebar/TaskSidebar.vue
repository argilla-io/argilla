<template>
  <div>
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
        v-for="metricType in metricsTypes"
        :key="metricType"
        v-show="currentMetric === metricType"
      >
        <component :is="componentName(metricType)" :dataset="dataset" />
      </div>
    </SidebarPanel>
  </div>
</template>

<script>
import { mapActions } from "vuex";
import { DatasetViewSettings } from "@/models/DatasetViewSettings";
import capitalize from "~/components/core/utils/capitalize";
import SidebarMenu from "./SidebarMenu";
import SidebarPanel from "./SidebarPanel";
export default {
  components: { SidebarMenu, SidebarPanel },
  props: {
    dataset: {
      type: Object,
      required: true,
    },
    sidebarItems: {
      type: Array,
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
    metricsTypes() {
      return this.$refs.menu.metricsTypes;
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
      this.currentMetric = this.metricsTypes.includes(this.currentMetric)
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
    componentName(metricType) {
      return `${this.currentTask}${capitalize(metricType)}`;
    },
  },
};
</script>
