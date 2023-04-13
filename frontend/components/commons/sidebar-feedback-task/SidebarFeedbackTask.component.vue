<template>
  <BaseSidebar
    :view-mode="viewMode"
    :sidebar-items="sidebarItems"
    @on-click-sidebar-action="onClickSidebarAction"
  />
</template>

<script>
export default {
  name: "SidebarFeedbaskTaskComponent",
  computed: {
    viewMode() {
      return "annotate";
    },
  },
  created() {
    this.sidebarItems = [
      {
        id: "annotate",
        tooltip: "Hand labeling",
        icon: "hand-labeling",
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
        component: "FeedbackTaskProgress",
      },
      {
        id: "refresh",
        tooltip: "Refresh",
        icon: "refresh",
        group: "Refresh",
        action: "refresh",
      },
    ];
  },
  methods: {
    onClickSidebarAction(action, value) {
      switch (action) {
        case "change-view-mode":
          console.log("change-view-mode", value);
          break;
        case "refresh":
          console.log("refresh dataset");
          break;
        default:
          console.warn(action);
      }
    },
  },
};
</script>
