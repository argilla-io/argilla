<template>
  <div class="wrapper">
    <section class="wrapper__records">
      <DatasetFiltersComponent :recordCriteria="recordCriteria">
        <ToggleAnnotationType
          v-if="
            records.hasRecordsToAnnotate && recordCriteria.committed.isPending
          "
          :recordCriteria="recordCriteria"
      /></DatasetFiltersComponent>
      <SimilarityRecordReference
        v-show="recordCriteria.isFilteringBySimilarity"
        v-if="!!records.reference"
        :fields="records.reference.fields"
        :recordCriteria="recordCriteria"
        :availableVectors="datasetVectors"
      />
      <div class="wrapper__records__header">
        <PaginationFeedbackTaskComponent :recordCriteria="recordCriteria" />
      </div>
      <Record
        v-if="records.hasRecordsToAnnotate"
        :datasetVectors="datasetVectors"
        :recordCriteria="recordCriteria"
        :record="record"
      />
      <div v-else class="wrapper--empty">
        <p class="wrapper__text --heading3" v-text="noRecordsMessage" />
      </div>
    </section>

    <QuestionsFormComponent
      v-if="!!record"
      :key="`${record.id}_questions`"
      class="wrapper__form"
      :class="statusClass"
      :datasetId="recordCriteria.datasetId"
      :record="record"
      :show-discard-button="!record.isDiscarded"
      :is-draft-saving="isDraftSaving"
      :is-submitting="isSubmitting"
      :is-discarding="isDiscarding"
      @on-submit-responses="onSubmit"
      @on-discard-responses="onDiscard"
      @on-save-draft="onSaveDraft"
    />
  </div>
</template>
<script>
import { useFocusAnnotationViewModel } from "./useFocusAnnotationViewModel";
export default {
  props: {
    recordCriteria: {
      type: Object,
      required: true,
    },
    datasetVectors: {
      type: Array,
      required: false,
    },
    records: {
      type: Object,
      required: true,
    },
    record: {
      type: Object,
    },
    noRecordsMessage: {
      type: String,
      required: true,
    },
    statusClass: {
      type: String,
      required: true,
    },
  },
  methods: {
    async onSubmit() {
      await this.submit(this.record);
      this.$emit("on-submit-responses");
    },
    async onDiscard() {
      if (this.record.isDiscarded) return;

      await this.discard(this.record);
      this.$emit("on-discard-responses");
    },
    async onSaveDraft() {
      await this.saveAsDraft(this.record);
    },
  },
  setup() {
    return useFocusAnnotationViewModel();
  },
};
</script>

<style lang="scss" scoped>
.wrapper {
  display: flex;
  flex-wrap: wrap;
  height: 100%;
  gap: $base-space * 2;
  padding: $base-space * 2;
  @include media("<desktop") {
    flex-flow: column;
    overflow: auto;
  }
  &__records,
  &__form {
    @include media("<desktop") {
      overflow: visible;
      height: auto;
      max-height: none !important;
    }
  }
  &__records {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: $base-space;
    height: 100%;
    min-width: 0;
    &__header {
      display: flex;
      justify-content: flex-end;
      align-items: center;
      gap: $base-space;
    }
  }
  &__text {
    color: $black-54;
  }
  &--empty {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}
</style>
