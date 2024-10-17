<template>
  <transition name="fade" appear>
    <dialog class="dataset-config-dialog" v-click-outside="closeDialog">
      <form
        class="dataset-config-dialog__content"
        @submit.prevent="createDataset"
      >
        <h1 class="dataset-config-dialog__title">
          Create the dataset in Argilla
        </h1>
        <div class="dataset-config-dialog__row">
          <label class="dataset-config-dialog__label" for="datasetName"
            >Dataset name</label
          >
          <DatasetConfigurationInput
            id="datasetName"
            v-model="dataset.name"
            placeholder="Name"
          />
        </div>
        <div class="dataset-config-dialog__row">
          <label class="dataset-config-dialog__label">Assign a workspace</label>
          <DatasetConfigurationSelector
            :options="workspaces"
            v-model="dataset.workspace"
          />
        </div>
        <div class="dataset-config-dialog__row" v-if="dataset.splits">
          <label class="dataset-config-dialog__label">Select a split</label>
          <DatasetConfigurationSelector
            class="config-form__selector"
            :options="dataset.splits"
            v-model="dataset.selectedSplit.value"
          />
        </div>
        <p class="dataset-config-dialog__info">
          The created dataset will include the first xK rows and further records
          can be logged via the python SDK.
        </p>
        <BaseButton
          :disabled="!dataset.name"
          :loading="isLoading"
          type="submit"
          class="dataset-config-dialog__button primary full"
          >Create dataset</BaseButton
        >
      </form>
    </dialog>
  </transition>
</template>
<script>
import { useDatasetConfigurationNameAndWorkspace } from "./useDatasetConfigurationNameAndWorkspace";

export default {
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
  methods: {
    closeDialog() {
      this.$emit("close-dialog");
    },
    createDataset() {
      this.$emit("create-dataset");
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
    @include font-size(13px);
    color: var(--fg-tertiary);
    margin-bottom: 0;
  }
  &__button.button {
    justify-content: center;
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
