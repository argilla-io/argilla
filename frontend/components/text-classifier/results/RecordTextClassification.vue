<template>
  <div class="record">
    <!-- annotation labels and prediction status -->
    <div class="record--left">
      <!-- record text -->
      <RecordInputs
        :predicted="record.predicted"
        :data="record.inputs"
        :explanation="record.explanation"
        :query-text="dataset.query.text"
      />
      <!-- record annotation area -->
      <ClassifierAnnotationArea
        v-if="annotationEnabled"
        :labels="labelsForAnnotation"
        :multi-label="record.multi_label"
        @annotate="onAnnotate"
        @edit="onEdit"
      />
      <ClassifierExplorationArea v-else :labels="predictionLabels" />
    </div>
    <div v-if="!annotationEnabled" class="record__labels">
      <LabelPill
        v-if="record.annotation && !annotationEnabled"
        class="annotations"
        :labels="record.annotation.labels"
        :predicted="record.predicted"
      />
    </div>
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
      return this.dataset.viewSettings.annotationEnabled;
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
      validate: "entities/datasets/validateAnnotations",
      edit: "entities/datasets/editAnnotations",
    }),

    async onEdit({ labels }) {
      await this.edit({
        dataset: this.dataset,
        records: [
          {
            ...this.record,
            status: "Edited",
            annotation: {
              agent: this.$auth.user,
              labels,
            },
          },
        ],
      });
    },

    async onAnnotate({ labels }) {
      await this.validate({
        dataset: this.dataset,
        agent: this.$auth.user,
        records: [
          {
            ...this.record,
            status: ["Discarded", "Validated"].includes(this.record.status)
              ? "Edited"
              : this.record.status,
            annotation: {
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

<style scoped lang="scss">
.record {
  display: flex;
  &--left {
    width: 100%;
    padding: 2em 2em 0.5em 2em;
    .list__item--annotation-mode & {
      padding-left: 65px;
    }
  }
  &__labels {
    position: relative;
    border-left: 1px solid palette(grey, bg);
    margin-left: 2em;
    width: 170px;
    flex-shrink: 0;
    margin-bottom: -3em;
  }
}
</style>
