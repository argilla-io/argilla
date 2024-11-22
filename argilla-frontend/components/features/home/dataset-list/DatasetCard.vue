<template>
  <div class="dataset-card">
    <div>
      <div class="dataset-card__row">
        <div class="dataset-card__actions">
          <BaseActionTooltip :tooltip="$t('copied')" tooltip-position="bottom">
            <BaseButton
              :title="$t('copyLink')"
              class="dataset-card__action"
              @click.prevent="$emit('copy-url')"
              ><svgicon name="link" width="14" height="14"
            /></BaseButton>
          </BaseActionTooltip>
          <BaseButton
            :title="$t('settings.title')"
            class="dataset-card__action"
            @click.prevent="$emit('go-to-settings')"
            ><svgicon name="settings" width="14" height="14"
          /></BaseButton>
        </div>
        <div class="dataset-card__date">
          <span v-text="$t('home.updatedAt')" />
          <BaseDate format="date-relative-now" :date="dataset.updatedAt" />
        </div>
      </div>
      <p class="dataset-card__workspace">{{ dataset.workspaceName }}</p>

      <div class="dataset-card__content">
        <h1 class="dataset-card__title">{{ dataset.name }}</h1>
        <DatasetFields :dataset="dataset" />
        <DatasetQuestions :dataset="dataset" />
      </div>
    </div>
    <div class="dataset-card__footer">
      <span class="dataset-card__row">
        <DatasetProgress :percent="completedPercent" />
        <div class="dataset-card__column">
          <DatasetTotal :total="total" />
          <DatasetUsers :users="users" />
        </div>
      </span>
    </div>
  </div>
</template>

<script>
import "assets/icons/copy";
import "assets/icons/link";
import "assets/icons/settings";
import "assets/icons/update";
import { useDatasetCardViewModel } from "./useDatasetCardViewModel";
export default {
  props: {
    dataset: {
      type: Object,
      required: true,
    },
  },
  setup(props) {
    return useDatasetCardViewModel(props);
  },
};
</script>

<style scoped lang="scss">
.dataset-card {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  text-align: center;
  gap: $base-space * 2;
  height: 100%;
  padding: $base-space * 2;
  text-align: left;
  background: var(--bg-accent-grey-3);
  border-radius: $border-radius-m;
  box-shadow: $shadow-400;
  transition: all 0.2s ease;
  border: 1px solid var(--bg-opacity-4);
  &:hover {
    box-shadow: $shadow-300;
    .dataset-card__title {
      transition: color 0.2s ease;
      color: var(--fg-cuaternary);
    }
    .dataset-card__action {
      display: block;
    }
  }
  &__row {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: $base-space;
  }
  &__column {
    display: flex;
    flex-direction: column;
    gap: calc($base-space / 3);
  }
  &__header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: $base-space;
    padding-bottom: $base-space;
  }
  &__content {
    display: flex;
    flex-direction: column;
    gap: $base-space;
    height: 100%;
  }
  &__title {
    margin: 0 0 $base-space 0;
    color: var(--fg-primary);
    font-weight: 500;
    @include font-size(16px);
    word-break: break-word;
    transition: color 0.3s ease;
  }
  &__workspace {
    margin: 0 0 calc($base-space / 2) 0;
    color: var(--fg-secondary);
    @include font-size(12px);
  }
  &__date {
    margin: 0;
    color: var(--fg-secondary);
    text-align: right;
    font-weight: 200;
    @include font-size(11px);
  }
  &__footer {
    padding-top: $base-space * 2;
    border-top: 1px solid var(--bg-opacity-6);
    min-height: $base-space * 7;
  }
  &__actions {
    display: flex;
    justify-content: flex-end;
    gap: $base-space;
  }
  &__action {
    display: none;
    &.button {
      padding: 0 calc($base-space / 2);
      color: var(--fg-tertiary);
      &:hover {
        color: var(--fg-secondary);
      }
    }
  }
}
</style>
