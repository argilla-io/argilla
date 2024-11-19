<template>
  <div class="dataset-card">
    <div>
      <div class="dataset-card__date">
        <span v-text="$t('home.updatedAt')" />
        <BaseDate format="date-relative-now" :date="dataset.updatedAt" />
      </div>
      <p class="dataset-card__workspace">{{ dataset.workspaceName }}</p>
      <!-- <div class="dataset-card__actions">
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
      </div> -->

      <div class="dataset-card__content">
        <h1 class="dataset-card__title">{{ dataset.name }}</h1>
        <DatasetFields :dataset="dataset" />
        <DatasetQuestions :dataset="dataset" />
      </div>
    </div>
    <div class="dataset-card__footer">
      <span class="dataset-card__row">
        <DatasetProgress :datasetId="dataset.id" />
        <DatasetTotal :datasetId="dataset.id" />
      </span>
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
  justify-content: space-between;
  text-align: center;
  gap: $base-space * 2;
  height: 100%;
  padding: $base-space * 2;
  text-align: left;
  background: var(--bg-accent-grey-3);
  border: 1px solid var(--bg-opacity-6);
  border-radius: $border-radius-m;
  box-shadow: 0 0 0 0 var(--bg-opacity-4);
  transition: all 0.2s ease;
  &:hover {
    border-color: var(--bg-opacity-10);
    box-shadow: 0 2px 1px 1px var(--bg-opacity-4);
  }
  &__row {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: $base-space;
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
  }
  &__workspace {
    margin: 0;
    color: var(--fg-secondary);
    @include font-size(12px);
  }
  &__date {
    margin: 0;
    color: var(--fg-tertiary);
    text-align: right;
    font-weight: 200;
    @include font-size(11px);
  }
  &__footer {
    padding-top: $base-space;
    border-top: 1px solid var(--bg-opacity-6);
  }
  &__actions {
    display: flex;
    justify-content: flex-end;
    gap: $base-space;
  }
  // &__action {
  //   &.button {
  //     padding: $base-space;
  //     color: var(--fg-secondary);
  //     &:hover {
  //       color: var(--fg-tertiary);
  //     }
  //   }
  // }
}
</style>
