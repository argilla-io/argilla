<template>
  <transition name="fade" appear>
    <dialog class="dataset-config-dialog" v-click-outside="closeDialog">
      <form
        class="dataset-config-dialog__content"
        @submit.prevent="createDataset"
      >
        <h1
          class="dataset-config-dialog__title"
          v-text="$t('datasetCreation.createDataset')"
        />
        <div class="dataset-config-dialog__row">
          <label
            class="dataset-config-dialog__label"
            for="datasetName"
            v-text="$t('datasetCreation.datasetName')"
          />
          <DatasetConfigurationInput
            id="datasetName"
            v-model="dataset.name"
            :placeholder="$t('datasetCreation.datasetName')"
          />
        </div>
        <div class="dataset-config-dialog__row">
          <label
            class="dataset-config-dialog__label"
            v-text="$t('datasetCreation.assignWorkspace')"
          />
          <template v-if="!workspaces.length">
            <span
              class="dataset-config-dialog__unique-workspace"
              v-text="$t('datasetCreation.none')"
            />
            <Validation :validations="[$t('datasetCreation.noWorkspaces')]" />
          </template>
          <span
            v-else-if="workspaces.length === 1"
            class="dataset-config-dialog__unique-workspace"
            v-text="dataset.workspace.name"
          />
          <DatasetConfigurationSelector
            v-else
            :options="workspaces"
            v-model="dataset.workspace"
          />
        </div>

        <div
          class="dataset-config-dialog__row"
          v-if="dataset.selectedSubset.splits?.length > 1"
        >
          <label
            class="dataset-config-dialog__label"
            v-text="$t('datasetCreation.selectSplit')"
          />
          <DatasetConfigurationSelector
            class="config-form__selector"
            :options="dataset.selectedSubset.splits"
            v-model="dataset.selectedSubset.selectedSplit"
          />
        </div>
        <p
          class="dataset-config-dialog__info"
          v-text="$t('datasetCreation.recordWarning')"
        />
        <BaseButton
          :disabled="!dataset.name || !dataset.workspace || !dataset.isValid"
          :loading="isLoading"
          type="submit"
          class="dataset-config-dialog__button primary full"
          >{{ $t("datasetCreation.button") }}</BaseButton
        >
        <Validation
          v-if="!dataset.isValid"
          :validations="translatedValidations"
        />
      </form>
    </dialog>
  </transition>
</template>
<script>
import Validation from "../../annotation/settings/Validation.vue";
import { useDatasetConfigurationNameAndWorkspace } from "./useDatasetConfigurationNameAndWorkspace";

export default {
  components: { Validation },
  props: {
    dataset: {
      type: Object,
      required: true,
    },
    isLoading: {
      type: Boolean,
      default: false,
    },
  },
  watch: {
    firstWorkspace: {
      handler(value) {
        if (value) {
          this.$set(this.dataset, "workspace", this.firstWorkspace);
        }
      },
      deep: true,
    },
  },
  computed: {
    translatedValidations() {
      return this.dataset.validate().question.map((validation) => {
        return this.$t(validation);
      });
    },
    firstWorkspace() {
      if (this.workspaces.length && !this.dataset.workspace) {
        return this.workspaces[0];
      }
    },
  },
  methods: {
    closeDialog() {
      this.$emit("close-dialog");
    },
    createDataset() {
      if (this.dataset.isValid) {
        this.$emit("create-dataset");
      }
    },
    selectWorkspace(workspace) {
      this.$set(this.dataset, "workspace", workspace);
    },
  },
  setup() {
    return useDatasetConfigurationNameAndWorkspace();
  },
};
</script>

<style lang="scss" scoped>
.dataset-config-dialog {
  position: absolute;
  right: 0;
  left: 0;
  width: calc(100% - $base-space * 3);
  bottom: $base-space;
  display: block;
  margin-left: auto;
  padding: 0;
  border: 1px solid var(--bg-opacity-10);
  border-radius: $border-radius-m;
  box-shadow: $shadow;
  z-index: 1;
  &__header {
    padding: $base-space * 2;
    border-top-left-radius: $border-radius-m;
    border-top-right-radius: $border-radius-m;
    background: linear-gradient(
      90deg,
      hsla(227, 31%, 57%, 0.1) 0%,
      hsla(227, 56%, 52%, 0) 100%
    );
  }
  &__unique-workspace {
    height: $base-space * 4;
    line-height: $base-space * 4;
    padding: 0 $base-space;
    background: var(--bg-opacity-4);
    border: none;
    border-radius: $border-radius;
    color: var(--fg-secondary);
    @include font-size(12px);
    user-select: none;
  }
  &__content {
    display: flex;
    flex-direction: column;
    gap: $base-space;
    padding: $base-space * 2;
  }
  &__row {
    display: flex;
    flex-direction: column;
    gap: calc($base-space / 2);
  }
  &__title {
    font-weight: 500;
    @include font-size(16px);
    margin: 0 0 $base-space 0;
  }
  &__label {
    font-weight: 400;
    @include font-size(14px);
  }
  &__info {
    font-weight: 400;
    @include font-size(11px);
    @include line-height(14px);
    color: var(--fg-tertiary);
    margin-bottom: 0;
  }
  &__button.button {
    justify-content: center;
  }
  .selector {
    &.dropdown {
      @include font-size(12px);
    }
  }
}
.fade-enter-active,
.fade-leave-active {
  transition: all 0.4s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
