<template>
  <div class="fields__header">
    <div class="fields__header--left">
      <BaseCheckbox
        v-if="selectableRecord"
        class="fields__checkbox"
        @input="onSelectedRecord"
      />
    </div>
    <div class="fields__header--right">
      <RecordStatus class="fields__status" :recordStatus="record.status" />
      <SimilarityScorePercentage
        v-if="recordCriteria.isFilteringBySimilarity && record.score.percentage"
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
    </div>
  </div>
</template>

<script>
export default {
  props: {
    selectableRecord: {
      type: Boolean,
      default: false,
    },
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
      default: () => [],
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
