<template>
  <div class="new-dataset">
    <HeaderFeedbackTask
      :breadcrumbs="[
        { link: '/', name: $t('breadcrumbs.home') },
        { name: 'new' },
        { name: datasetConfig?.repoId },
      ]"
    >
      <template slot="badge">
        <p class="new-dataset__header-badge">
          {{ $t("datasetCreation.preview") }}
        </p>
      </template>
    </HeaderFeedbackTask>
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
  &__header-badge {
    background-color: hsl(from var(--bg-config-card) h 30% 50%);
    padding: calc($base-space / 2) $base-space;
    border-radius: $border-radius;
    margin: 0;
    font-weight: 500;
    margin-left: $base-space * 2;
    @include font-size(12px);
    @include line-height(16px);
  }
}
</style>
