<template>
  <div class="dataset-options">
    <dataset-option-help-info
      class="dataset-options__item"
      v-if="availableHelpInfoType.length"
      :task="task"
      :availableHelpInfoType="availableHelpInfoType"
    />
  </div>
</template>

<script>
export default {
  props: {
    dataset: {
      type: Object,
      required: true,
    },
  },
  computed: {
    availableHelpInfoType() {
      const types = [
        this.isExplanationHelpInfoAvailable,
        this.isSimilarityHelpInfoAvailable,
      ];
      return types.filter((type) => type);
    },
    isExplanationHelpInfoAvailable() {
      return (
        this.dataset.results.records.some((record) => record.explanation) &&
        "explain"
      );
    },
    isSimilarityHelpInfoAvailable() {
      return (
        this.dataset.viewSettings.viewMode !== "labelling-rules" && "similarity"
      );
    },
    task() {
      return this.dataset.task;
    },
  },
};
</script>

<style lang="scss" scoped>
.dataset-options {
  display: flex;
  align-items: center;
  gap: $base-space;
  margin-left: auto;
  &__item {
    display: flex;
    align-items: center;
  }
}
</style>
