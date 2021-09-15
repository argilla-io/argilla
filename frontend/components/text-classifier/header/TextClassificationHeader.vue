<template>
  <div>
    <header-title title="Text Classification" v-if="dataset.results.records" :dataset="dataset" />
    <filters-area :dataset="dataset" />
    <global-actions :dataset="dataset">
      <validate-discard-action
        :dataset="dataset"
        @discard-records="onDiscard"
        @validate-records="onValidate"
      >
        <template slot="first" slot-scope="validateDiscard">
          <annotation-label-selector
            :class="'validate-discard-actions__select'"
            :multi-label="isMultiLabelRecord"
            :options="availableLabels"
            @selected="onSelectLabels($event, validateDiscard.selectedRecords)"
          />
        </template>
      </validate-discard-action>
      <create-new-action @new-label="onNewLabel" />
    </global-actions>
  </div>
</template>
<script>
import { mapActions } from "vuex";
export default {
  props: {
    dataset: {
      type: Object,
      required: true,
    },
  },
  computed: {
    isExplainedRecord() {
      return this.dataset.results.records.some((record) => record.explanation);
    },
    showAnnotationMode() {
      return this.dataset.viewSettings.annotationEnabled;
    },
    isMultiLabelRecord() {
      return this.dataset.visibleRecords.some((record) => record.multi_label);
    },
    availableLabels() {
      const record = this.dataset.results.records[0];
      let labels =
        record && record.prediction
          ? record.prediction.labels.map((label) => label.class)
          : [];
      labels = Array.from(new Set([...labels, ...this.dataset.labels]));
      return labels;
    },
  },
  methods: {
    ...mapActions({
      updateRecords: "entities/datasets/updateRecords",
      discard: "entities/datasets/discardAnnotations",
      validate: "entities/datasets/validateAnnotations",
    }),
    async onSelectLabels(labels, selectedRecords) {
      const records = selectedRecords.map((record) => {
        const appliedLabels = record.annotation
          ? [...record.annotation.labels]
          : [];

        const filterAppliedLabels = labels.filter(
          (l) => appliedLabels.map((label) => label.class).indexOf(l) === -1
        );

        let newLabels = this.isMultiLabelRecord ? filterAppliedLabels : labels;
        newLabels = newLabels.map((label) => ({
          class: label,
          score: 1.0,
        }));
        return {
          ...record,
          annotation: {
            agent: this.$auth.user,
            labels: this.isMultiLabelRecord
              ? [...appliedLabels, ...newLabels]
              : newLabels,
          },
        };
      });
      await this.validate({ dataset: this.dataset, records: records });
    },
    async onDiscard(records) {
      await this.discard({
        dataset: this.dataset,
        records: records,
      });
    },
    async onValidate(records) {
      await this.validate({
        dataset: this.dataset,
        records: records,
      });
    },
    async onNewLabel(newLabel) {
      if (this.isTextClassification) {
        await this.dataset.$dispatch("setLabels", {
          dataset: this.dataset,
          labels: [...new Set([...this.dataset.labels, newLabel])],
        });
      }
    },
  },
};
</script>
