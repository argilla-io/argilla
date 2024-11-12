<template>
  <div class="dataset-card">
    <div class="dataset-card__header">
      <p class="dataset-card__workspace">{{ dataset.workspaceName }}</p>
      <div class="dataset-card__actions">
        <BaseActionTooltip :tooltip="$t('copied')" tooltip-position="bottom">
          <BaseButton
            class="dataset-card__action"
            @click.prevent="$emit('copy-name')"
            ><svgicon name="copy"
          /></BaseButton>
        </BaseActionTooltip>
        <BaseActionTooltip :tooltip="$t('copied')" tooltip-position="bottom">
          <BaseButton
            class="dataset-card__action"
            @click.prevent="$emit('copy-url')"
            ><svgicon name="link"
          /></BaseButton>
        </BaseActionTooltip>
        <BaseButton
          class="dataset-card__action"
          @click.prevent="$emit('go-to-settings')"
          ><svgicon name="settings"
        /></BaseButton>
      </div>
    </div>
    <div class="dataset-card__content">
      <span class="dataset-card__row">
        <h1 class="dataset-card__title">{{ dataset.name }}</h1>
        <DatasetTotal :datasetId="dataset.id" />
      </span>
      <DatasetProgress :datasetId="dataset.id" />
      <DatasetFields :dataset="dataset" />
      <DatasetQuestions :dataset="dataset" />
    </div>
    <div class="dataset-card__footer">
      <svgicon
        name="update"
        height="14"
        width="14"
        color="var(--fg-tertiary)"
      />
      <BaseDate
        class="dataset-card__date"
        format="date-relative-now"
        :date="dataset.updatedAt"
      />
    </div>
  </div>
</template>

<script>
import "assets/icons/copy";
import "assets/icons/link";
import "assets/icons/settings";
import "assets/icons/update";
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
  height: 100%;
  padding: $base-space * 2;
  text-align: left;
  background: var(--bg-accent-grey-2);
  border: 1px solid var(--bg-opacity-10);
  border-radius: $border-radius-m;
  &__row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: $base-space;
  }
  &__header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: $base-space;
    padding-bottom: $base-space;
    border-bottom: 1px solid var(--bg-opacity-10);
  }
  &__content {
    display: flex;
    flex-direction: column;
    gap: $base-space;
    height: 100%;
  }
  &__title {
    margin: 0;
    color: var(--fg-primary);
    font-weight: 500;
    @include font-size(14px);
  }
  &__workspace {
    margin: 0;
    color: var(--fg-secondary);
    @include font-size(12px);
  }
  &__date {
    margin: 0;
    color: var(--fg-tertiary);
    @include font-size(12px);
  }
  &__footer {
    padding-top: $base-space;
    border-top: 1px solid var(--bg-opacity-10);
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
        color: var(--fg-tertiary);
      }
    }
  }
}
</style>
