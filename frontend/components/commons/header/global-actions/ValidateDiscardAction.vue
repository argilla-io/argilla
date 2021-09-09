<template>
  <div class="validate-discard-actions" :class="[selectedRecords.length ? '' : 'validate-discard-actions--disabled']">
    <ReCheckbox v-model="allSelected" class="list__item__checkbox"></ReCheckbox>
    <slot name="first" :selectedRecords="selectedRecords" />
    <ReButton class="validate-discard-actions__button" @click="onValidate"
      >Validate</ReButton
    >
    <ReButton class="validate-discard-actions__button" @click="onDiscard"
      >Discard</ReButton
    >
    <slot name="last" :selectedRecords="selectedRecords" />
    <p v-if="selectedRecords.length" class="validate-discard-actions__text">
      Actions will apply to the
      <span>{{ selectedRecords.length }} records</span> selected
    </p>
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
    position: {
      type: String,
      default: "before",
    },
  },
  data: () => ({
    allSelected: false,
  }),
  computed: {
    visibleRecords() {
      return this.dataset.visibleRecords;
    },
    selectedRecords() {
      // Return selected records.
      return this.visibleRecords.filter((record) => record.selected);
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
    }),
    onDiscard() {
      this.$emit("discard-records", this.selectedRecords);
    },
    async onValidate() {
      this.$emit("validate-records", this.selectedRecords);
    },
  },
};
</script>
<style lang="scss" scoped>
.validate-discard-actions {
  display: flex;
  align-items: center;
  width: 100%;
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
      max-height: 33px;
      background: $lighter-color;
      border-width: 1px;
      color: $font-secondary;
      font-weight: bold;
    }
  }
  &__button {
    border-radius: 0;
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
    margin: 0;
    color: $darker-color;
    font-weight: normal;
    span {
      font-weight: bold;
      color: $primary-color;
    }
  }
  &--disabled {
    .validate-discard-actions__button,
    .validate-discard-actions__select {
      pointer-events: none;
      opacity: 0.5;
    }
  }
}
</style>
