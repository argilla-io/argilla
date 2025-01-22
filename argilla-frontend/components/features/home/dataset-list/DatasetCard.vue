<template>
  <NuxtLink :to="getDatasetLink(dataset)" class="dataset-card">
    <div class="dataset-card__body">
      <div class="dataset-card__row">
        <div class="dataset-card__actions">
          <BaseActionTooltip :tooltip="$t('copied')" tooltip-position="bottom">
            <BaseButton
              :title="$t('copyLink')"
              class="dataset-card__action"
              @click.prevent="copyUrl()"
              ><svgicon name="link" width="14" height="14"
            /></BaseButton>
          </BaseActionTooltip>
          <BaseButton
            :title="$t('settings.title')"
            class="dataset-card__action"
            @click.prevent="goToSetting()"
            ><svgicon name="settings" width="14" height="14"
          /></BaseButton>
        </div>
        <div class="dataset-card__date">
          <span v-text="$t('home.updatedAt')" />
          <BaseDate format="date-relative-now" :date="dataset.lastActivityAt" />
        </div>
      </div>
      <p class="dataset-card__workspace">{{ dataset.workspaceName }}</p>

      <div class="dataset-card__content">
        <h1 class="dataset-card__title">{{ dataset.name }}</h1>
        <div class="dataset-card__badges">
          <DatasetFields :dataset="dataset" />
          <DatasetQuestions :dataset="dataset" />
        </div>
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
  </NuxtLink>
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
  methods: {
    copyUrl() {
      this.$copyToClipboard(
        `${window.origin}${this.getDatasetLink(this.dataset)}`
      );
    },
  },
  setup(props) {
    return useDatasetCardViewModel(props);
  },
};
</script>

<style scoped lang="scss">
$shadow-default: rgba(0, 0, 0, 0.1) 0px 3px 12px 0px,
  var(--bg-opacity-4) 0px 0px 0px 1px inset;
$shadow-hover: rgba(0, 0, 0, 0.05) 0px 1px 4px 0px,
  var(--bg-opacity-4) 0px 0px 0px 1px inset;
.dataset-card {
  text-decoration: none;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  text-align: center;
  gap: $base-space * 2;
  height: 100%;
  padding: $base-space * 3;
  text-align: left;
  background: var(--bg-accent-grey-3);
  border-radius: $border-radius-l;
  box-shadow: $shadow-default;
  transition: all 0.2s ease;
  &:hover {
    box-shadow: $shadow-hover;
    background: hsla(from var(--bg-accent-grey-3) h s l / 40%);
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
  &__body {
    display: flex;
    flex-direction: column;
    height: 100%;
  }
  &__content {
    display: flex;
    flex-direction: column;
    gap: $base-space;
    height: 100%;
  }
  &__badges {
    display: flex;
    flex-direction: column;
    gap: $base-space;
  }
  &__title {
    margin: 0 0 $base-space 0;
    color: var(--fg-primary);
    font-weight: 500;
    min-height: $base-space * 5;
    @include font-size(18px);
    word-break: break-all;
    transition: color 0.3s ease;
  }
  &__workspace {
    margin: 0 0 calc($base-space / 2) 0;
    color: var(--fg-primary);
    @include font-size(12px);
  }
  &__date {
    margin: 0 0 calc($base-space / 2) 0;
    color: var(--fg-secondary);
    text-align: right;
    @include font-size(11px);
  }
  &__footer {
    flex-shrink: 0;
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
