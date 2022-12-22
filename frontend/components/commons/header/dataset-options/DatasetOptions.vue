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
        this.availableExplanationHelpInfo,
        this.availableSimilarityHelpInfo,
      ];
      return types.filter((type) => type);
    },
    availableExplanationHelpInfo() {
      return this.dataset.results.records.some((record) => record.explanation) && "explain";
    },
    availableSimilarityHelpInfo() {
      return this.dataset.viewSettings.viewMode === "annotate" && 'similarity';
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
