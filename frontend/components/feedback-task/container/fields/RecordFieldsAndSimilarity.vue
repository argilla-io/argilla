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
      <div class="fields__header">
        <div class="fields__header--left"></div>
        <div class="fields__header--right">
          <SimilarityScorePercentage
            v-if="
              recordCriteria.isFilteringBySimilarity && record.score.percentage
            "
            class="similarity__progress"
            :value="record.score.percentage"
            :data-title="$t('similarityScore')"
          >
          </SimilarityScorePercentage>
          <SimilarityFilter
            v-if="datasetVectors?.length"
            :availableVectors="datasetVectors"
            :recordCriteria="recordCriteria"
            :recordId="record.id"
          />
          <RecordStatus :recordStatus="record.status" />
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

.similarity__progress {
  &[data-title] {
    position: relative;
    @extend %has-tooltip--left;
  }
}
</style>
