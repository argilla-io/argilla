<template>
  <div>
    <!-- annotation labels and prediction status -->
    <LabelPill
      v-if="record.annotation && !annotationEnabled"
      class="annotations"
      :labels="record.annotation.labels"
      :predicted="record.predicted"
    />
    <!-- record text -->
    <RecordInputs :data="record.inputs" :queryText="dataset.query.text" />
    <!-- record annotation area -->
    <ClassifierAnnotationArea
      v-if="annotationEnabled"
      :labels="labelsForAnnotation"
      :multi-label="record.multi_label"
      @annotate="onAnnotate"
      @updateStatus="onChangeRecordStatus"
    />
    <ClassifierExplorationArea v-else :labels="predictionLabels" />
    <RecordExtraActions
      :allow-validate="false"
      :annotation-mode="annotationEnabled"
      :record="record"
      @onChangeRecordStatus="onChangeRecordStatus"
      @onShowMetadata="$emit('onShowMetadata')"
    />
  </div>
</template>
<script>
import {
  TextClassificationRecord,
  TextClassificationDataset,
} from "@/models/TextClassification";
import { mapActions } from "vuex";
export default {
  props: {
    dataset: {
      type: TextClassificationDataset,
      required: true,
    },
    record: {
      type: TextClassificationRecord,
      required: true,
    },
  },
  data: () => ({}),
  computed: {
    labelsForAnnotation() {
      const labelsDict = {};

      this.dataset.labels.forEach((label) => {
        labelsDict[label] = { confidence: 0, selected: false };
      });

      let annotationLabels = this.annotationLabels.map((label) => {
        return {
          ...label,
          selected: true,
        };
      });

      this.predictionLabels.concat(annotationLabels).forEach((label) => {
        labelsDict[label.class] = {
          confidence: label.confidence,
          selected: label.selected,
        };
      });

      return Object.keys(labelsDict).map((label) => {
        return {
          class: label,
          confidence: labelsDict[label].confidence,
          selected: labelsDict[label].selected,
        };
      });
    },
    annotationEnabled() {
      return this.dataset.viewSettings.annotationEnabled
    },
    annotationLabels() {
      return this.record.annotation ? this.record.annotation.labels : [];
    },
    predictionLabels() {
      return this.record.prediction ? this.record.prediction.labels : [];
    },
  },
  methods: {
    ...mapActions({
      editAnnotations: "entities/datasets/editAnnotations",
      discard: "entities/datasets/discardAnnotations",
      validate: "entities/datasets/validateAnnotations",
    }),
    async onChangeRecordStatus(status) {
      switch (status) {
        case "Validated":
          await this.validate({
            dataset: this.dataset,
            records: [this.record],
          });
          break;
        case "Discarded":
          await this.discard({
            dataset: this.dataset,
            records: [this.record],
          });
          break;
        case "Edited":
          await this.editAnnotations({
            dataset: this.dataset,
            records: [
              {
                ...this.record,
                status: "Edited",
                annotation: {
                  agent: this.$auth.user,
                  labels: [],
                },
              },
            ],
          });
          break;
        default:
          console.log("waT?", status);
      }
    },
    async onAnnotate({ labels }) {
      console.log(labels)
      await this.validate({
        dataset: this.dataset,
        records: [
          {
            ...this.record,
            status: ["Discarded", "Validated"].includes(this.record.status)
              ? "Edited"
              : this.record.status,
            annotation: {
              agent: this.$auth.user,
              labels: labels.map((label) => ({
                class: label,
                confidence: 1.0,
              })),
            },
          },
        ],
      });
    },
  },
};
</script>
<style lang="scss" scoped>
.record {
  @include font-size(15px);
}
</style>
