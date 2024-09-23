<template>
  <div
    class="similarity-reference"
    v-if="recordCriteria.isFilteringBySimilarity"
  >
    <div class="similarity-reference__left">
      <SimilarityFilterLimit
        class="similarity-reference__dropdown"
        v-model="recordCriteria.similaritySearch.limit"
      />
      <SimilarityFilterOrder
        class="similarity-reference__dropdown"
        v-model="recordCriteria.similaritySearch.order"
      />
      <p>{{ $t("similarity.similarTo") }}</p>
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

      <SimilarityFilterVector
        class="similarity-reference__dropdown"
        :vectors="availableVectors"
        v-model="recordCriteria.similaritySearch.vectorName"
      />
    </div>

    <div class="similarity-reference__right">
      <BaseButton
        :data-title="
          !visibleReferenceRecord
            ? $t('similarity.expand')
            : $t('similarity.collapse')
        "
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
    availableVectors: {
      type: Array,
      required: true,
    },
  },
  watch: {
    "recordCriteria.similaritySearch": {
      deep: true,
      handler() {
        this.filterChanged();
      },
    },
  },
  methods: {
    removeSimilaritySearch() {
      this.recordCriteria.similaritySearch.reset();
    },
    filterChanged() {
      if (!this.recordCriteria.hasChanges) return;
      this.recordCriteria.page.goToFirst();

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
  max-width: 100%;
  margin-right: auto;
  border-radius: $border-radius;
  color: var(--fg-secondary);
  background: var(--bg-opacity-4);
  @include font-size(12px);
  transition: background 0.3s ease-in-out;
  &:hover {
    background: var(--bg-opacity-6);
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
  &__button-icon.button {
    padding: 0;
    color: var(--fg-secondary);
  }
  &__preview {
    display: flex;
    flex: 1;
    align-items: center;
    gap: $base-space;
    min-width: 0;
    background: var(--bg-similarity);
    border: 1px solid hsl(from var(--fg-similarity) h s l / 25%);
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
      color: var(--fg-similarity);
    }
    &__button-close.button {
      padding: 0;
      color: var(--fg-similarity);
      &:hover {
        color: var(--fg-similarity);
      }
    }
  }
  :deep(.dropdown__header) {
    background: none;
    cursor: pointer;
    max-width: 200px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  :deep(.dropdown__content) {
    left: -$base-space;
    right: auto;
    top: calc(100% + 4px);
  }
  p {
    margin: 0;
    white-space: nowrap;
    font-weight: 500;
  }
}
[data-title] {
  position: relative;
  overflow: visible;
  @include tooltip-mini("top");
}
</style>
