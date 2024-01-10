<template>
  <div class="fields__header">
    <div class="fields__header--left">
      <BaseCheckbox
        v-if="Array.isArray(selectedRecords)"
        :decoration-circle="animateCheckboxes"
        class="fields__checkbox"
        :value="selectedRecords.includes(record)"
        @input="onSelectedRecord"
      />
    </div>
    <div class="fields__header--right">
      <SimilarityScorePercentage
        v-if="recordCriteria.isFilteringBySimilarity && record.score.percentage"
        class="similarity__progress"
        :value="record.score.percentage"
        :data-title="$t('similarityScore')"
      >
      </SimilarityScorePercentage>
      <SimilarityFilter
        v-if="datasetVectors.length"
        :availableVectors="datasetVectors"
        :recordCriteria="recordCriteria"
        :recordId="record.id"
      />
      <RecordStatus :recordStatus="record.status" />
    </div>
  </div>
</template>

<script>
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
      default: () => [],
    },
    selectedRecords: {
      type: Array,
    },
  },
  data() {
    return {
      animateCheckboxes: false,
    };
  },
  methods: {
    onSelectedRecord(isSelected) {
      this.$emit("on-select-record", isSelected, this.record);
    },
  },
  created() {
    this.$nuxt.$on("animate-checkboxes", () => {
      this.animateCheckboxes = true;
    });
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
  &__checkbox {
    &:not(.checked):hover {
      :deep(.checkbox__container) {
        border-color: $black-37;
      }
    }
    :deep(.checkbox__container) {
      border-color: $black-20;
    }
  }
}

.similarity__progress {
  &[data-title] {
    position: relative;
    @extend %has-tooltip--left;
  }
}
</style>
