<template>
  <div class="record__wrapper" v-if="!!record" :key="`${record.id}_fields`">
    <div
      class="record"
      :class="Array.isArray(selectedRecords) ? 'record--bulk' : 'record--focus'"
    >
      <RecordFieldsHeader
        class="record__fixed-header"
        :record="record"
        :recordCriteria="recordCriteria"
        :datasetVectors="datasetVectors"
        :selectedRecords="selectedRecords"
        @on-select-record="onSelectedRecord"
      />
      <div class="record__content">
        <RecordFields :fields="record.fields" />
      </div>
    </div>
  </div>
</template>
<script>
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
    selectedRecords: {
      type: Array,
    },
  },
  computed: {
    searchValue() {
      return this.$route.query?._search ?? "";
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
.record {
  display: flex;
  flex-direction: column;
  min-height: 0;
  background: palette(white);
  border: 1px solid palette(grey, 600);
  border-radius: $border-radius-m;
  &--focus {
    overflow: auto;
  }
  &__wrapper {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: $base-space;
    min-width: 0;
    height: 100%;
    min-height: 0;
  }
  &__content {
    display: flex;
    flex-direction: column;
    gap: $base-space * 2;
    padding: $base-space * 2;
    border-radius: $border-radius-m;
    .record--bulk & {
      height: 100%;
      overflow: auto;
    }
  }
  &__fixed-header {
    padding: $base-space * 2;
    & + :deep(.record__content) {
      padding-top: 0;
    }
  }
}
</style>
