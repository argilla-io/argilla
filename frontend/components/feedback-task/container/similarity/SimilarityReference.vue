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
          ><svgicon name="close" height="10"
        /></BaseButton>
      </span>
    </div>
    <div class="similarity-reference__right">
      <BaseButton
        class="similarity-reference__button-icon"
        :title="visibleReferenceRecord ? $t('minimize') : $t('expand')"
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
  justify-content: space-between;
  max-width: min(600px, 100%);
  margin-right: auto;
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
    background: lighten($similarity-color, 25%);
    border: 1px solid lighten($similarity-color, 10%);
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
      color: $similarity-color;
    }
    &__button-close {
      padding: 0;
      color: $similarity-color;
      &:hover {
        color: darken($similarity-color, 15%);
      }
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
