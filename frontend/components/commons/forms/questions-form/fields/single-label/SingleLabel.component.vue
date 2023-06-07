<template>
  <div class="wrapper">
    <QuestionHeaderComponent
      :title="title"
      :isRequired="isRequired"
      :tooltipMessage="description"
    />

    <LabelSelectionComponent
      v-model="uniqueOptions"
      :multiple="false"
      :componentId="questionId"
      :showSearch="showSearch"
      :maxOptionsToShowBeforeCollapse="maxOptionsToShowBeforeCollapse"
    />
  </div>
</template>

<script>
import { OPTIONS_THRESHOLD_TO_ENABLE_SEARCH } from "@/components/feedback-task/feedbackTask.properties";
export default {
  name: "SingleLabelComponent",
  props: {
    questionId: {
      type: String,
      required: true,
    },
    title: {
      type: String,
      required: true,
    },
    options: {
      type: Array,
      required: true,
    },
    isRequired: {
      type: Boolean,
      default: () => false,
    },
    description: {
      type: String,
      default: () => "",
    },
    visibleOptions: {
      type: Number | null,
      required: false,
    },
  },
  model: {
    prop: "options",
  },
  data() {
    return {
      uniqueOptions: [],
    };
  },
  beforeMount() {
    this.uniqueOptions = this.options.reduce((accumulator, current) => {
      if (!accumulator.find((item) => item.id === current.id)) {
        accumulator.push(current);
      }
      return accumulator;
    }, []);
  },
  computed: {
    showSearch() {
      return this.uniqueOptions.length >= OPTIONS_THRESHOLD_TO_ENABLE_SEARCH;
    },
    maxOptionsToShowBeforeCollapse() {
      return this.visibleOptions ?? -1;
    },
  },
};
</script>

<style lang="scss" scoped>
.wrapper {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
</style>
