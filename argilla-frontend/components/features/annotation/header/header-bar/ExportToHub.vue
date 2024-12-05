<template>
  <div class="export-to-hub" @keydown.stop="">
    <BaseButton
      class="primary export-to-hub__button"
      @click.prevent="openDialog"
      :loading="isExporting"
      :disabled="isExporting"
      >{{ $t("button.exportToHub") }}</BaseButton
    >
    <transition name="fade" appear>
      <dialog
        v-if="isDialogOpen"
        v-click-outside="closeDialog"
        class="export-to-hub__dialog"
      >
        <form @submit.prevent="exportToHub" class="export-to-hub__form">
          <h2
            class="export-to-hub__title"
            v-text="$t('exportToHub.dislogTitle')"
          />

          <div class="export-to-hub__form__dataset">
            <div class="export-to-hub__form__group --small">
              <div class="export-to-hub__label">
                <label v-text="$t('owner')" />
                <BaseIconWithBadge
                  class="export-to-hub__label__info"
                  icon="info"
                  icon-color="var(--fg-tertiary)"
                  v-tooltip="{
                    backgroundColor: 'var(--bg-accent-grey-5)',
                    content: $t('exportToHub.ownerTooltip'),
                    width: 300,
                  }"
                  role="tooltip"
                  :aria-label="$t('exportToHub.ownerTooltip')"
                />
              </div>
              <input
                type="text"
                v-model="exportToHubForm.orgOrUsername"
                class="input"
                @blur="validateForm('orgOrUsername')"
                @input="validateForm('orgOrUsername')"
                :placeholder="$t('owner')"
              />
            </div>
            <span aria-hidden="true" class="export-to-hub__form__separator"
              >/</span
            >
            <div class="export-to-hub__form__group">
              <label>Dataset name</label>
              <input
                type="text"
                v-model="exportToHubForm.datasetName"
                class="input"
                :placeholder="$t('datasetCreation.datasetName')"
                @blur="validateForm('datasetName')"
                @input="validateForm('datasetName')"
              />
            </div>
          </div>

          <div class="export-to-hub__form__group">
            <div class="export-to-hub__label">
              <label v-text="$t('hfToken')" />
              <BaseIconWithBadge
                class="export-to-hub__label__info"
                icon="info"
                icon-color="var(--fg-tertiary)"
                v-tooltip="{
                  backgroundColor: 'var(--bg-accent-grey-5)',
                  content: $t('exportToHub.tokenTooltip'),
                  width: 200,
                }"
                role="tooltip"
                :aria-label="$t('exportToHub.tokenTooltip')"
              />
            </div>
            <input
              class="input"
              type="password"
              autocomplete="one-time-code"
              v-model="exportToHubForm.hfToken"
              :placeholder="$t('hfToken')"
              @blur="validateForm('hfToken')"
              @input="validateForm('hfToken')"
            />
          </div>

          <div class="export-to-hub__form__group">
            <BaseSwitch
              class="export-to-hub__form__switch"
              v-model="exportToHubForm.isPrivate"
              >{{ $t("private") }}</BaseSwitch
            >
          </div>
          <Validation
            v-for="(error, index) in errors"
            :key="index"
            :validations="error"
          />
          <BaseButton
            type="submit"
            :disabled="!isValid()"
            class="primary full-width export-to-hub__form__button"
          >
            {{ $t("button.exportToHub") }}
          </BaseButton>
        </form>
      </dialog>
    </transition>
  </div>
</template>

<script>
import { useExportToHubViewModel } from "./useExportToHubViewModel";

export default {
  props: {
    dataset: {
      type: Object,
      required: true,
    },
  },
  data: () => ({
    errors: {
      orgOrUsername: [],
      datasetName: [],
      hfToken: [],
    },
  }),
  methods: {
    validateForm(input) {
      this.errors[input] = this.validate()[input];
    },
  },
  setup(props) {
    return useExportToHubViewModel(props);
  },
};
</script>

<style lang="scss" scoped>
.export-to-hub {
  position: relative;
  margin-left: auto;
  margin-right: 0;
  &__title {
    margin-top: 0;
    @include font-size(16px);
    font-weight: 500;
  }
  &__dialog {
    position: absolute;
    right: 0;
    left: auto;
    width: auto;
    min-width: 450px;
    top: calc(100% + $base-space + 2px);
    display: block;
    margin-left: auto;
    padding: $base-space * 2;
    background: var(--bg-accent-grey-1);
    border: 1px solid var(--bg-opacity-10);
    border-radius: $border-radius-m;
    box-shadow: $shadow;
    z-index: 2;
  }

  &__form {
    display: flex;
    flex-direction: column;
    gap: $base-space;

    &__group {
      display: flex;
      flex-direction: column;
      width: 100%;
      gap: calc($base-space/2);
      &.--small {
        max-width: 30%;
      }
    }

    &__dataset {
      display: flex;
      gap: $base-space;
      align-items: flex-end;
    }

    &__separator {
      @include font-size(16px);
      margin-bottom: $base-space;
      color: var(--fg-tertiary);
    }

    &__switch {
      color: var(--fg-primary);
      margin-top: $base-space;
    }

    &__button {
      margin-top: $base-space * 2;
    }
  }

  &__button.button {
    background: hsl(0, 1%, 18%);
    &:hover {
      background: hsl(0, 1%, 22%);
    }
  }

  &__label {
    display: flex;
    align-items: center;
    gap: $base-space;
    color: var(--fg-primary);
    &__info {
      padding: 0;
    }
  }

  input {
    display: flex;
    flex-direction: row;
    align-items: center;
    width: 100%;
    height: 24px;
    padding: 16px;
    background: var(--bg-accent-grey-2);
    color: var(--fg-primary);
    border: 1px solid var(--bg-opacity-20);
    border-radius: $border-radius;
    outline: 0;
    &:focus {
      border: 1px solid var(--bg-action);
    }
  }
}
</style>
