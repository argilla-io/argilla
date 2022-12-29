<template>
  <div class="sidebar__container" v-if="dataset">
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
      @set-sidebar-items="onSetSidebarItems"
    />
  </div>
</template>

<script>
import { mapActions } from "vuex";
import { DatasetViewSettings } from "@/models/DatasetViewSettings";
import { Vector as VectorModel } from "@/models/Vector";
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
    sidebarItems: [],
    currentMetric: undefined,
  }),
  computed: {
    currentTask() {
      return this.dataset.task;
    },
    currentTaskSidebar() {
      return `${this.currentTask}Sidebar`;
    },
    metricsByViewMode() {
      return this.sidebarItems.find(
        (item) => item.id === this.dataset.viewSettings.viewMode
      ).relatedMetrics;
    },
    isReferenceRecord() {
      const value = VectorModel.query().where("is_active", true).first();
      return !!value;
    },
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
      if (value === "labelling-rules" && this.isReferenceRecord) {
        this.removeSimilarityFilter(value);
      }
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
    removeSimilarityFilter() {
      this.$emit("search-records", { query: { vector: null } });
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
