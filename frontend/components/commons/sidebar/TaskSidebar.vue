<template>
  <div class="sidebar__container" v-if="dataset">
    <component :is="currentTaskHelp" :dataset="dataset" />
    <sidebar-panel
      :class="[currentTask, currentMetric ? 'visible' : '']"
      :dataset="dataset"
      @close-panel="onClosePanel"
    >
      <transition name="fade" appear duration="500">
        <span v-if="currentMetric">
          <div
            v-for="metric in metricsByViewMode"
            :key="metric"
            v-if="currentMetric === metric"
          >
            <component :is="componentName(metric)" :dataset="dataset" />
          </div>
        </span>
      </transition>
    </sidebar-panel>
    <component
      ref="menu"
      :is="currentTaskSidebar"
      :dataset="dataset"
      :current-metric="currentMetric"
      @refresh="onRefresh"
      @show-metrics="onShowSidebarInfo"
      @change-view-mode="onChangeViewMode"
    />
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
    currentTask() {
      return this.dataset.task;
    },
    currentTaskSidebar() {
      return `${this.currentTask}Sidebar`;
    },
    currentTaskHelp() {
      return `${this.currentTask}ViewInfo`;
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
    position: fixed;
    display: flex;
    right: 0;
    pointer-events: none;
    .--metrics & {
      pointer-events: all;
    }
  }
}
</style>
