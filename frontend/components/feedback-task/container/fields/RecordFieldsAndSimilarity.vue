<template>
  <div class="fields">
    <SimilarityRecordReference
      :fields="record.fields"
      :recordCriteria="recordCriteria"
    />
    <RecordFields :fields="record.fields">
      <div class="fields__header">
        <div class="fields__header--left">
          <StatusTag class="fields__status" :recordStatus="record.status" />
          <span
            class="similarity-icon"
            :data-title="`Similarity Score ${similarityScore}`"
          >
            <svgicon name="similarity" width="30" height="30" />
          </span>
        </div>
        <SimilarityFilter
          v-if="datasetVectors?.length"
          :available-vectors="datasetVectors"
          :recordCriteria="recordCriteria"
          :recordId="record.id"
        /></div
    ></RecordFields>
  </div>
</template>
<script>
import { useRecordFieldsAndSimilarityViewModel } from "./useRecordFieldsAndSimilarityViewModel";
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
  },
  data() {
    return {
      similarityScore: 80,
    };
  },
  setup(props) {
    return useRecordFieldsAndSimilarityViewModel(props);
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
  }
  &__status {
    display: inline-flex;
    margin-right: auto;
  }
}

.similarity-icon {
  color: darken($similarity-color, 20%);
  &[data-title] {
    position: relative;
    @extend %has-tooltip--right;
  }
}
</style>
