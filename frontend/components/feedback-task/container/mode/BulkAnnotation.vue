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
      <div class="wrapper__records__header">
        <BaseCheckbox
          v-if="records.hasRecordsToAnnotate"
          class="wrapper__records__header__checkbox"
          :value="selectedRecords.length === recordsOnPage.length"
          @input="toggleAllRecords"
        />
        <PaginationFeedbackTaskComponent :recordCriteria="recordCriteria" />
      </div>
      <div class="bulk__records">
        <RecordFieldsAndSimilarity
          v-for="(record, i) in recordsOnPage"
          :key="record.id"
          :datasetVectors="datasetVectors"
          :records="records"
          :recordCriteria="recordCriteria"
          :record="record"
          :fixed-header="true"
          :show-record-similar="i === 0"
          :selectable-record="true"
          :selectedRecords="selectedRecords"
          @on-select-record="onSelectRecord"
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
      :is-draft-saving="isDraftSaving"
      :is-submitting="isSubmitting"
      :is-discarding="isDiscarding"
      :are-actions-enabled="hasSelectedAtLeastOneRecord"
      @on-submit-responses="onSubmit"
      @on-discard-responses="onDiscard"
      @on-save-draft="onSaveDraft"
    />
  </div>
</template>
<script>
import { useBulkAnnotationViewModel } from "./useBulkAnnotationViewModel";
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
    recordsOnPage() {
      return this.records.getRecordsOn(this.recordCriteria.committed.page);
    },
    hasSelectedAtLeastOneRecord() {
      return this.selectedRecords.length > 0;
    },
  },
  methods: {
    onSelectRecord(isSelected, record) {
      if (isSelected) {
        return this.selectedRecords.push(record);
      }

      this.selectedRecords = this.selectedRecords.filter(
        (r) => r.id !== record.id
      );
    },
    async onSubmit() {
      await this.submit(this.selectedRecords, this.record);

      this.$emit("on-submit-responses");
    },
    async onDiscard() {
      await this.discard(this.selectedRecords, this.record);

      this.$emit("on-discard-responses");
    },
    async onSaveDraft() {
      await this.saveAsDraft(this.selectedRecords, this.record);
    },
    toggleAllRecords() {
      if (this.selectedRecords.length === this.recordsOnPage.length) {
        this.selectedRecords = [];
      } else {
        this.selectedRecords = [...this.recordsOnPage];
      }
    },
  },
  watch: {
    "recordCriteria.status"() {
      this.recordCriteria.page.focusMode();
    },
    "recordCriteria.committed.page"() {
      this.selectedRecords = [];
    },
    "recordCriteria.page.client.many"() {
      this.recordCriteria.page.goToFirst();

      this.$root.$emit("on-change-record-criteria-filter", this.recordCriteria);
    },
  },
  setup() {
    return useBulkAnnotationViewModel();
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
