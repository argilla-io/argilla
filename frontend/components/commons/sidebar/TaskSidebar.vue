<template>
  <div>
    <SidebarMenu
      :dataset="dataset"
      @refresh="onRefresh"
      @showMetric="onShowSidebarInfo"
      @changeViewMode="onChangeViewMode"
    />
    <!-- TODO: Use media queries -->
    <SidebarPanel
      v-if="sidebarVisible"
      :dataset="dataset"
      :class="dataset.task"
    >
      <div v-show="sidebarInfoType === 'progress'">
        <component :is="currentTaskProgress" :dataset="dataset" />
      </div>
      <div v-show="sidebarInfoType === 'stats'">
        <component :is="currentTaskStats" :dataset="dataset" />
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
    sidebarInfoType: "progress",
    sidebarVisible: false,
    width: window.innerWidth,
  }),
  computed: {
    currentTask() {
      return this.dataset.task;
    },
    currentTaskProgress() {
      return this.currentTask + "Progress";
    },
    currentTaskStats() {
      return this.currentTask + "Stats";
    },
  },
  updated() {
    window.onresize = () => {
      this.width = window.innerWidth;
    };
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
    },
    onShowSidebarInfo(info) {
      if (this.sidebarInfoType !== info) {
        this.sidebarVisible = true;
      } else {
        this.sidebarVisible = !this.sidebarVisible;
      }
      this.sidebarInfoType = info;
      DatasetViewSettings.update({
        where: this.dataset.name,
        data: {
          visibleMetrics: this.sidebarVisible,
        },
      });
    },
  },
};
</script>
