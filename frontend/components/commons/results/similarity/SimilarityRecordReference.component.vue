<template>
  <results-record
    class="record--reference"
    :dataset="dataset"
    :item="referenceRecord"
    :isReferenceRecord="!!referenceRecord"
    @search-records="searchRecords"
    @show-metadata="onShowMetadata"
  >
    <slot :record="referenceRecord" />
  </results-record>
</template>
<script>
export default {
  props: {
    dataset: {
      type: Object,
      required: true,
    },
    referenceRecord: {
      type: Object,
    },
  },
  methods: {
    onShowMetadata(query) {
      this.$emit("show-metadata", query);
    },
    searchRecords(query) {
      this.$emit("search-records", query);
    },
  },
};
</script>

<style lang="scss" scoped>
.record--reference {
  :deep(.list__item--annotation-mode) {
    border: 1px solid $record-reference-border-color;
    background: $record-reference-background-color;
  }
  :deep(.origins) {
    pointer-events: none;
  }
}
</style>
