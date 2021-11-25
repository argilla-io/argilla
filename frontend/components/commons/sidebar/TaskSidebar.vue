<template>
  <div>
    <sidebar-menu
      :dataset="dataset"
      @refresh="onRefresh"
      @showSidebarInfo="onShowSidebarInfo"
      @onEnableAnnotationView="onEnableAnnotationView"
    />
    <!-- TODO: Use media queries -->
    <sidebar-panel
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
    </sidebar-panel>
  </div>
</template>

<script>
import { mapActions } from "vuex";
import { DatasetViewSettings } from "@/models/DatasetViewSettings";
export default {
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
    annotationEnabled() {
      return this.dataset.viewSettings.annotationEnabled;
    },
  },
  updated() {
    window.onresize = () => {
      this.width = window.innerWidth;
    };
  },
  methods: {
    ...mapActions({
      enableAnnotation: "entities/datasets/enableAnnotation",
      refresh: "entities/datasets/refresh",
    }),
    onRefresh() {
      this.refresh({
        dataset: this.dataset,
      });
    },
    async onEnableAnnotationView(value) {
      await this.enableAnnotation({
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
