<template>
  <div class="new-dataset">
    <HeaderFeedbackTask
      :breadcrumbs="[
        { link: '/', name: 'Home' },
        { name: 'dataset' },
        { name: 'new' },
        { name: datasetConfig?.repoId },
      ]"
    />
    <DatasetConfiguration
      v-if="datasetConfig"
      :dataset="datasetConfig"
      @change-subset="changeSubset($event)"
    />
  </div>
</template>

<script>
import { useNewDatasetViewModel } from "./useNewDatasetViewModel";

export default {
  mounted() {
    this.getNewDatasetByRepoIdFromUrl();
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
