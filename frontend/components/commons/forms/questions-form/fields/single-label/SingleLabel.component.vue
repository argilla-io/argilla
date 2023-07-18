<template>
  <div class="wrapper">
    <QuestionHeaderComponent
      :title="title"
      :isRequired="isRequired"
      :hasSuggestion="hasSuggestion"
      :tooltipMessage="description"
    />

    <LabelSelectionComponent
      v-model="uniqueOptions"
      :multiple="false"
      :componentId="questionId"
      :maxOptionsToShowBeforeCollapse="maxOptionsToShowBeforeCollapse"
    />
  </div>
</template>

<script>
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
    hasSuggestion: {
      type: Boolean,
      default: () => false,
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
