<template>
  <div class="top-content">
    <h1 v-html="title" />
    <base-button :to="datasetPageUrl" class="secondary text">
      <svgicon name="chevron-left" width="10" height="10" color="#4C4EA3" />
      {{ goToDatasetPageLabel }}
    </base-button>
  </div>
</template>

<script>
export default {
  name: "TopDatasetSettingsContent",
  data() {
    return {
      title: "Dataset settings",
      goToDatasetPageLabel: "See your dataset",
    };
  },
  computed: {
    datasetPageUrl() {
      const { fullPath } = this.$route;
      const datasetPageUrl = fullPath.replace("/settings?", "?");
      return datasetPageUrl;
    },
  },
};
</script>

<style lang="scss" scoped>
.top-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
  border-bottom: 1px solid #e6e6e6;
}
</style>
