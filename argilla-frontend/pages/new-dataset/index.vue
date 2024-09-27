<template>
  <div class="new-dataset">
    <HeaderFeedbackTask :breadcrumbs="[{ link: {}, name: 'Home' }]" />
    <DatasetCreation
      v-if="!datasetConfig"
      @load-dataset-from-hf="onLoadDatasetFromHF"
    />
    <DatasetConfiguration
      v-else
      :dataset-config="datasetConfig"
      :dataset-id="datasetId"
      @change-subset="changeSubset($event)"
    />
  </div>
</template>

<script>
import { useNewDatasetViewModel } from "./useNewDatasetViewModel";
export default {
  methods: {
    onLoadDatasetFromHF(repoId) {
      this.getNewDatasetByRepoId(repoId);
    },
  },
  setup() {
    return useNewDatasetViewModel();
  },
};
</script>

<style scoped lang="scss">
.new-dataset {
  height: 100vh;
  display: flex;
  flex-direction: column;
}
</style>
