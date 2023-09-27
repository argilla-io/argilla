<template>
  <div
    class="metadata-filter"
    v-if="!!metadataFilters && metadataFilters.hasFilters"
  >
    <BaseDropdown
      :visible="visibleDropdown"
      @visibility="onMetadataToggleVisibility"
    >
      <span slot="dropdown-header">
        <MetadataButton
          :is-active="visibleDropdown"
          :badges="appliedCategoriesFilters"
          :active-badge="visibleCategory?.name"
          @click-on-badge="openCategoryFilter"
          @click-on-clear="removeCategoryFilters"
        />
      </span>
      <span
        v-if="!!metadataFilters"
        slot="dropdown-content"
        class="metadata-filter__container"
      >
        <MetadataCategoriesSelector
          v-if="!visibleCategory"
          class="metadata-filter__categories"
          :categories="metadataCategoriesName"
          @select-category="selectMetadataCategory"
        />
        <template v-else>
          <div
            class="metadata-filter__header"
            @click="selectMetadataCategory(null)"
          >
            <span v-text="visibleCategory.name" />
            <svgicon name="chevron-left" width="12" height="12" />
          </div>
          <div class="metadata-filter__content">
            <MetadataLabelsSelector
              v-if="visibleCategory.isTerms"
              :metadata="visibleCategory"
            />
            <div v-else>
              <MetadataRangeSelector :metadata="visibleCategory" />
            </div>
            <BaseButton
              class="metadata-filter__button primary small full-width"
              @on-click="applyFilter"
              >Filter</BaseButton
            >
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
    datasetId: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      visibleDropdown: false,
      visibleCategory: null,
      selectedOptions: [],
      appliedCategoriesFilters: [],
    };
  },
  created() {
    this.$root.$on("reset-metadata-filter", this.updateFiltersFromQueryParams);
  },
  destroyed() {
    this.$root.$off("reset-metadata-filter");
  },
  methods: {
    onMetadataToggleVisibility(value) {
      this.visibleDropdown = value;
      this.visibleCategory = null;
    },
    selectMetadataCategory(category) {
      this.visibleCategory = this.metadataFilters.findByCategory(category);
    },
    applyFilter() {
      this.visibleDropdown = false;

      this.$root.$emit(
        "metadata-filter-changed",
        this.metadataFilters.convertToRouteParam()
      );

      const newCategoryFilters = this.metadataFilters.filteredCategories.filter(
        (category) => !this.appliedCategoriesFilters.includes(category)
      );
      if (newCategoryFilters.length) {
        newCategoryFilters.forEach((f) => {
          this.appliedCategoriesFilters.push(f);
        });
      } else {
        this.appliedCategoriesFilters = this.metadataFilters.filteredCategories;
      }
    },
    openCategoryFilter(category) {
      this.visibleDropdown = this.visibleDropdown
        ? category !== this.visibleCategory?.name
        : true;

      this.selectMetadataCategory(category);
    },
    removeCategoryFilters(category) {
      this.metadataFilters.findByCategory(category).clear();
      this.applyFilter();
    },
    updateFiltersFromQueryParams() {
      this.completeByRouteParams();

      this.appliedCategoriesFilters = this.metadataFilters.filteredCategories;
    },
  },
  computed: {
    metadataCategoriesName() {
      return this.metadataFilters.categories;
    },
  },
  watch: {
    visibleDropdown() {
      if (this.visibleDropdown) {
        this.updateFiltersFromQueryParams();
      }
    },
  },
  async mounted() {
    await this.getMetadataFilters(this.datasetId);

    this.updateFiltersFromQueryParams();
  },
  setup() {
    return useMetadataFilterViewModel();
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
      background: $black-4;
    }
  }
  &__content {
    padding: $base-space;
  }
  &__categories {
    padding: $base-space;
    background: palette(white);
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
