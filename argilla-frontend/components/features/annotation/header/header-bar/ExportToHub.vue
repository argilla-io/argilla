<template>
  <div class="export-to-hub" @keydown.stop="">
    <BaseButton
      class="primary export-to-hub__button"
      @click.prevent="isDialogVisible = !isDialogVisible"
      :loading="isExporting"
      :disabled="isExporting"
      >{{ $t("button.exportToHub") }}</BaseButton
    >
    <transition name="fade" appear>
      <dialog
        v-if="isDialogVisible"
        v-click-outside="closeDialog"
        class="export-to-hub__dialog"
      >
        <div class="export-to-hub__form">
          <div class="export-to-hub__form__group">
            <label v-text="$t('datasetCreation.datasetName')" />
            <div class="export-to-hub__form-dataset">
              <input
                type="text"
                v-model="exportToHubForm.orgOrUsername"
                class="input"
                :placeholder="$t('orgOrUsername')"
              />
              /
              <input
                type="text"
                v-model="exportToHubForm.datasetName"
                class="input"
                :placeholder="$t('datasetCreation.datasetName')"
              />
            </div>
          </div>

          <div class="export-to-hub__form__group">
            <BaseSwitch v-model="exportToHubForm.isPrivate">{{
              $t("private")
            }}</BaseSwitch>
          </div>

          <div class="export-to-hub__form__group">
            <label v-text="$t('hfToken')" />
            <input
              type="text"
              v-model="exportToHubForm.hfToken"
              class="input"
              :placeholder="$t('hfToken')"
            />
          </div>

          <div>
            <BaseButton
              class="primary export-to-hub__button"
              :loading="isExporting"
              :disabled="isExporting"
              @click.prevent="exportToHub"
            >
              Export to hub
            </BaseButton>
          </div>
        </div>
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
  data() {
    return {
      isDialogVisible: false,
    };
  },
  methods: {
    closeDialog() {
      this.isDialogVisible = false;
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

  &__dialog {
    position: absolute;
    right: 0;
    left: auto;
    width: auto;
    min-width: 560px;
    top: calc(100% + $base-space);
    display: block;
    margin-left: auto;
    padding: $base-space * 2;
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
      gap: 12px;
    }

    &-dataset {
      display: flex;
      gap: $base-space;
      align-items: center;
    }
  }

  &__button.button {
    background: hsl(0, 1%, 18%);
    &:hover {
      background: hsl(0, 1%, 22%);
    }
  }
}

label {
  width: fit-content;
  height: 14px;
  color: var(--fg-secondary);
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
</style>
