<template>
  <span class="bulk__container">
    <LoadLine v-if="isSubmitting || isDraftSaving || isDiscarding" />
    <VerticalResizable
      class="wrapper"
      :id="`${recordCriteria.datasetId}-r-v-rz`"
    >
      <template #left>
        <HorizontalResizable
          :id="`${recordCriteria.datasetId}-r-h-rz`"
          class="wrapper__left"
          collapsable
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
                <div class="wrapper__records__header--left">
                  <BaseCheckbox
                    :data-title="
                      !selectedRecords.length
                        ? $t('bulkAnnotation.select_to_annotate')
                        : null
                    "
                    v-if="records.hasRecordsToAnnotate"
                    :decoration-circle="true"
                    class="wrapper__records__header__checkbox"
                    :value="isSelectedAll"
                    @input="toggleAllRecords"
                  />
                  <span
                    class="wrapper__records__header__selection-text"
                    v-if="selectedRecords.length && !affectAllRecords"
                    v-text="
                      $tc(
                        'bulkAnnotation.recordsSelected',
                        selectedRecords.length
                      )
                    "
                  />

                  <div
                    v-if="isAffectAllRecordsAllowed"
                    class="bulk-by-criteria"
                  >
                    <BaseButton
                      v-if="!affectAllRecords"
                      class="bulk-by-criteria__button primary text small"
                      @on-click="affectAllRecords = true"
                      >{{
                        $t("bulkAnnotation.selectAllResults", {
                          total: records.total,
                        })
                      }}</BaseButton
                    >
                    <template v-else>
                      <span class="wrapper__records__header__selection-text">{{
                        $t("bulkAnnotation.haveSelectedRecords", {
                          total: records.total,
                        })
                      }}</span>
                      <BaseButton
                        class="bulk-by-criteria__button primary text small"
                        @on-click="resetAffectAllRecords"
                        >{{ $t("button.cancel") }}</BaseButton
                      >
                    </template>
                  </div>
                </div>
                <RecordsViewConfig
                  v-if="records.hasRecordsToAnnotate"
                  v-model="recordHeight"
                />
                <PaginationFeedbackTask :recordCriteria="recordCriteria" />
              </div>
              <div v-if="recordsMessage" class="wrapper--empty">
                <p class="wrapper__text --heading3" v-html="recordsMessage" />
              </div>
              <div ref="bulkScrollableArea" class="bulk__records snap" v-else>
                <Record
                  class="snap-child"
                  :class="{
                    'record__wrapper--fixed-height':
                      recordHeight === 'fixedHeight',
                  }"
                  v-for="(record, i) in recordsOnPage"
                  :key="`${recordCriteria.committed.page.client.page}_${record.id}_${i}`"
                  :datasetVectors="datasetVectors"
                  :recordCriteria="recordCriteria"
                  :record="record"
                  :selectedRecords="selectedRecords"
                  @on-select-record="onSelectRecord"
                />
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
          collapsable
        >
          <template #up>
            <QuestionsForm
              v-if="!!record"
              :key="`${recordCriteria.committed.page.client.page}_${record.id}_questions`"
              class="wrapper__form"
              :class="statusClass"
              :datasetId="recordCriteria.datasetId"
              :record="record"
              :is-bulk-mode="true"
              :show-discard-button="recordsOnPage.some((r) => !r.isDiscarded)"
              :is-submitting="isSubmitting"
              :is-discarding="isDiscarding"
              :is-draft-saving="isDraftSaving"
              :is-submit-disabled="!hasSelectedAtLeastOneRecord"
              :is-discard-disabled="!hasSelectedAtLeastOneRecord"
              :is-draft-save-disabled="!hasSelectedAtLeastOneRecord"
              :submit-tooltip="bulkActionsTooltip"
              :discard-tooltip="bulkActionsTooltip"
              :draft-saving-tooltip="bulkActionsTooltip"
              :progress="progress"
              @on-submit-responses="onClickSubmit"
              @on-discard-responses="onClickDiscard"
              @on-save-draft="onClickSaveDraft"
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
    <BaseModal
      class="conformation-modal"
      :modal-custom="true"
      :prevent-body-scroll="true"
      modal-class="modal-secondary"
      :modal-title="$t('bulkAnnotation.actionConfirmation')"
      :modal-visible="visibleConfirmationModal"
      @close-modal="cancelAction"
    >
      <p
        v-text="
          $t('bulkAnnotation.actionConfirmationText', { total: records.total })
        "
      />
      <div class="modal-buttons">
        <BaseButton class="primary outline" @on-click="cancelAction">
          {{ $t("button.cancel") }}
        </BaseButton>
        <BaseButton class="primary" @on-click="confirmAction">
          {{ $t("button.continue") }}
        </BaseButton>
      </div>
    </BaseModal>
  </span>
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
      selectedRecords: [],
      recordHeight: "defaultHeight",
      visibleConfirmationModal: false,
      allowedAction: null,
      expandedGuidelines: false,
    };
  },
  computed: {
    recordsOnPage() {
      return this.records.getRecordsOn(this.recordCriteria.committed.page);
    },
    numberOfSelectedRecords() {
      if (this.affectAllRecords) return this.records.total;

      return this.selectedRecords.length;
    },
    hasSelectedAtLeastOneRecord() {
      return this.numberOfSelectedRecords > 0;
    },
    bulkActionsTooltip() {
      if (!this.hasSelectedAtLeastOneRecord)
        return this.$t("bulkAnnotation.to_annotate_record_bulk_required");

      return this.$tc(
        "bulkAnnotation.recordsSelected",
        this.numberOfSelectedRecords
      );
    },
    isSelectedAll() {
      return this.selectedRecords.length === this.recordsOnPage.length;
    },
    isAffectAllRecordsAllowed() {
      return (
        this.isSelectedAll &&
        this.checkIfSomeFilterIsActive(this.recordCriteria) &&
        this.records.total > this.recordsOnPage.length &&
        this.records.total <= 1000
      );
    },
    shouldShowModalToConfirm() {
      return this.affectAllRecords && this.numberOfSelectedRecords > 100;
    },
    spansQuestionsWithSelectedEntities() {
      return this.record.questions
        .filter((q) => q.isSpanType)
        .filter((s) => s.answer.options.some((e) => e.isSelected));
    },
  },
  methods: {
    onSelectRecord(isSelected, record) {
      if (isSelected) {
        if (!this.selectedRecords.some((r) => r.id === record.id))
          return this.selectedRecords.push(record);

        return;
      }

      this.selectedRecords = this.selectedRecords.filter(
        (r) => r.id !== record.id
      );
    },
    showConfirmationModal(action) {
      this.visibleConfirmationModal = true;
      this.allowedAction = action;
    },
    cancelAction() {
      this.visibleConfirmationModal = false;
      this.allowedAction = null;
    },
    async confirmAction() {
      this.visibleConfirmationModal = false;
      switch (this.allowedAction) {
        case "submit":
          await this.onSubmit();
          break;
        case "saveDraft":
          await this.onSaveDraft();
          break;
        case "discard":
          await this.onDiscard();
          break;
      }
      this.allowedAction = null;
    },
    onClickSubmit() {
      if (this.shouldShowModalToConfirm) {
        this.showConfirmationModal("submit");
      } else {
        this.onSubmit();
      }
    },
    onClickSaveDraft() {
      if (this.shouldShowModalToConfirm) {
        this.showConfirmationModal("saveDraft");
      } else {
        this.onSaveDraft();
      }
    },
    onClickDiscard() {
      if (this.shouldShowModalToConfirm) {
        this.showConfirmationModal("discard");
      } else {
        this.onDiscard();
      }
    },
    async onSubmit() {
      const allSuccessful = await this.submit(
        this.recordCriteria,
        this.record,
        this.selectedRecords
      );

      if (allSuccessful) this.selectedRecords = [];
    },
    async onDiscard() {
      const allSuccessful = await this.discard(
        this.recordCriteria,
        this.record,
        this.selectedRecords
      );

      if (allSuccessful) this.selectedRecords = [];
    },
    async onSaveDraft() {
      const allSuccessful = await this.saveAsDraft(
        this.recordCriteria,
        this.record,
        this.selectedRecords
      );

      if (allSuccessful) this.selectedRecords = [];
    },
    toggleAllRecords() {
      if (this.isSelectedAll) {
        this.selectedRecords = [];
      } else {
        this.selectedRecords = [...this.recordsOnPage];
      }
    },
    resetAffectAllRecords() {
      this.affectAllRecords = false;
      this.selectedRecords = [];
    },
    resetScroll() {
      if (!this.$refs.bulkScrollableArea) return;
      this.$refs.bulkScrollableArea.scrollTop = 0;
    },
  },
  watch: {
    spansQuestionsWithSelectedEntities: {
      deep: true,
      handler() {
        const spanQuestions = this.recordsOnPage
          .flatMap((r) => r.questions)
          .filter((q) => q.isSpanType);

        this.spansQuestionsWithSelectedEntities.forEach((q) => {
          spanQuestions.forEach((question) => {
            if (question.id === q.id) {
              question.answer.options.forEach((option) => {
                option.isSelected = q.answer.options.some(
                  (o) => o.isSelected && o.id === option.id
                );
              });
            }
          });
        });
      },
    },
    "recordCriteria.status"() {
      this.recordCriteria.page.focusMode();
    },
    "recordCriteria.committed.page"() {
      this.selectedRecords = [];
      this.resetScroll();
    },
    "recordCriteria.page.client.many"() {
      this.recordCriteria.page.goToFirst();

      this.$root.$emit("on-change-record-criteria-filter", this.recordCriteria);
    },
    isSelectedAll(value) {
      if (!value) {
        this.affectAllRecords = false;
      }
    },
  },
  setup(props) {
    return useBulkAnnotationViewModel(props);
  },
};
</script>

<style lang="scss" scoped>
.snap {
  scroll-snap-type: y mandatory;
}
.snap-child {
  scroll-snap-align: start;
}
.wrapper {
  position: relative;
  display: flex;
  flex-wrap: wrap;
  height: 100%;
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
      :deep(.resizable-h__down) {
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
    padding: $base-space * 2 $base-space * 2 0 $base-space * 2;
    &__header {
      display: flex;
      justify-content: flex-end;
      align-items: center;
      gap: $base-space;
      padding: 0 0 0 $base-space * 2;
      &__selection-text {
        user-select: none;
        color: var(--fg-secondary);
        @include font-size(13px);
      }
      &__checkbox {
        :deep(.checkbox__container) {
          border-color: var(--fg-secondary);
        }
      }
      &--left {
        display: flex;
        align-items: center;
        gap: $base-space * 2;
        margin-left: 0;
        margin-right: auto;
      }
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
.bulk {
  &__container {
    display: flex;
    flex-direction: column;
    height: 100%;
    min-height: 0;
  }
  &__records {
    position: relative;
    display: flex;
    flex-direction: column;
    padding-bottom: $base-space * 2;
    gap: $base-space;
    height: 100%;
    overflow: auto;
    @extend %hide-scrollbar;
    .record__wrapper {
      min-height: auto;
      height: auto;
      flex: 0;
      &--fixed-height {
        max-height: 80%;
        height: 100%;
      }
    }
  }
}

.bulk-by-criteria {
  display: flex;
  align-items: center;
  gap: $base-space * 2;
  &__button.button {
    padding: 6px;
    border-radius: $border-radius;
    &:hover {
      background: #edf0fa;
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
[data-title] {
  @include tooltip-mini("right", 12px);
}
</style>
