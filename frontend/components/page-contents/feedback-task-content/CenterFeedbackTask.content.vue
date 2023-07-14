<template>
  <RecordFeedbackTaskAndQuestionnaireContent :datasetId="datasetId" />
</template>

<script>
export default {
  name: "CenterFeedbackTaskContent",
  props: {
    datasetId: {
      type: String,
      required: true,
    },
  },
};
</script>
