<template>
  <div class="dataset-card">
    <div class="dataset-card__header">
      <p class="dataset-card__workspace">{{ dataset.workspaceName }}</p>
      <div class="dataset-card__actions">
        <BaseButton class="dataset-card__action" @click="$emit('copy-name')"
          ><svgicon name="copy"
        /></BaseButton>
        <BaseButton class="dataset-card__action" @click="$emit('copy-url')"
          ><svgicon name="link"
        /></BaseButton>
        <BaseButton
          class="dataset-card__action"
          @click="$emit('go-to-settings')"
          ><svgicon name="settings"
        /></BaseButton>
      </div>
    </div>
    <div class="dataset-card__content">
      <h1 class="dataset-card__title">{{ dataset.name }}</h1>
      <DatasetProgress :datasetId="dataset.id" />
      <DatasetFields :dataset="dataset" />
    </div>
    <div class="dataset-card__footer">
      <p class="dataset-card__date">{{ dataset.updatedAt }}</p>
    </div>
  </div>
</template>

<script>
import "assets/icons/copy";
import "assets/icons/link";
import "assets/icons/settings";
export default {
  props: {
    dataset: {
      type: Object,
      required: true,
    },
  },
};
</script>

<style scoped lang="scss">
.dataset-card {
  display: flex;
  flex-direction: column;
  text-align: center;
  gap: $base-space * 2;
  border: 1px solid var(--bg-opacity-10);
  border-radius: $border-radius-m;
  padding: $base-space * 2;
  &__header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: $base-space;
  }
  &__actions {
    display: flex;
    justify-content: flex-end;
    gap: $base-space;
  }
  &__action {
    &.button {
      padding: $base-space;
      color: var(--fg-secondary);
      &:hover {
        background: var(--bg-opacity-4);
      }
    }
  }
}
</style>
