<template>
  <div class="fields">
    <SimilarityRecordReference
      v-show="recordCriteria.isFilteringBySimilarity"
      v-if="!!records.reference"
      :fields="records.reference.fields"
      :recordCriteria="recordCriteria"
      :availableVectors="datasetVectors"
    />
    <RecordFields
      v-if="!!record"
      :key="`${record.id}_fields`"
      :fields="record.fields"
    >
      <template v-if="fixedHeader" v-slot:fixed-header>
        <RecordFieldsHeader
          class="fields__fixed-header"
          :selectableRecord="selectableRecord"
          :selected-record-id="selectedRecordId"
          :record="record"
          :recordCriteria="recordCriteria"
          :datasetVectors="datasetVectors"
          @input="onInput"
        />
      </template>
      <template v-else v-slot:content-header>
        <RecordFieldsHeader
          :record="record"
          :recordCriteria="recordCriteria"
          :datasetVectors="datasetVectors"
        />
      </template>
    </RecordFields>
  </div>
</template>
<script>
import "assets/icons/similarity";
export default {
  props: {
    record: {
      type: Object,
    },
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
    selectedRecordId: {
      type: [String, null],
    },
    selectableRecord: {
      type: Boolean,
      default: false,
    },
    fixedHeader: {
      type: Boolean,
      default: false,
    },
  },
  model: {
    prop: "selectedRecordId",
    event: "input",
  },
  methods: {
    onInput(isSelected) {
      const input = isSelected ? this.record.id : null;
      this.$emit("input", input);
    },
  },
};
</script>
<style lang="scss" scoped>
.fields {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: $base-space;
  min-width: 0;
  height: 100%;
  min-height: 0;
  &__fixed-header {
    padding: $base-space * 2;
    & + :deep(.record__content) {
      padding-top: 0;
    }
  }
}
</style>
