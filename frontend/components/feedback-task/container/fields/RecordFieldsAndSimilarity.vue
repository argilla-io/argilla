<template>
  <div class="fields">
    <SimilarityRecordReference
      v-show="recordCriteria.isFilteringBySimilarity"
      v-if="showRecordSimilar && !!records.reference"
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
          :record="record"
          :recordCriteria="recordCriteria"
          :datasetVectors="datasetVectors"
          :selectableRecord="selectableRecord"
          :selectedRecords="selectedRecords"
          @on-select-record="onSelectedRecord"
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
    selectableRecord: {
      type: Boolean,
      default: false,
    },
    selectedRecords: {
      type: Array,
      default: () => [],
    },
    fixedHeader: {
      type: Boolean,
      default: false,
    },
    showRecordSimilar: {
      type: Boolean,
      default: true,
    },
  },
  methods: {
    onSelectedRecord(isSelected) {
      this.$emit("on-select-record", isSelected, this.record);
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
