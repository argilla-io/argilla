<template>
  <div class="metadata-filter" v-if="metadataFilters.hasFilters">
    <BaseDropdown
      boundary="viewport"
      :visible="visibleDropdown"
      @visibility="onMetadataToggleVisibility"
    >
      <span slot="dropdown-header">
        <FilterButtonWithBadges
          :is-active="visibleDropdown"
          :badges="appliedCategoriesFilters"
          :active-badge="visibleCategory"
          @click-on-badge="openCategoryFilter"
          @click-on-clear="clearCategoryFilter"
          @click-on-clear-all="clearAllCategories"
          :name="$t('metadata')"
        />
      </span>
      <span
        v-if="!!metadataFilters"
        slot="dropdown-content"
        class="metadata-filter__container"
      >
        <CategoriesSelector
          v-if="!visibleCategory"
          name="metadataCategories"
          class="metadata-filter__categories"
          :categories="metadataFilters.categories"
          @select-category="selectMetadataCategory"
        />
        <template v-else>
          <div
            class="metadata-filter__header"
            @click="selectMetadataCategory(null)"
          >
            <span v-text="visibleCategory.title" />
            <svgicon name="chevron-left" width="12" height="12" />
          </div>
          <div class="metadata-filter__content">
            <LabelsSelector
              v-if="visibleCategory.isTerms"
              :filter="visibleCategory"
            />
            <div v-else>
              <RangeSelector :filter="visibleCategory" />
            </div>
          </div>
        </template>
      </span>
    </BaseDropdown>
  </div>
</template>

<script>
import { useMetadataFilterViewModel } from "./useMetadataFilterViewModel";
import "assets/icons/chevron-left";

export default {
  props: {
    datasetMetadata: {
      type: Array,
      required: true,
    },
    metadataFiltered: {
      type: Array,
      required: true,
    },
  },
  model: {
    prop: "metadataFiltered",
    event: "onMetadataFilteredChanged",
  },
  data() {
    return {
      visibleDropdown: false,
      visibleCategory: null,
      appliedCategoriesFilters: [],
    };
  },
  methods: {
    onMetadataToggleVisibility(value) {
      this.visibleDropdown = value;
      this.visibleCategory = null;
    },
    selectMetadataCategory(category) {
      this.visibleCategory = null;

      this.$nextTick(() => {
        this.visibleCategory = category;
      });
    },
    applyFilter() {
      this.visibleDropdown = false;

      this.filter();
    },
    filter() {
      if (!this.metadataFilters.hasChangesSinceLatestCommit) return;

      const newFilter = this.metadataFilters.commit();

      this.$emit("onMetadataFilteredChanged", newFilter);

      this.appliedCategoriesFilters = this.metadataFilters.filteredCategories;
    },
    openCategoryFilter(category) {
      this.visibleDropdown = this.visibleDropdown
        ? category !== this.visibleCategory
        : true;

      this.selectMetadataCategory(category);
    },
    clearCategoryFilter(category) {
      category.clear();

      this.applyFilter();
    },
    clearAllCategories(categories) {
      categories.forEach((category) => {
        category.clear();
      });

      this.applyFilter();
    },
    updateAppliedCategoriesFromMetadataFilter() {
      if (!this.metadataFilters) return;

      this.metadataFilters.complete(this.metadataFiltered);

      this.appliedCategoriesFilters = this.metadataFilters.filteredCategories;
    },
  },
  watch: {
    visibleDropdown() {
      if (!this.visibleDropdown) {
        this.debounce.stop();

        this.filter();
      }
    },
    "metadataFilters.categories": {
      deep: true,
      async handler() {
        this.debounce.stop();

        await this.debounce.wait();

        this.filter();
      },
    },
    metadataFiltered() {
      this.updateAppliedCategoriesFromMetadataFilter();
    },
  },
  created() {
    this.updateAppliedCategoriesFromMetadataFilter();
  },
  setup(props) {
    return useMetadataFilterViewModel(props);
  },
};
</script>
<style lang="scss" scoped>
$metadata-filter-width: 300px;
.metadata-filter {
  &__container {
    display: block;
    width: $metadata-filter-width;
  }
  &__header {
    display: flex;
    gap: $base-space;
    align-items: center;
    justify-content: space-between;
    padding: $base-space $base-space * 2;
    cursor: pointer;
    &:hover {
      background: var(--bg-opacity-4);
    }
  }
  &__content {
    padding: $base-space;
  }
  &__categories {
    padding: $base-space;
    background: var(--bg-accent-grey-2);
    border-radius: $border-radius;
  }
  &__button.button {
    padding: 10px;
  }
  :deep(.dropdown__header:hover) {
    background: none;
  }
  :deep(.dropdown__content) {
    right: auto;
    left: 0;
  }
}
</style>
