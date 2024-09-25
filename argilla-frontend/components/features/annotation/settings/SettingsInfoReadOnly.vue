<template>
  <div class="settings">
    <h2 class="--heading5 --medium">{{ $t("settings.datasetInfo") }}</h2>
    <div class="settings__area">
      <div class="settings__row">
        <div class="settings__item">
          <p
            class="setting__dataset-name --body1"
            v-html="settings.dataset.name"
          />
        </div>
        <base-action-tooltip :tooltip="$t('copied')">
          <base-button
            :title="$t('button.tooltip.copyToClipboard')"
            class="secondary small"
            @click.prevent="$copyToClipboard(datasetSettingsUrl)"
          >
            {{ $t("copyLink") }}
          </base-button>
        </base-action-tooltip>
      </div>
    </div>
    <div class="settings__area">
      <h2
        class="--heading5 --medium description__title"
        v-text="$t('taskDistribution')"
      />

      <div class="form-group">
        <label v-text="$t('minimumSubmittedResponses')" />
        <span class="info-icon" :data-title="$t('taskDistributionTooltip')">
          <svgicon name="info" width="20" height="20"></svgicon>
        </span>
        <span
          class="form-group__input--read-only"
          v-text="settings.dataset.distribution.minSubmitted"
        />
      </div>
    </div>
    <div class="settings__area">
      <DatasetDescriptionReadOnly
        :guidelines="guidelines"
        :isColorLight="!guidelines"
      />
    </div>
  </div>
</template>

<script>
export default {
  name: "SettingsInfo",
  props: {
    settings: {
      type: Object,
      required: true,
    },
  },
  computed: {
    datasetSettingsUrl() {
      const { fullPath } = this.$route;
      return `${window.origin}${fullPath}`;
    },
    guidelines() {
      return (
        this.settings.dataset.guidelines || this.$t("noAnnotationGuidelines")
      );
    },
  },
};
</script>

<styles lang="scss" scoped>
.settings {
  &__area {
    max-width: 800px;
    padding-bottom: $base-space * 3;
    border-bottom: 1px solid var(--bg-opacity-10);
  }

  &__row {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  &__item {
    display: flex;
    align-items: center;
    gap: $base-space * 3;
    flex-wrap: wrap;
  }

  &__dataset-name {
    margin: 0;
  }
  .form-group {
    display: flex;
    align-items: center;
    width: 100%;
    gap: $base-space;
    &__input--read-only {
      display: flex;
      flex-direction: row;
      align-items: center;
      width: 80px;
      height: 24px;
      padding: $base-space * 2;
      border: 1px solid var(--bg-opacity-20);
      border-radius: $border-radius;
      background: var(--bg-opacity-4);
      border: 1px solid var(--bg-opacity-20);
      opacity: 0.6;
    }
  }
  .info-icon {
    color: var(--fg-tertiary);
    margin-right: $base-space * 2;
    &[data-title] {
      position: relative;
      overflow: visible;
      @include tooltip-mini("top", $base-space);
    }
  }
}
</styles>
