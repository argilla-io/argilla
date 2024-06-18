<template>
  <VerticalResizable class="wrapper" :id="`${recordCriteria.datasetId}-r-v-rz`">
    <template #left>
      <HorizontalResizable
        :id="`${recordCriteria.datasetId}-r-h-rz`"
        class="wrapper__left"
      >
        <template #up>
          <section class="wrapper__records">
            <DatasetFilters :recordCriteria="recordCriteria">
              <ToggleAnnotationType
                v-if="
                  records.hasRecordsToAnnotate &&
                  recordCriteria.committed.isPending
                "
                :recordCriteria="recordCriteria"
            /></DatasetFilters>
            <SimilarityRecordReference
              v-show="recordCriteria.isFilteringBySimilarity"
              v-if="!!records.reference"
              :fields="records.reference.fields"
              :recordCriteria="recordCriteria"
              :availableVectors="datasetVectors"
            />
            <div class="wrapper__records__header">
              <PaginationFeedbackTask :recordCriteria="recordCriteria" />
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
        </template>

        <template #downHeader>
          <p v-text="$t('guidelines')" />
        </template>
        <template #downContent>
          <AnnotationGuidelines />
        </template>
      </HorizontalResizable>
    </template>

    <template #right>
      <HorizontalResizable
        :id="`${recordCriteria.datasetId}-q-h-rz}`"
        class="wrapper__right"
      >
        <template #up>
          <QuestionsForm
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
            :enableAutoSubmitWithKeyboard="true"
            @on-submit-responses="onSubmit"
            @on-discard-responses="onDiscard"
            @on-save-draft="onSaveDraft"
          />
        </template>
        <template #downHeader>
          <p v-text="$t('metrics.progress')" />
          <AnnotationProgress
            class="annotation-progress"
            :datasetId="recordCriteria.datasetId"
            enableFetch
          />
        </template>
        <template #downContent>
          <AnnotationProgress :datasetId="recordCriteria.datasetId" />
          <AnnotationProgressDetailed :datasetId="recordCriteria.datasetId" />
        </template>
      </HorizontalResizable>
    </template>
    <BaseCollapsablePanel
      class="--mobile"
      :is-expanded="expandedGuidelines"
      @toggle-expand="expandedGuidelines = !expandedGuidelines"
    >
      <template #panelHeader>
        <p v-text="$t('guidelines')" />
      </template>
      <template #panelContent>
        <AnnotationGuidelines />
      </template>
    </BaseCollapsablePanel>
  </VerticalResizable>
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
  data() {
    return {
      expandedGuidelines: false,
    };
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
  position: relative;
  display: flex;
  flex-wrap: wrap;
  height: 100%;
  &__inner {
    display: flex;
  }
  @include media("<desktop") {
    flex-flow: column;
    overflow: auto;
  }
  &__left,
  &__right {
    @include media("<desktop") {
      overflow: visible;
      height: auto !important;
      max-height: none !important;
    }
  }
  &__left {
    @include media("<desktop") {
      :deep(.resizable__down) {
        display: none;
      }
    }
  }
  &__form {
    padding: $base-space * 2;
  }
  &__records {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: $base-space;
    height: 100%;
    min-width: 0;
    padding: $base-space * 2;
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
.annotation-progress {
  .--expanded & {
    display: none;
  }
}
.--mobile {
  @include media(">=desktop") {
    display: none;
  }
}
</style>
