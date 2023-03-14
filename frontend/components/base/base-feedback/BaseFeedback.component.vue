<template>
  <BaseFeedbackErrorComponent
    id="daboudi"
    v-if="isFeedbackError"
    :message="feedbackInput.message"
    :buttonLabels="feedbackInput.buttonLabels"
    @on-click="onClick"
  />
  <div v-else>{{ feedbackType }}</div>
</template>

<script>
const FEEDBACK_TYPES = {
  WARNING: "WARNING",
  INFO: "INFO",
  ERROR: "ERROR",
  SUCCESS: "SUCCESS",
};

export default {
  name: "BaseFeedBackComponent",
  props: {
    feedbackInput: {
      type: Object,
      required: true,
    },
  },
  computed: {
    feedbackType() {
      return this.feedbackInput.feedbackType;
    },
    isFeedbackError() {
      return this.feedbackType === FEEDBACK_TYPES.ERROR;
    },
  },
  methods: {
    onClick(buttonLabel) {
      this.$emit("on-click", buttonLabel);
    },
  },
};
</script>
