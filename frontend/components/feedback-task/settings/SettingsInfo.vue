<template>
  <div class="settings__container">
    <div class="settings__content">
      <h2 class="--heading5 --medium">Dataset info</h2>
      <div class="settings__area">
        <div class="settings__row">
          <div class="settings__item">
            <p
              class="settings__dataset-name --body1"
              v-html="settings.dataset.name"
            />
            <BaseBadge :text="settings.dataset.task" />
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
        <form
          @submit.prevent="onSubmit()"
          class="settings__edition-form-fields"
        >
          <DatasetDescriptionComponent
            :key="settings.dataset.updatedAt"
            v-model="settings.dataset"
          />
          <div class="settings__edition-form__footer">
            <BaseButton
              type="button"
              class="secondary light small"
              @on-click="restore(settings.dataset)"
              :disabled="!settings.dataset.isModified"
            >
              <span v-text="$t('cancel')" />
            </BaseButton>
            <BaseButton
              type="submit"
              class="primary small"
              :disabled="!settings.dataset.isModified"
            >
              <span v-text="$t('update')" />
            </BaseButton>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { useSettingInfoViewModel } from "./useSettingInfoViewModel";
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
  },
  methods: {
    onSubmit() {
      this.update(this.settings.dataset);
    },
  },
  setup() {
    return useSettingInfoViewModel();
  },
};
</script>

<styles lang="scss" scoped>
.settings {
  &__container {
    display: flex;
    gap: $base-space * 4;
    height: 100%;
    flex-wrap: wrap;
    min-height: 0;
    overflow: auto;
  }

  &__content {
    flex: 1;
    max-width: 1000px;
    padding-top: $base-space;
  }
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

  &__item {
    display: flex;
    align-items: center;
    gap: $base-space * 3;
  }

  &__dataset-name {
    margin: 0;
  }

  &__edition-form {
    &__footer {
      width: 100%;
      display: flex;
      flex-direction: row;
      justify-content: flex-end;
      align-items: center;
      padding-top: $base-space * 3;
      gap: $base-space;
    }
  }
}
</styles>
./useSettingInfoViewModel
