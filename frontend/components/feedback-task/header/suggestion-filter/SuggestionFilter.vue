<template>
  <div>
    <div v-for="question in questionFilters.questions">
      {{ question.name }}
    </div>
  </div>
</template>
<script>
import { useSuggestionFilterViewModel } from "./useSuggestionFilterViewModel";

export default {
  props: {
    datasetQuestions: {
      type: Array,
      required: true,
    },
  },
  setup(props) {
    return useSuggestionFilterViewModel(props);
  },
};
</script>
