<template>
  <div class="dataset-card">
    <div class="dataset-card__header">
      <p class="dataset-card__workspace">{{ dataset.workspaceName }}</p>
      <div class="dataset-card__actions">
        <BaseButton
          class="dataset-card__action"
          icon="copy"
          @click="$emit('copy-name')"
          title="Copy name to clipboard"
        />
        <BaseButton
          class="dataset-card__action"
          icon="link"
          @click="$emit('copy-url')"
          title="Copy link to clipboard"
        />
        <BaseButton
          class="dataset-card__action"
          icon="settings"
          @click="$emit('go-to-settings')"
          title="Go to dataset settings"
        />
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
  </div>
</template>

<script>
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
}
</style>
