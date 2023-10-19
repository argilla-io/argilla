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
      <p v-if="!isExpanded">Similar to:</p>
      <span
        class="similarity-reference__preview"
        v-if="!isExpanded"
        v-text="preview"
      />
    </div>
    <div class="similarity-reference__right">
      <BaseButton
        class="similarity-reference__button-close"
        @on-click="removeSimilaritySearch"
        ><svgicon name="close" height="14"
      /></BaseButton>
      <BaseButton
        class="similarity-reference__button-expand"
        @on-click="$emit(isExpanded ? 'minimize' : 'expand')"
        ><svgicon :name="isExpanded ? 'minimize-arrows' : 'expand-arrows'"
      /></BaseButton>
    </div>
  </div>
</template>
<script>
import "assets/icons/expand-arrows";
import "assets/icons/chevron-down";
export default {
  props: {
    preview: {
      type: String,
      required: true,
    },
    isExpanded: {
      type: Boolean,
      default: true,
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
    expand() {
      this.$emit("expand");
    },
    minimize() {
      this.$emit("minimize");
    },
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
$color-bg-preview: #fff3e9;
$color-border-preview: #ffc28f;
.similarity-reference {
  display: flex;
  align-items: center;
  gap: $base-space * 2;
  padding: calc($base-space / 2);
  justify-content: space-between;
  border-radius: $border-radius-m;
  @include font-size(12px);
  color: $black-54;
  transition: background 0.3s ease-in-out;
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
  &__button-expand,
  &__button-close {
    padding: 0;
    color: $black-54;
    &:hover {
      color: $black-87;
    }
  }
  &__button-close {
    opacity: 0;
    pointer-events: none;
  }
  &__preview {
    flex: 1;
    background: $color-bg-preview;
    padding: 0 $base-space;
    border: 1px solid $color-border-preview;
    border-radius: $border-radius;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  :deep(.dropdown__header) {
    background: none;
    cursor: pointer;
  }
  :deep(.dropdown__content) {
    left: -$base-space;
    right: auto;
  }
  &:hover {
    transition: background 0.3s ease-in-out;
    background: $black-4;
    .similarity-reference__button-close {
      opacity: 1;
      pointer-events: all;
    }
  }
  p {
    margin: 0;
    white-space: nowrap;
  }
}
</style>
