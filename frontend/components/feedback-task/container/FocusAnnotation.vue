<template>
  <div class="wrapper">
    <section class="wrapper__records">
        FOCUS
      <DatasetFiltersComponent :recordCriteria="recordCriteria">
        <ToggleAnnotationType
          v-if="records.hasRecordsToAnnotate && record.status === 'pending'"
          :value="bulkAnnotation"
          @change="changeAnnotationType"
        />
      </DatasetFiltersComponent>
      <PaginationFeedbackTaskComponent :recordCriteria="recordCriteria" />
      <RecordFieldsAndSimilarity
        :datasetVectors="datasetVectors"
        :records="records"
        :recordCriteria="recordCriteria"
        :record="record"
      />
      <div v-if="!records.hasRecordsToAnnotate" class="wrapper--empty">
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
      :draft-saving="draftSaving"
      :is-submitting="isSubmitting"
      :is-discarding="isDiscarding"
      @on-submit-responses="onSubmit"
      @on-discard-responses="onDiscard"
      @on-clear-responses="onClear"
      @on-save-draft="onSaveDraft"
      @on-save-draft-immediately="onSaveDraftImmediately"
    />
  </div>
</template>
<script>
import { useQuestionFormViewModel } from './questions/useQuestionsFormViewModel';
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
    bulkAnnotation: {
      type: Boolean,
      required: true,
    },
  },
  model: {
    prop: "bulkAnnotation",
    event: "change",
  },
  methods: {
    changeAnnotationType(value) {
      this.$emit("change", value);
      console.log(value);
    },
    async onSubmit() {
      if (this.isSubmitButtonDisabled) return;

      await this.submit(this.record);
      this.$emit("on-submit-responses");
    },
    async onDiscard() {
      if (this.record.isDiscarded) return;

      await this.discard(this.record);
      this.$emit("on-discard-responses");
    },
    async onClear() {
        await this.clear(this.record);
    },
    async onSaveDraft() {
      await this.saveDraft(this.record);
    },
    async onSaveDraftImmediately() {
       await this.saveDraftImmediately(this.record);
    }
  },
  setup() {
    return useQuestionFormViewModel();
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