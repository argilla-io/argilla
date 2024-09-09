<template>
  <div class="filters__wrapper">
    <div class="filters">
      <SearchBarFilter
        v-model="recordCriteria.searchText"
        :fields="datasetFields"
      />
      <StatusFilter class="filters__status" v-model="recordCriteria.status" />
      <FilterButton
        v-if="isAnyAvailableFilter"
        class="filters__filter-button"
        @click.native="toggleVisibilityOfFilters"
        :button-name="$t('filters')"
        icon-name="filter"
        :show-chevron-icon="false"
        :is-button-active="isAnyFilterActive"
      />
      <Sort
        v-if="datasetMetadataIsLoaded && datasetQuestionIsLoaded"
        :datasetMetadata="datasetMetadata"
        :datasetQuestions="datasetQuestions"
        v-model="recordCriteria.sortBy.value"
      />
      <BaseButton
        v-if="isAnyFilterActive || isSortedBy"
        class="small clear filters__reset-button"
        @on-click="resetFilters()"
        >{{ $t("reset") }}</BaseButton
      >
      <div class="filters--right">
        <slot></slot>
      </div>
    </div>
    <div class="filters__list__wrapper" v-if="visibleFilters">
      <transition name="filterAppear" appear>
        <div class="filters__list">
          <MetadataFilter
            v-if="datasetMetadataIsLoaded && !!datasetMetadata.length"
            :datasetMetadata="datasetMetadata"
            v-model="recordCriteria.metadata.value"
          />
          <ResponsesFilter
            :datasetQuestions="datasetQuestions"
            v-model="recordCriteria.response.value"
          />
          <SuggestionFilter
            v-model="recordCriteria.suggestion.value"
            :datasetId="recordCriteria.datasetId"
            :datasetQuestions="datasetQuestions"
          />
        </div>
      </transition>
    </div>
  </div>
</template>

<script>
import { useDatasetsFiltersViewModel } from "./useDatasetsFiltersViewModel";

export default {
  name: "DatasetFilters",
  props: {
    recordCriteria: {
      type: Object,
      required: true,
    },
  },
  data: () => {
    return {
      visibleFilters: false,
    };
  },
  computed: {
    isAnyAvailableFilter() {
      return !!this.datasetMetadata.length || !!this.datasetQuestions.length;
    },
    isAnyFilterActive() {
      return (
        this.recordCriteria.isFilteredByMetadata ||
        this.recordCriteria.isFilteredByResponse ||
        this.recordCriteria.isFilteredBySuggestion
      );
    },
    isSortedBy() {
      return this.recordCriteria.isSortedBy;
    },
  },
  methods: {
    newFiltersChanged() {
      if (!this.recordCriteria.hasChanges) return;
      if (!this.recordCriteria.isChangingAutomatically) {
        this.recordCriteria.page.goToFirst();
      }

      this.$root.$emit("on-change-record-criteria-filter", this.recordCriteria);
    },
    toggleVisibilityOfFilters() {
      this.visibleFilters = !this.visibleFilters;
    },
    resetFilters() {
      this.recordCriteria.reset();
    },
  },
  watch: {
    "recordCriteria.searchText.value"() {
      this.newFiltersChanged();
    },
    "recordCriteria.status"() {
      this.newFiltersChanged();
    },
    "recordCriteria.metadata.value"() {
      this.newFiltersChanged();
    },
    "recordCriteria.sortBy.value"() {
      this.newFiltersChanged();
    },
    "recordCriteria.response.value"() {
      this.newFiltersChanged();
    },
    "recordCriteria.suggestion.value"() {
      this.newFiltersChanged();
    },
  },
  setup(props) {
    return useDatasetsFiltersViewModel(props);
  },
};
</script>

<style lang="scss" scoped>
.filters {
  display: flex;
  gap: $base-space;
  align-items: center;
  @include media("<=tablet") {
    flex-wrap: wrap;
  }
  &__wrapper {
    width: 100%;
  }
  &__list {
    position: relative;
    display: flex;
    gap: $base-space;
    width: 100%;
    padding-top: $base-space;
    overflow: auto;
    @extend %hide-scrollbar;
    &__wrapper {
      position: relative;
      &:after {
        content: "";
        position: absolute;
        right: 0;
        top: 0;
        width: $base-space * 4;
        height: 100%;
        background: linear-gradient(
          90deg,
          transparent 0%,
          var(--bg-solid-grey-1) 50%
        );
        transition: all 0.3s ease;
      }
      &:hover {
        &:after {
          width: 0;
          transition: all 0.3s ease;
        }
      }
    }
  }
  &__reset-button {
    @include font-size(13px);
    flex-shrink: 0;
  }
  &__filter-button {
    user-select: none;
    &.filter-button--active {
      background: none;
      &,
      :deep(.button) {
        color: var(--fg-cuaternary);
      }
      &:hover {
        background: hsl(from var(--fg-cuaternary) h s l / 6%);
      }
    }
  }
  &--right {
    flex-shrink: 0;
    margin-left: auto;
  }
  .search-area {
    width: min(100%, 400px);
  }
}

.filterAppear-enter-active,
.filterAppear-leave-active {
  transition: all 0.3s ease-out;
}

.filterAppear-enter,
.filterAppear-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
