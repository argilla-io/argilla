<template>
  <div class="datasets-empty">
    <span class="datasets-empty__message" v-text="$t('home.none')" />
    <div class="datasets-empty__cards" v-if="isAdminOrOwnerRole">
      <DatasetsEmptyCard
        :title="$t('home.importTitle')"
        :text="$t('home.importText')"
        :button-text="$t('home.importButton')"
        button-type="hub"
        button-action="expand-import-dataset"
        @on-click="$emit('on-click-card', $event)"
      />
      <div class="dataset__placeholder"></div>
      <div class="dataset__placeholder"></div>
    </div>
  </div>
</template>

<script>
import { useDatasetEmptyViewModel } from "./useDatasetsEmpty";
export default {
  setup() {
    return useDatasetEmptyViewModel();
  },
};
</script>
<style lang="scss" scoped>
.dataset {
  &__placeholder {
    background: linear-gradient(
      180deg,
      var(--bg-opacity-2) 0%,
      var(--bg-opacity-4) 100%
    );
    border-radius: $border-radius-m;
  }
}
.datasets-empty {
  &__content {
    max-width: max(900px, 50vw);
    width: auto;
    padding-top: $base-space * 2;
    padding-bottom: $base-space * 4;
    color: var(--fg-secondary);
    line-height: 1.5;
  }
  &__message {
    display: flex;
    color: var(--fg-tertiary);
    margin: $base-space * 4 0;
  }
  &__cards {
    display: grid;
    gap: $base-space * 2;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    grid-auto-rows: 1fr;
  }
}
</style>
