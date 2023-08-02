<template>
  <div>
    <h2 class="--heading5 --semibold">Dataset info</h2>
    <div class="settings__area">
      <div class="settings__row">
        <div class="item">
          <p class="dataset-name" v-html="settings.dataset.name" />
          <p class="badge" v-html="settings.dataset.task" />
        </div>
        <base-action-tooltip tooltip="Copied">
          <base-button
            title="Copy to clipboard"
            class="secondary small"
            @click.prevent="$copyToClipboard(datasetSettingsUrl)"
          >
            Copy link
          </base-button>
        </base-action-tooltip>
      </div>
    </div>
    <div class="settings__area">
      <DatasetDescriptionComponent
        :datasetDescription="guidelines"
        :isColorLight="!settings.dataset.guidelines"
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
    guidelines() {
      return (
        this.settings.dataset.guidelines ||
        "This dataset has no annotation guidelines"
      );
    },
  },
};
</script>

<styles lang="scss" scoped>
.settings {
  &__area {
    max-width: 1000px;
    padding-bottom: $base-space * 3;
    border-bottom: 1px solid $black-10;
  }

  &__row {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
}

.item {
  display: flex;
  gap: $base-space * 3;
}

.dataset-name {
  @include font-size(16px);
}

.dataset-task {
  color: $black-54;
  border: 1px solid $black-37;
  border-radius: $border-radius-m;
  padding: calc($base-space / 2);
  @include font-size(12px);
  @include line-height(12px);
}
</styles>
