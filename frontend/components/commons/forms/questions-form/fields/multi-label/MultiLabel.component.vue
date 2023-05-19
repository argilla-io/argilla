<template>
  <div class="">
    <ClassifierAnnotationForFeedbackTaskComponent
      v-if="inputId && options"
      :maxVisibleLabels="100"
      :inputLabels="formattedOptionsForClassifierAnnotationComponent"
      :datasetName="'feedbackTask'"
      :isMultiLabel="true"
      :paginationSize="10"
      :record="formattedSelectedInputsClassifierAnnotationComponent"
      @update-labels="onChangeClassifierAnnotation"
    />
  </div>
</template>

<script>
export default {
  name: "MultiLabelComponent",
  props: {
    inputId: {
      type: String,
      required: true,
    },
    options: {
      type: Array,
      required: true,
    },
  },
  computed: {
    formattedOptionsForClassifierAnnotationComponent() {
      return this.options.reduce((acc, curr) => acc.concat(curr.text), []);
    },
    currentAnnotation() {
      const labels = this.options.reduce((acc, curr) => {
        if (curr.value) return acc.concat({ class: curr.text });
        return acc;
      }, []);

      return { labels };
    },
    formattedSelectedInputsClassifierAnnotationComponent() {
      // NOTE - inputId is only necessary because the child component use the scroll plugin which need an id
      const { inputId, currentAnnotation } = this;
      return {
        id: inputId,
        currentAnnotation,
      };
    },
  },
  methods: {
    onChangeClassifierAnnotation($event) {
      const { options } = this;

      options.forEach((option) => {
        if ($event.includes(`${option.text}`)) {
          option.value = true;
        } else {
          option.value = false;
        }
      });

      this.$emit("on-change-multilabel", options);
    },
  },
};
</script>
