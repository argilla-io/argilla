<template>
  <div class="settings__container">
    <div class="settings__content">
      <h2 class="--heading5 --medium">{{ $t("settings.datasetInfo") }}</h2>
      <div class="settings__area">
        <div class="settings__row">
          <div class="settings__item">
            <p
              class="settings__dataset-name --body1"
              v-html="settings.dataset.name"
            />
          </div>
          <base-action-tooltip :tooltip="$t('copied')">
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
        <form
          @submit.prevent="onSubmit()"
          class="settings__edition-form-fields"
        >
          <div class="settings__area">
            <h2
              class="--heading5 --medium description__title"
              v-text="$t('taskDistribution')"
            />

            <div class="form_group">
              <label
                for="task-distribution"
                v-text="$t('minimumSubmittedResponses')"
              />
              <span
                class="info-icon"
                :data-title="$t('taskDistributionTooltip')"
              >
                <svgicon name="info" width="22" height="22"></svgicon>
              </span>
              <input type="number" id="task-distribution" />
            </div>
          </div>

          <DatasetDescription
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
    max-width: 800px;
    padding-top: $base-space;
  }
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

.form_group {
  display: flex;
  align-items: center;
  width: 100%;
  gap: $base-space;

  & > label {
    color: $black-87;
  }

  & input {
    display: flex;
    flex-direction: row;
    align-items: center;
    width: auto;
    height: 24px;
    padding: $base-space * 2;
    background: palette(white);
    border: 1px solid $black-20;
    border-radius: $border-radius;
    outline: 0;
    &:focus {
      border: 1px solid $primary-color;
    }
  }
}
.info-icon {
  color: $black-87;
  margin-right: $base-space * 2;
}
[data-title] {
  position: relative;
  overflow: visible;
  @include tooltip-mini("top", 8px);
}
</styles>
