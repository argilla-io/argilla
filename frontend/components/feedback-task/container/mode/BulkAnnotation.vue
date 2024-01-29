<template>
  <span>
    <LoadLine v-if="isSubmitting || isDraftSaving || isDiscarding" />
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
                $tc('bulkAnnotation.recordsSelected', selectedRecords.length)
              "
            />

            <div v-if="isAffectAllRecordsAllowed" class="bulk-by-criteria">
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
          <PaginationFeedbackTaskComponent :recordCriteria="recordCriteria" />
        </div>
        <div
          ref="bulkScrollableArea"
          class="bulk__records snap"
          v-if="records.hasRecordsToAnnotate"
        >
          <Record
            class="snap-child"
            :class="{
              'record__wrapper--fixed-height': recordHeight === 'fixedHeight',
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
        <div v-else class="wrapper--empty">
          <p class="wrapper__text --heading3" v-text="noRecordsMessage" />
        </div>
      </section>

      <QuestionsFormComponent
        v-if="!!record"
        :key="`${recordCriteria.committed.page.client.page}_${record.id}_questions`"
        class="wrapper__form"
        :class="statusClass"
        :datasetId="recordCriteria.datasetId"
        :record="record"
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
    </div>
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
        <BaseButton class="primary" @on-click="confirmateAction">
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
      recordHeight: "defaultHeight",
      visibleConfirmationModal: false,
      allowedAction: null,
    };
  },
  computed: {
    recordsOnPage() {
      return this.records.getRecordsOn(this.recordCriteria.committed.page);
    },
    numberOfSelectedRecords() {
      return this.selectedRecords.length;
    },
    hasSelectedAtLeastOneRecord() {
      return this.numberOfSelectedRecords > 0 || this.affectAllRecords;
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
        this.records.total <= this.bulkRecordsLimit
      );
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
    showConfirmationModal(action) {
      this.visibleConfirmationModal = true;
      this.allowedAction = action;
    },
    cancelAction() {
      this.visibleConfirmationModal = false;
      this.resetAffectAllRecords();
      this.allowedAction = null;
    },
    async confirmateAction() {
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
      if (this.affectAllRecords) {
        this.showConfirmationModal("submit");
      } else {
        this.onSubmit();
      }
    },
    onClickSaveDraft() {
      if (this.affectAllRecords) {
        this.showConfirmationModal("saveDraft");
      } else {
        this.onSaveDraft();
      }
    },
    onClickDiscard() {
      if (this.affectAllRecords) {
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
  setup() {
    return useBulkAnnotationViewModel();
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
    gap: $base-space * 2;
    height: 100%;
    min-width: 0;
    &__header {
      display: flex;
      justify-content: flex-end;
      align-items: center;
      gap: $base-space;
      padding: 0 0 0 $base-space * 2;
      &__selection-text {
        user-select: none;
        color: $black-54;
        @include font-size(13px);
      }
      &__checkbox {
        :deep(.checkbox__container) {
          border-color: $black-54;
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
    .record__wrapper {
      min-height: auto;
      height: auto;
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

[data-title] {
  @include tooltip-mini("right", 12px);
}
</style>
