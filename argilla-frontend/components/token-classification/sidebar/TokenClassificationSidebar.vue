<!--
  - coding=utf-8
  - Copyright 2021-present, the Recognai S.L. team.
  -
  - Licensed under the Apache License, Version 2.0 (the "License");
  - you may not use this file except in compliance with the License.
  - You may obtain a copy of the License at
  -
  -     http://www.apache.org/licenses/LICENSE-2.0
  -
  - Unless required by applicable law or agreed to in writing, software
  - distributed under the License is distributed on an "AS IS" BASIS,
  - WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  - See the License for the specific language governing permissions and
  - limitations under the License.
  -->

<template>
  <sidebar-menu
    :current-metric="currentMetric"
    :dataset="dataset"
    :sidebar-items="sidebarItems"
    @refresh="$emit('refresh')"
    @show-metrics="onShowMetrics"
    @change-view-mode="onChangeViewMode"
  />
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
          id: "annotate",
          tooltip: "Hand labeling",
          icon: "hand-labeling",
          group: "Mode",
          action: "change-view-mode",
          relatedMetrics: ["progress", "stats"],
        },
        {
          id: "explore",
          tooltip: "Exploration",
          icon: "exploration",
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
          icon: "stats",
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
  beforeMount() {
    this.$emit("set-sidebar-items", this.sidebarItems);
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
