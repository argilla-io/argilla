<template>
  <BaseLoading v-if="$fetchState.pending" />
  <RecordFeedbackTaskAndQuestionnaireContent
    v-else
    :datasetId="datasetId"
    :feedback="feedback"
  />
</template>

<script>
import { useFeedbackTaskViewModel } from "./useFeedbackTaskViewModel";

export default {
  name: "CenterFeedbackTaskContent",
  props: {
    datasetId: {
      type: String,
      required: true,
    },
  },
  fetch() {
    return this.loadFeedback(this.datasetId);
  },
  setup() {
    return useFeedbackTaskViewModel();
  },
};
</script>
