<template>
  <div>
    <SidebarMenu
      :current-metric="currentMetric"
      :dataset="dataset"
      :sidebar-items="sidebarItems"
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
          id: "progress",
          tooltip: "Progress",
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
