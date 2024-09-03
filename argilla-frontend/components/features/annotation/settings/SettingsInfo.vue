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
        <form
          @submit.prevent="onSubmitDatasetTaskMinimumResponse()"
          class="settings__edition-form-fields"
        >
          <h2
            class="--heading5 --medium description__title"
            v-text="$t('taskDistribution')"
          />

          <Validation :validations="settings.dataset.validate().distribution">
            <div class="form_group">
              <label
                for="task-distribution"
                v-text="$t('minimumSubmittedResponses')"
              />
              <span
                class="info-icon"
                :data-title="$t('taskDistributionTooltip')"
              >
                <svgicon name="info" width="20" height="20"></svgicon>
              </span>
              <input
                type="number"
                id="task-distribution"
                min="1"
                v-model="settings.dataset.distribution.minSubmitted"
              />
            </div>
          </Validation>

          <div class="settings__edition-form__footer">
            <BaseButton
              type="button"
              class="secondary light small"
              @on-click="settings.dataset.restore('distribution')"
              :disabled="!settings.dataset.isModifiedTaskDistribution"
            >
              <span v-text="$t('cancel')" />
            </BaseButton>
            <BaseButton
              type="submit"
              class="primary small"
              :disabled="
                !settings.dataset.isModifiedTaskDistribution ||
                !settings.dataset.isValidDistribution
              "
            >
              <span v-text="$t('update')" />
            </BaseButton>
          </div>
        </form>
      </div>

      <div class="settings__area">
        <form
          @submit.prevent="onSubmitDatasetGuidelines()"
          class="settings__edition-form-fields"
        >
          <Validation :validations="settings.dataset.validate().guidelines">
            <DatasetDescription
              :key="settings.dataset.updatedAt"
              v-model="settings.dataset"
            />
          </Validation>

          <div class="settings__edition-form__footer">
            <BaseButton
              type="button"
              class="secondary light small"
              @on-click="settings.dataset.restore('guidelines')"
              :disabled="!settings.dataset.isModifiedGuidelines"
            >
              <span v-text="$t('cancel')" />
            </BaseButton>
            <BaseButton
              type="submit"
              class="primary small"
              :disabled="
                !settings.dataset.isModifiedGuidelines ||
                !settings.dataset.isValidGuidelines
              "
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
    onSubmitDatasetGuidelines() {
      this.update(this.settings.dataset, "guidelines");
    },
    onSubmitDatasetTaskMinimumResponse() {
      this.update(this.settings.dataset, "distribution");
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
    color: var(--fg-primary);
  }

  & input,
  &__input--read-only {
    display: flex;
    flex-direction: row;
    align-items: center;
    width: 80px;
    height: 24px;
    padding: $base-space * 2;
    background: var(--bg-accent-grey-2);
    color: var(--fg-primary);
    border: 1px solid var(--bg-opacity-20);
    border-radius: $border-radius;
    outline: 0;
    &:focus {
      border: 1px solid var(--bg-action);
    }
  }
  &__input {
    &--read-only {
      background: var(--bg-opacity-4);
      border: 1px solid var(--bg-opacity-20);
      opacity: 0.6;
    }
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
</styles>
