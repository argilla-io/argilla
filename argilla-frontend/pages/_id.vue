<template>
  <div class="new-dataset">
    <HeaderFeedbackTask
      :breadcrumbs="[
        { link: '/', name: $t('breadcrumbs.home') },
        { name: repoIdWithoutOrg },
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
  middleware({ route, redirect }) {
    if (route.params.id === "datasets") {
      redirect("/");
    }
  },
  mounted() {
    this.getNewDatasetByRepoIdFromUrl();
  },
  setup() {
    return useNewDatasetViewModel();
  },
  computed: {
    repoIdWithoutOrg() {
      return this.datasetConfig?.repoId?.split("/")[1];
    },
  },
};
</script>

<style scoped lang="scss">
.new-dataset {
  height: 100vh;
  display: flex;
  flex-direction: column;
  &__header-badge {
    background-color: hsl(from var(--color-brand-secondary) h s l);
    color: var(--color-dark-grey);
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
