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
      <span v-if="!isExpanded" class="similarity-reference__preview">
        <span
          v-for="text in preview"
          :key="text"
          class="similarity-reference__preview__text"
          >{{ text }}</span
        >
        <BaseButton
          class="similarity-reference__preview__button-close"
          @on-click="removeSimilaritySearch"
          ><svgicon name="close" height="8"
        /></BaseButton>
      </span>
    </div>
    <div class="similarity-reference__right">
      <BaseButton
        v-if="isExpanded"
        class="similarity-reference__button-close"
        @on-click="removeSimilaritySearch"
        ><svgicon name="close" height="12"
      /></BaseButton>
      <BaseButton
        :title="isExpanded ? $t('minimize') : $t('expand')"
        class="similarity-reference__button-expand"
        @on-click="$emit(isExpanded ? 'minimize' : 'expand')"
        ><svgicon
          height="12"
          :name="isExpanded ? 'minimize-arrows' : 'expand-arrows'"
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
      type: Array,
      required: true,
    },
    isExpanded: {
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
$color-bg-preview: #ffd1ab;
.similarity-reference {
  display: flex;
  align-items: center;
  gap: $base-space;
  padding: calc($base-space / 2);
  justify-content: space-between;
  border-radius: $border-radius-m;
  color: $black-54;
  @include font-size(13px);
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
    display: flex;
    flex: 1;
    background: $color-bg-preview;
    padding: 0 $base-space;
    border-radius: $border-radius-l;
    min-width: 0;
    @include font-size(12px);
    &__text {
      flex: 1;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    &__button-close {
      padding: 0;
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
  &:hover {
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
