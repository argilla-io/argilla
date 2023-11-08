<template>
  <div class="fields">
    <SimilarityRecordReference
      v-if="recordCriteria.isFilteredBySimilarity && !!records.reference"
      :fields="records.reference.fields"
      :recordCriteria="recordCriteria"
      :availableVectors="datasetVectors"
    />
    <p v-if="shouldShowTotalRecords" class="total-records">
      {{ totalRecordsInfo }}
    </p>
    <RecordFields :fields="record.fields" :key="`${record.id}_fields`">
      <div class="fields__header">
        <div class="fields__header--left">
          <StatusTag class="fields__status" :recordStatus="record.status" />
        </div>
        <div class="fields__header--right">
          <BaseHalfCircleProgress
            v-if="
              recordCriteria.isFilteredBySimilarity && record.score.percentage
            "
            class="similarity__progress"
            :value="record.score.percentage"
            :data-title="$t('similarityScore')"
          >
            <svgicon name="similarity" width="30" height="30" />
          </BaseHalfCircleProgress>
          <SimilarityFilter
            v-if="datasetVectors?.length"
            :availableVectors="datasetVectors"
            :recordCriteria="recordCriteria"
            :recordId="record.id"
          />
        </div></div
    ></RecordFields>
  </div>
</template>
<script>
import "assets/icons/similarity";
export default {
  props: {
    record: {
      type: Object,
      required: true,
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
  },
  data: () => {
    return {
      totalRecords: null,
    };
  },
  computed: {
    totalRecordsInfo() {
      if (!this.totalRecords || this.totalRecords === 0) return null;

      return this.totalRecords === 1
        ? `${this.totalRecords} record`
        : `${this.totalRecords} records`;
    },
    shouldShowTotalRecords() {
      return (
        this.recordCriteria.isFilteredByText ||
        this.recordCriteria.isFilteredByMetadata
      );
    },
  },
  mounted() {
    this.$root.$on("on-changed-total-records", (totalRecords) => {
      this.totalRecords = totalRecords;
    });
  },
  destroyed() {
    this.$root.$off("on-changed-total-records");
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

  &__header {
    $this: &;
    border-radius: $border-radius-m;
    background: palette(white);
    display: flex;
    justify-content: space-between;
    #{$this}__header {
      padding: $base-space $base-space * 2;
    }

    &--left {
      display: flex;
      align-items: center;
      gap: $base-space;
    }
    &--right {
      display: flex;
      align-items: center;
      gap: $base-space;
    }
  }
  &__status {
    display: inline-flex;
    margin-right: auto;
  }
}

.total-records {
  display: inline-flex;
  justify-content: end;
  flex-shrink: 0;
  margin: 0;
  @include font-size(13px);
  color: $black-37;
}

.similarity__progress {
  color: $similarity-color;
  &[data-title] {
    position: relative;
    @extend %has-tooltip--right;
  }
}
</style>
