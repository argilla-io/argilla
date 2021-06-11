<template>
  <div
    :class="[
      'container',
      selectedRecords.length ? '' : 'global-actions--disabled',
    ]"
  >   
    <div class="global-actions--exploration" v-if="!annotationEnabled">
      <ReButton class="button--refresh button-primary" @click="refresh()">
        <svgicon name="refresh" width="20" height="14" /> Refresh
      </ReButton>
    </div>   
    <div class="global-actions" v-else>
      <ReButton class="button--refresh button-primary" @click="refresh()">
        <svgicon name="refresh" width="20" height="14" /> Refresh
      </ReButton>
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
      <div class="new-label__container">
        <reButton
          v-if="!newLabelVisible"
          class="new-label__main-button button-secondary--outline"
          @click="newLabelVisible = true"
          ><svgicon name="plus" width="10" height="10" />Create new
          label</reButton
        >
        <div v-else class="new-label">
          <input
            v-model="newLabel"
            autofocus
            class="new-label__input"
            type="text"
            placeholder="New label"
            @keyup.enter="addNewLabel(newLabel)"
          />
          <svgicon
            class="new-label__close"
            name="cross"
            @click="closeNewLabelVisible()"
          />
          <reButton
            class="new-label__button button-primary--small"
            :disabled="!this.newLabel"
            @click="addNewLabel(newLabel)"
            >Create</reButton
          >
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import { mapActions } from "vuex";
import "assets/icons/export";
import "assets/icons/plus";
import "assets/icons/refresh";

export default {
  props: {
    dataset: {
      type: Object,
      required: true,
    },
    annotationEnabled: {
      type: Boolean,
      required: true,      
    }
  },
  data: () => ({
    allSelected: false,
    openExportModal: false,
    newLabel: undefined,
    newLabelVisible: false,
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
      let labels =
        record && record.prediction
          ? record.prediction.labels.map((label) => label.class)
          : [];
      labels = Array.from(new Set([...labels, ...this.dataset.labels]));
      return this.isTextClassification ? labels : [];
    },
    visibleRecords() {
      return this.dataset.visibleRecords;
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
      search: "entities/datasets/search",
    }),
    refresh() {
      this.search({
        dataset: this.dataset,
        query: this.dataset.query
      });
    },
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
    closeNewLabelVisible() {
      this.newLabel = undefined;
      this.newLabelVisible = false;
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
    async addNewLabel(newLabel) {
      if (!newLabel || !newLabel.trim()) {
        // If no label, nothing to do
        return;
      }
      if (this.isTextClassification) {
        this.dataset.$dispatch("setLabels", {
          dataset: this.dataset,
          labels: [...new Set([...this.dataset.labels, newLabel])],
        });
      } else if (this.isTokenClassification) {
        this.dataset.$dispatch("setEntities", {
          dataset: this.dataset,
          entities: [
            ...new Set([
              ...this.dataset.entities.map((ent) => ent.text),
              newLabel,
            ]),
          ],
        });
      }
      this.closeNewLabelVisible();
    },
  },
};
</script>
<style lang="scss" scoped>
.container {
  @extend %container;
  padding-top: 0;
  padding-bottom: 0;
}
.new-label {
  width: 180px;
  border-radius: 3px;
  border: 2px solid $primary-color;
  padding: 1em;
  position: absolute;
  top: -1em;
  background: $lighter-color;
  text-align: left;
  &__close {
    position: absolute;
    top: 1.2em;
    right: 1em;
    cursor: pointer;
    height: 12px;
    width: 12px;
    stroke: $font-secondary;
    stroke-width: 1;
  }
  &__input {
    border: 0;
    outline: none;
    padding-right: 2em;
    width: 100%;
  }
  &__button {
    margin-top: 2em;
    margin-bottom: 0 !important;
  }
  &__main-button {
    margin-bottom: 0 !important;
    margin-right: 0;
    margin-left: auto;
  }
  &__container {
    text-align: right;
    position: relative;
    margin-right: 0;
    margin-left: auto;
    width: 180px;
  }
}
.button--refresh {
  position: absolute !important;
  z-index: 2;
  top: -40px;
  right: 0;
  left: auto;
}
.global-actions {
  display: flex;
  align-items: center;
  width: 100%;
  text-align: left;
  padding: 1em 1.4em;
  background: $lighter-color;
  border-radius: 3px;
  position: relative;
  &--exploration {
    position: relative;
  }
  .fixed-header & {
    margin-top: 0;
    padding-top: 0;
    padding-bottom: 0;
    background: $bg;
    border: none;
    min-height: 70px;
  }
  @include media(">desktopLarge") {
    width: calc(100% - 294px);
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
  &__select {
    margin-left: 0.8em;
    ::v-deep .dropdown__header {
      border-radius: 5px;
      max-height: 33px;
      background: $lighter-color;
      border-width: 1px;
      color: $font-secondary;
      font-weight: bold;
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
    color: $font-secondary;
    background: $lighter-color;
    border: 1px solid $line-smooth-color;
    cursor: pointer;
    &:hover,
    &:focus {
      border-color: $primary-color;
    }
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
    color: $primary-color;
  }
}
</style>
