<template>
  <div class="top-content">
    <h1 v-html="title" />
    <base-button :to="datasetPage" class="secondary text">
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
    workspace() {
      return this.$route.params.workspace;
    },
    datasetName() {
      return this.$route.params.dataset;
    },
    datasetPage() {
      const { workspace, datasetName } = this;

      const datasetPageObjWithParams = {
        name: "datasets-workspace-dataset",
        params: { workspace, dataset: datasetName },
      };

      return datasetPageObjWithParams;
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
