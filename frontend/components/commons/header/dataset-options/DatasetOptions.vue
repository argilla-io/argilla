<template>
  <div class="dataset-options">
    <dataset-option-help-info
      class="dataset-options__item"
      v-if="availableHelpInfo"
      :task="task"
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
    availableHelpInfo() {
      return this.dataset.results.records.some((record) => record.explanation);
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
