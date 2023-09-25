<template>
  <div class="metadata-filter">
    <BaseDropdown
      :visible="visibleDropdown"
      @visibility="onMetadataToggleVisibility"
    >
      <span slot="dropdown-header">
        <MetadataButton
          :badges="appliedCategories"
          :active-badge="visibleCategoryName"
          @click-on-badge="openCategoryFilter"
          @click-on-clear="removeCategoryFilters"
        />
      </span>
      <span
        slot="dropdown-content"
        class="metadata-filter__container"
        v-if="!!metadataFilters"
      >
        <MetadataCategoriesSelector
          class="metadata-filter__categories"
          :categories="metadataCategoriesName"
          v-if="!visibleCategory"
          @select-category="selectMetadataCategory"
        />
        <template v-else>
          <div
            class="metadata-filter__header"
            @click="selectMetadataCategory(null)"
          >
            <svgicon name="chevron-left" width="8" height="8" />
            <strong v-text="visibleCategory.name" />
          </div>
          <div class="metadata-filter__content">
            <transition name="fade" appear>
              <MetadataLabelsSelector
                v-if="visibleCategory.isTerms"
                :metadata="visibleCategory"
              />

              <div v-else-if="visibleCategory.isFloat">
                <BaseRangeMultipleSlider :min="0" :max="1" />
                {{ visibleCategory.settings }}
              </div>

              <div v-else-if="visibleCategory.isInteger">
                {{ visibleCategory.settings }}
              </div>

              <div v-else>{{ visibleCategory.settings }}</div>
            </transition>
            <BaseButton class="primary small full-width" @on-click="applyFilter"
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
    };
  },
  created() {
    this.$root.$on("reset-metadata-filter", this.completeByRouteParams);
  },
  destroyed() {
    this.$root.$off("reset-metadata-filter");
  },
  methods: {
    onMetadataToggleVisibility(value) {
      this.visibleDropdown = value;
      this.selectMetadataCategory(null);
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
    },
    openCategoryFilter(category, e) {
      e.stopPropagation();
      this.visibleDropdown = this.visibleDropdown ? false : true;
      this.selectMetadataCategory(category);
    },
    removeCategoryFilters(category, e) {
      e.stopPropagation();
      const clickedCategory = this.metadataFilters.metadata.find(
        (f) => f.name === category
      );
      if (clickedCategory.isTerms) {
        this.metadataFilters.metadata
          .find((f) => f.name === category)
          .options.map((opt) => (opt.selected = false));
      }

      this.applyFilter();
    },
  },
  computed: {
    metadataCategoriesName() {
      return this.metadataFilters.categories;
    },
    metadataFilterFromQuery() {
      return this.$route.query?._metadata?.split("+") ?? [];
    },
    appliedCategories() {
      return this.metadataFilterFromQuery.map((m) => m.split(":")[0]);
    },
    visibleCategoryName() {
      return (this.visibleDropdown && this.visibleCategory?.name) || null;
    },
  },
  mounted() {
    this.getMetadataFilters(this.datasetId);
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
    background: $black-4;
    padding: $base-space $base-space * 2;
    cursor: pointer;
  }
  &__content {
    padding: $base-space;
  }
  &__categories {
    padding: $base-space;
    background: palette(white);
    border-radius: $border-radius;
  }
  :deep(.dropdown__content) {
    right: auto;
    left: 0;
  }
}
</style>
