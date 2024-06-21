<template>
  <div>
    <h2 class="--heading5 --medium">{{ $t("settings.datasetInfo") }}</h2>
    <div class="settings__area">
      <div class="settings__row">
        <div class="settings__item">
          <p
            class="setting__dataset-name --body1"
            v-html="settings.dataset.name"
          />
        </div>
        <base-action-tooltip tooltip="$t('copied')">
          <base-button
            title="Copy to clipboard"
            class="secondary small"
            @click.prevent="$copyToClipboard(datasetSettingsUrl)"
          >
            {{ $t("copyLink") }}
          </base-button>
        </base-action-tooltip>
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
    border-bottom: 1px solid $black-10;
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
}
</styles>
