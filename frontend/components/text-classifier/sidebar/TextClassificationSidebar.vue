<template>
  <div>
    <SidebarMenu
      :current-metric="currentMetric"
      :dataset="dataset"
      :sidebar-items="filteredSidebarItems"
      @refresh="$emit('refresh')"
      @show-metrics="onShowMetrics"
      @change-view-mode="onChangeViewMode"
    />
  </div>
</template>

<script>
export default {
  props: {
    dataset: {
      type: Object,
      required: true,
    },
    currentMetric: {
      type: String,
    },
  },
  data: () => {
    return {
      sidebarItems: [
        {
          id: "explore",
          tooltip: "Explore",
          icon: "explore-view",
          group: "Mode",
          action: "change-view-mode",
          relatedMetrics: ["progress", "stats"],
        },
        {
          id: "annotate",
          tooltip: "Annotate",
          icon: "annotate-view",
          group: "Mode",
          action: "change-view-mode",
          relatedMetrics: ["progress", "stats"],
        },
        {
          id: "labelling-rules",
          tooltip: "Define rules",
          icon: "labelling-rules-view",
          group: "Mode",
          action: "change-view-mode",
          relatedMetrics: ["stats", "rules"],
        },
        {
          id: "progress",
          tooltip: "Progress",
          icon: "progress",
          action: "show-metrics",
          group: "Metrics",
        },
        {
          id: "rules",
          tooltip: "Overall rule metrics",
          icon: "progress",
          action: "show-metrics",
          group: "Metrics",
        },
        {
          id: "stats",
          tooltip: "Stats",
          icon: "metrics",
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
      ],
    };
  },
  computed: {
    filteredSidebarItems() {
      return this.sidebarItems.filter(
        (item) =>
          item.group !== "Metrics" || this.metricsTypes.includes(item.id)
      );
    },
    metricsTypes() {
      return this.sidebarItems.find(
        (item) => item.id === this.dataset.viewSettings.viewMode
      ).relatedMetrics;
    },
  },
  methods: {
    onChangeViewMode(value) {
      this.$emit("change-view-mode", value);
    },
    onShowMetrics(info) {
      this.$emit("show-metrics", info);
    },
  },
};
</script>
