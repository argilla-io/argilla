<template>
  <div>
    <sidebar-menu
      :dataset="dataset"
      @refresh="onRefresh"
      @showSidebarInfo="onShowSidebarInfo"
      @onEnableAnnotationView="onEnableAnnotationView" />
      <!-- TODO: Use media queries -->
    <sidebar-panel
      v-if="sidebarVisible || width > 1500"
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
  watch: {
    annotationEnabled() {
      this.getSidebarType();
    }
  },
  mounted() {
    this.getSidebarType();
  },
  methods: {
    ...mapActions({
      enableAnnotation: "entities/datasets/enableAnnotation",
      search: "entities/datasets/search",
    }),
    onRefresh() {
      this.search({
        dataset: this.dataset,
        query: this.dataset.query,
      });
    },
    getSidebarType() {
      // TODO: Use media queries
      if (this.width > 1500) {
        if (this.annotationEnabled) {
          this.sidebarInfoType = "progress";
        } else {
          this.sidebarInfoType = "stats";
        }
      }
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
    },
  },
};
 </script>
 
