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
        <RecordFields
          :record="record"
          :fields="record.fields"
          :recordCriteria="recordCriteria"
        />
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
  position: relative;
  display: flex;
  flex-direction: column;
  min-height: 0;
  background: palette(white);
  border: 1px solid $black-6;
  border-radius: $border-radius-m;
  &:has(.dropdown__content),
  &:has(.checkbox.checked) {
    border-color: $black-20;
  }
  &__wrapper {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: $base-space;
    min-width: 0;
    height: 100%;
    min-height: 0;
    @include media("<=tablet") {
      height: auto;
    }
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
    .record--focus & {
      overflow-y: auto;
      overflow-x: hidden;
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
