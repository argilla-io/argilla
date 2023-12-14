<template>
  <div class="wrapper">
    <section class="wrapper__records">
      <DatasetFiltersComponent :recordCriteria="recordCriteria">
        <ToggleAnnotationType
          v-if="records.hasRecordsToAnnotate && record?.isPending"
          :recordCriteria="recordCriteria"
      /></DatasetFiltersComponent>
      <div class="wrapper__records__header">
        <BaseCheckbox
          v-if="records.hasRecordsToAnnotate"
          class="wrapper__records__header__checkbox"
          :value="filteredSelectedRecords.length === records.records.length"
          @input="toggleAllRecords"
        />
        <PageSizeSelector
          :options="recordCriteria.page.options"
          v-model="recordCriteria.page.client.many"
        />
        <PaginationFeedbackTaskComponent :recordCriteria="recordCriteria" />
      </div>
      <div class="bulk__records">
        <RecordFieldsAndSimilarity
          v-for="(record, index) in records.records
            .slice(recordCriteria.page.client.page - 1)
            .splice(0, recordCriteria.page.client.many)"
          :key="record.id"
          :datasetVectors="datasetVectors"
          :records="records"
          :recordCriteria="recordCriteria"
          :record="record"
          :selectable-record="true"
          v-model="selectedRecords[index]"
          :fixed-header="true"
        />
      </div>
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
      @on-clear="onClear"
      @on-save-draft="onSaveDraft"
      @on-save-draft-immediately="onSaveDraftImmediately"
    />
  </div>
</template>
<script>
import { useBulkAnnotationQuestionFormViewModel } from "./questions/useBulkAnnotationQuestionsFormViewModel";
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
  data() {
    return {
      selectedRecords: [],
    };
  },
  computed: {
    filteredSelectedRecords() {
      return this.selectedRecords.filter((r) => r);
    },
  },
  methods: {
    async onSubmit() {
      if (this.isSubmitButtonDisabled) return;

      await this.submit(this.filteredSelectedRecords, this.record);
      this.$emit("on-submit-responses");
    },
    async onDiscard() {
      if (this.record.isDiscarded) return;

      await this.discard(this.filteredSelectedRecords, this.record);
      this.$emit("on-discard-responses");
    },
    async onClear() {
      // await this.clear(this.record);
    },
    async onSaveDraft() {
      // await this.saveDraft(this.record);
    },
    async onSaveDraftImmediately() {
      // await this.saveDraftImmediately(this.record);
    },
    toggleAllRecords() {
      if (this.filteredSelectedRecords.length === this.records.records.length) {
        this.selectedRecords = [];
      } else {
        this.selectedRecords = this.records.records.map((r) => r.id);
      }
    },
  },
  watch: {
    "recordCriteria.page.client.many"() {
      this.recordCriteria.page.goToFirst();

      this.$root.$emit("on-change-record-criteria-filter", this.recordCriteria);
    },
  },
  setup() {
    return useBulkAnnotationQuestionFormViewModel();
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
      padding: $base-space $base-space * 2;
      border: 1px solid $black-10;
      background: palette(white);
      border-radius: $border-radius-m;
      &__checkbox {
        margin-left: 0;
        margin-right: auto;
      }
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
.bulk {
  &__records {
    display: flex;
    flex-direction: column;
    gap: $base-space;
    height: 100%;
    overflow: auto;
    @extend %hide-scrollbar;
    .fields {
      max-height: 300px;
      min-height: auto;
    }
  }
}
</style>
