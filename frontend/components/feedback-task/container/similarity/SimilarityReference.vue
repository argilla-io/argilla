<template>
  <div class="similarity-reference">
    <div class="similarity-reference__left">
      <SimilarityFilterLimit
        class="similarity-reference__dropdown"
        v-model="recordCriteria.similaritySearch.limit"
      />
      <SimilarityFilterOrder
        class="similarity-reference__dropdown"
        v-model="recordCriteria.similaritySearch.order"
      />
      <p>Similar to</p>
      <span class="similarity-reference__preview">
        <span
          v-for="text in preview"
          :title="text"
          :key="text"
          class="similarity-reference__preview__text"
          >{{ text }}</span
        >
        <BaseButton
          class="similarity-reference__preview__button-close"
          @on-click="removeSimilaritySearch"
          ><svgicon name="close" height="14"
        /></BaseButton>
      </span>
    </div>
    <div class="similarity-reference__right">
      <BaseButton
        class="similarity-reference__button-icon"
        @on-click="
          $emit(
            visibleReferenceRecord
              ? 'hide-reference-record'
              : 'show-reference-record'
          )
        "
        ><svgicon
          height="16"
          :name="visibleReferenceRecord ? 'minimize-arrows' : 'expand-arrows'"
      /></BaseButton>
    </div>
  </div>
</template>
<script>
import "assets/icons/expand-arrows";
import "assets/icons/minimize-arrows";
export default {
  props: {
    preview: {
      type: Array,
      required: true,
    },
    visibleReferenceRecord: {
      type: Boolean,
      default: false,
    },
    recordCriteria: {
      type: Object,
      required: true,
    },
  },
  watch: {
    "recordCriteria.similaritySearch.order"() {
      this.filterChanged();
    },
    "recordCriteria.similaritySearch.limit"() {
      this.filterChanged();
    },
  },
  methods: {
    removeSimilaritySearch() {
      this.recordCriteria.similaritySearch.reset();

      this.filterChanged();
    },
    filterChanged() {
      if (!this.recordCriteria.hasChanges) return;
      this.recordCriteria.page = 1;

      this.$root.$emit("on-change-record-criteria-filter", this.recordCriteria);
    },
  },
};
</script>
<style lang="scss" scoped>
.similarity-reference {
  display: flex;
  align-items: center;
  gap: $base-space;
  padding: $base-space 12px;
  max-width: 600px;
  border-radius: $border-radius;
  color: $black-54;
  background: $black-4;
  @include font-size(13px);
  transition: background 0.3s ease-in-out;
  &:hover {
    background: $black-6;
  }
  &__left {
    display: flex;
    gap: $base-space;
    min-width: 0;
  }
  &__right {
    display: flex;
    gap: $base-space;
    flex-shrink: 0;
    min-width: 0;
  }
  &__button-icon {
    padding: 0;
    color: $black-54;
  }
  &__preview {
    display: flex;
    flex: 1;
    align-items: center;
    gap: $base-space;
    min-width: 0;
    background: $similarity-color;
    border: 1px solid darken($similarity-color, 15%);
    padding: 2px $base-space;
    border-radius: $border-radius-l;
    @include font-size(12px);
    &__text {
      flex: 1;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      font-weight: 500;
      line-height: 1rem;
      color: darken($similarity-color, 55%);
    }
    &__button-close {
      padding: 0;
      color: darken($similarity-color, 55%);
    }
  }
  :deep(.dropdown__header) {
    background: none;
    cursor: pointer;
  }
  :deep(.dropdown__content) {
    left: -$base-space;
    right: auto;
  }
  p {
    margin: 0;
    white-space: nowrap;
    font-weight: 500;
  }
}
</style>
