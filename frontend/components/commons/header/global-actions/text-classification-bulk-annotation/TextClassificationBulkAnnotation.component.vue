<template>
  <div>
    <BulkAnnotationComponent
      class="bulk-annotation-component"
      :inputs="formattedLabelsForBulkAnnotationForm"
      @on-update-annotations="updateAnnotations"
    />
  </div>
</template>

<script>
export default {
  name: "TextClassificationBulkAnnotation",
  props: {
    datasetId: {
      type: Array,
      required: true,
    },
    records: {
      type: Array,
      required: true,
    },
    labels: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      labelsByRecordId: [],
    };
  },
  computed: {
    formattedLabelsForBulkAnnotationForm() {
      return this.initLabelForForm();
    },
  },
  methods: {
    initLabelForForm() {
      let labelsForForm = this.labelsForFormFactory();
      labelsForForm = this.updateLabelByCurrentAnnotation(labelsForForm);
      return labelsForForm;
    },
    labelsForFormFactory() {
      return this.labels.map((label) => ({
        record_ids: new Set(),
        id: label,
        label: label,
        selected: false,
        unmodified: false,
      }));
    },
    updateLabelByCurrentAnnotation(labelsForForm) {
      this.records.map((record) => {
        record.currentAnnotation?.labels.map((currLabelObj) => {
          labelsForForm.forEach((labelObj) => {
            if (labelObj.label === currLabelObj.class) {
              labelObj.record_ids.add(record.id);
              labelObj.selected = this.updateSelectedAttribute(
                labelObj.record_ids.size
              );
            }
          });
        });
      });
      return labelsForForm;
    },
    updateSelectedAttribute(numberOfRecordsWithThisLabel) {
      //NOTE - when the list numberOfRecordsWithThisLabel is equal to the nuber of records
      //        => all the records contains the same label
      return numberOfRecordsWithThisLabel === this.records.length;
    },
    updateAnnotations(updatedAnnotations) {
      this.$emit("on-update-annotations", updatedAnnotations);
    },
  },
};
</script>

<style lang="scss" scoped></style>
