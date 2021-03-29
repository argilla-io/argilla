<template>
  <div
    :class="[
      'global-actions',
      selectedRecords.length ? '' : 'global-actions--disabled',
    ]"
  >
    <div class="global-actions__container">
      <!-- TODO use v-model for ReCheckbox with boolean values -->
      <ReCheckbox
        v-model="allSelected"
        class="list__item__checkbox"
      ></ReCheckbox>
      <FeedbackDropdownAll
        v-if="isTextClassification"
        :multi-label="isMultiLabelRecord"
        class="global-actions__select"
        :options="options"
        @addNewLabel="onAddNewLabel"
        @selected="onSelectAnnotation($event)"
      ></FeedbackDropdownAll>
      <ReButton class="global-actions__button" @click="onValidate"
        >Validate</ReButton
      >
      <ReButton class="global-actions__button" @click="onDiscard"
        >Discard</ReButton
      >
      <p v-if="selectedRecords.length" class="global-actions__text">
        Actions will apply to the
        <span>{{ selectedRecords.length }} records</span> selected
      </p>
      <ReButton
        class="button-clear button-action global-actions__export"
        @click="onOpenExportModal()"
      >
        <svgicon name="export" width="14" height="14" color="#F48E5F" />Export
        annotations
      </ReButton>
    </div>
    <ReModal
      :modal-custom="true"
      :prevent-body-scroll="true"
      modal-class="modal-primary"
      :modal-visible="openExportModal"
      modal-position="modal-center"
      @close-modal="closeModal()"
    >
      <p class="modal__title">Confirm export of annotations</p>
      <p class="modal__text">
        You are about to export {{ annotationsSum }} annotations. You will find
        the file on the server once the action is completed.
      </p>
      <div class="modal-buttons">
        <ReButton
          class="button-tertiary--small button-tertiary--outline"
          @click="closeModal()"
        >
          Cancel
        </ReButton>
        <ReButton
          class="button-secondary--small"
          @click="onExportAnnotations()"
        >
          Confirm export
        </ReButton>
      </div>
    </ReModal>
  </div>
</template>
<script>
import { mapActions } from "vuex";
import "assets/icons/export";

export default {
  props: {
    dataset: {
      type: Object,
      required: true,
    },
  },
  data: () => ({
    allSelected: false,
    openExportModal: false,
  }),
  computed: {
    selectedRecords() {
      return this.visibleRecords.filter((record) => record.selected);
    },
    isTokenClassification() {
      return this.dataset.task === "TokenClassification";
    },
    isTextClassification() {
      return this.dataset.task === "TextClassification";
    },
    isMultiLabelRecord() {
      return this.selectedRecords.some((record) => record.multi_label);
    },
    options() {
      const record = this.dataset.results.records[0];
      const labels = record.prediction ? record.prediction.labels.map((label) => label.class) : [];
      return this.isTextClassification ? labels : [];
    },
    visibleRecords() {
      return this.dataset.visibleRecords;
    },
    annotationsSum() {
      return this.dataset.results.aggregations.status.Validated;
    },
    _allSelected() {
      return this.allSelected;
    },
  },
  watch: {
    visibleRecords(newValue) {
      if (!newValue.every((record) => record.selected)) {
        this.allSelected = false;
      }
    },
    allSelected(allSelected) {
      if (
        allSelected ||
        this.visibleRecords.every((record) => record.selected)
      ) {
        this.updateRecords({
          dataset: this.dataset,
          records: this.visibleRecords.map((record) => {
            return { ...record, selected: this.allSelected };
          }),
        });
      }
    },
  },
  methods: {
    ...mapActions({
      updateRecords: "entities/datasets/updateRecords",
      discard: "entities/datasets/discardAnnotations",
      validate: "entities/datasets/validateAnnotations",
      exportAnnotations: "entities/datasets/exportAnnotations",
    }),

    async onSelectAnnotation(labels) {
      const records = this.selectedRecords.map((record) => {
        const appliedLabels = record.annotation
          ? [...record.annotation.labels]
          : [];

        const filterAppliedLabels = labels.filter(
          (l) => appliedLabels.map((label) => label.class).indexOf(l) === -1
        );

        let newLabels = this.isMultiLabelRecord ? filterAppliedLabels : labels;
        newLabels = newLabels.map((label) => ({
          class: label,
          confidence: 1.0,
        }));
        return {
          ...record,
          annotation: {
            agent: this.$auth.user,
            labels: this.isMultiLabelRecord
              ? [...appliedLabels, ...newLabels]
              : newLabels,
          },
        };
      });

      await this.validate({
        dataset: this.dataset,
        records: records,
      });
    },
    async onDiscard() {
      await this.discard({
        dataset: this.dataset,
        records: this.selectedRecords,
      });
    },
    async onValidate() {
      await this.validate({
        dataset: this.dataset,
        records: this.selectedRecords,
      });
    },
    async onAddNewLabel(newLabel) {
      this.dataset.$dispatch("setLabels", {
        dataset: this.dataset,
        labels: [...new Set([...this.dataset.labels, newLabel])],
      });
    },
    onOpenExportModal() {
      this.openExportModal = true;
    },
    closeModal() {
      this.openExportModal = false;
    },
    async onExportAnnotations() {
      this.openExportModal = false;
      this.exportAnnotations({ name: this.dataset.name });
    },
  },
};
</script>
<style lang="scss" scoped>
.global-actions {
  padding: 2em 1.2em 0 1.2em;
  display: flex;
  align-items: center;
  color: $font-medium-color;
  min-height: 0;
  font-weight: 600;
  .fixed-header & {
    margin-top: 0;
    padding-top: 0;
    background: $line-smooth-color;
    border: none;
    min-height: 70px;
  }
  @include media(">desktopLarge") {
    padding-left: 4em;
    padding-right: 4em;
  }
  .re-checkbox {
    position: relative;
    left: 0;
    top: 0;
    margin: 0 8px 0 0;
  }
  &__export {
    margin: auto 0 auto auto;
  }
  &__container {
    display: flex;
    align-items: center;
    width: 100%;
    @extend %container;
    padding-top: 0;
    padding-bottom: 0;
  }
  &__select {
    margin-left: 0.8em;
    ::v-deep .dropdown__header {
      border-radius: 5px;
      max-height: 33px;
      background: $lighter-color;
      border-width: 1px;
    }
  }
  &__button {
    border-radius: 5px;
    height: 33px;
    border: none;
    min-width: 80px;
    margin-left: 1em;
    margin-right: 1em;
    outline: none;
    font-weight: 600;
    color: $font-medium-color;
    background: $lighter-color;
    border: 1px solid $line-smooth-color;
    cursor: pointer;
    &:first-of-type {
      margin-right: 0;
    }
  }
  &__text {
    color: $darker-color;
    font-weight: normal;
  }
  &--disabled {
    .global-actions__button,
    .global-actions__select {
      pointer-events: none;
      opacity: 0.5;
    }
  }
}
.global-actions__text {
  margin: 0;
  span {
    font-weight: bold;
    color: $secondary-color;
  }
}
</style>
