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
            <div v-if="recordsMessage" class="wrapper--empty">
              <p class="wrapper__text --heading3" v-html="recordsMessage" />
            </div>
            <Record
              v-else
              :datasetVectors="datasetVectors"
              :recordCriteria="recordCriteria"
              :record="record"
            />
          </section>
        </template>
        <template #downHeader>
          <p v-text="$t('guidelines')" />
        </template>
        <template #downHeaderExpanded>
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
          <AnnotationProgress
            class="annotation-progress"
            :datasetId="recordCriteria.datasetId"
          />
        </template>
        <template #downHeaderExpanded>
          <p v-text="$t('metrics.progress.my')" />
        </template>
        <template #downContent>
          <AnnotationProgressDetailed :datasetId="recordCriteria.datasetId" />
        </template>
      </HorizontalResizable>
    </template>
    <BaseCollapsablePanel
      hideOnDesktop
      :isExpanded="expandedGuidelines"
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
    recordsMessage: {
      type: String,
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
      height: 100% !important;
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
    color: var(--fg-secondary);
    max-width: 80%;
  }
  &--empty {
    width: 100%;
    text-align: center;
    height: 80vh;
    display: flex;
    align-items: center;
    justify-content: center;
    @include media("<=tablet") {
      height: 100%;
      text-align: center;
    }
  }
}
.annotation-progress {
  .--expanded & {
    display: none;
  }
}
.annotation-progress__title {
  display: none;
  .--expanded & {
    display: block;
  }
}
</style>
