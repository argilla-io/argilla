<template>
  <div :class="[selectedRecords.length ? '' : 'global-actions--disabled']">
    <ReCheckbox v-model="allSelected" class="list__item__checkbox"></ReCheckbox>
    <slot name="first" :selectedRecords="selectedRecords" />
    <ReButton class="global-actions__button" @click="onValidate"
      >Validate</ReButton
    >
    <ReButton class="global-actions__button" @click="onDiscard"
      >Discard</ReButton
    >
    <slot name="last" :selectedRecords="selectedRecords" />
    <p v-if="selectedRecords.length" class="global-actions__text">
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
.global-actions__text {
  margin: 0;
  span {
    font-weight: bold;
    color: $primary-color;
  }
}
</style>
