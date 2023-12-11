<template>
  <div class="wrapper">
    <section class="wrapper__records">
      <DatasetFiltersComponent :recordCriteria="recordCriteria">
        <ToggleAnnotationType
          v-if="records.hasRecordsToAnnotate && record.status === 'pending'"
          :value="bulkAnnotation"
          @change="changeAnnotationType"
      /></DatasetFiltersComponent>
      <div class="wrapper__records__header">
        <BaseCheckbox
          v-if="records.hasRecordsToAnnotate"
          class="wrapper__records__header__checkbox"
          :value="filteredSelectedRecords.length === records.records.length"
          @input="toggleAllRecords"
        />
        <PageSizeSelector :options="[10, 25, 50, 100]" v-model="pageSize" />
        <PaginationFeedbackTaskComponent :recordCriteria="recordCriteria" />
      </div>
      <div class="bulk__records">
        <RecordFieldsAndSimilarity
          v-for="(r, index) in records.records"
          :key="r.id"
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
import { useQuestionFormViewModel } from "./questions/useQuestionsFormViewModel";
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
  data() {
    return {
      selectedRecords: [],
      pageSize: 10,
    };
  },
  model: {
    prop: "bulkAnnotation",
    event: "change",
  },
  computed: {
    filteredSelectedRecords() {
      return this.selectedRecords.filter((r) => r);
    },
  },
  methods: {
    changeAnnotationType(value) {
      this.$emit("change", value);
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
    },
    toggleAllRecords() {
      if (this.filteredSelectedRecords.length === this.records.records.length) {
        this.selectedRecords = [];
      } else {
        this.selectedRecords = this.records.records.map((r) => r.id);
      }
    },
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
