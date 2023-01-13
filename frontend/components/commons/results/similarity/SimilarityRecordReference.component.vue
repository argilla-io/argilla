<template>
  <results-record
    class="record--reference"
    :datasetId="datasetId"
    :datasetTask="datasetTask"
    :record="referenceRecord"
    :isReferenceRecord="!!referenceRecord"
    @search-records="searchRecords"
    @show-record-info-modal="onShowRecordInfoModal"
  />
</template>

<script>
export default {
  props: {
    datasetId: {
      type: Array,
      required: true,
    },
    datasetTask: {
      type: String,
      required: true,
    },
    referenceRecord: {
      type: Object,
    },
  },
  methods: {
    searchRecords(query) {
      this.$emit("search-records", query);
    },
    onShowRecordInfoModal(record) {
      this.$emit("show-record-info-modal", record);
    },
  },
};
</script>

<style lang="scss" scoped>
.record--reference {
  :deep(.list__item--annotation-mode),
  :deep(.list__item) {
    border: 1px solid $record-reference-border-color;
    background: $record-reference-background-color;
  }
  :deep(.origins) {
    pointer-events: none;
  }
  :deep(.highlight) {
    pointer-events: all;
  }
  :deep(.remove-button) {
    display: none;
  }
}
</style>
