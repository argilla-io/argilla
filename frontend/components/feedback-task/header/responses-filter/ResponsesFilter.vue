<template>
  <div
    class="responses-filter"
    v-if="!!questionFilters && questionFilters.questions"
  >
    <BaseDropdown
      :visible="visibleDropdown"
      @visibility="onResponsesToggleVisibility"
    >
      <span slot="dropdown-header">
        <FilterButtonWithBadges
          :is-active="visibleDropdown"
          :badges="appliedCategoriesFilters"
          :active-badge="visibleCategory"
          @click-on-badge="openCategoryFilter"
          @click-on-clear="removeCategoryFilters"
          @click-on-clear-all="clearAllCategories"
          :name="$t('responses')"
        />
      </span>
      <span
        v-if="!!questionFilters"
        slot="dropdown-content"
        class="responses-filter__container"
      >
        <CategoriesSelector
          v-if="!visibleCategory"
          class="responses-filter__categories"
          :categories="questionFilters.questions"
          name="metadataCategories"
          @select-category="selectCategory"
        />
        <template v-else>
          <div class="responses-filter__header" @click="selectCategory(null)">
            <span v-text="visibleCategory.title" />
            <svgicon name="chevron-left" width="12" height="12" />
          </div>
          <div class="responses-filter__content">
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
import { useResponseFilterViewModel } from "./useResponseFilterViewModel";
import "assets/icons/chevron-left";

export default {
  props: {
    datasetQuestions: {
      type: Array,
      required: true,
    },
    questionFiltered: {
      type: Array,
      required: true,
    },
  },
  model: {
    prop: "questionFiltered",
    event: "onquestionFilteredChanged",
  },
  data() {
    return {
      visibleDropdown: false,
      visibleCategory: null,
      selectedOptions: [],
      appliedCategoriesFilters: [],
    };
  },
  methods: {
    onResponsesToggleVisibility(value) {
      this.visibleDropdown = value;
      this.visibleCategory = null;
    },
    selectCategory(category) {
      this.visibleCategory = category;
    },
    applyFilter() {
      this.visibleDropdown = false;

      this.filter();
    },
    filter() {
      if (!this.questionFilters.hasChangesSinceLatestCommit) return;

      const newFilter = this.questionFilters.commit();

      this.$emit("onquestionFilteredChanged", newFilter);

      this.appliedCategoriesFilters = this.questionFilters.filteredCategories;
    },
    openCategoryFilter(category) {
      this.visibleDropdown = this.visibleDropdown
        ? category !== this.visibleCategory
        : true;

      this.selectCategory(category);
    },
    removeCategoryFilters(category) {
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
      if (!this.questionFilters) return;

      // this.questionFilters.initializeWith(this.questionFiltered);

      this.appliedCategoriesFilters = this.questionFilters.filteredCategories;
    },
  },
  watch: {
    visibleDropdown() {
      if (!this.visibleDropdown) {
        this.debounce.stop();

        this.filter();
      }
    },
    "questionFilters.categories": {
      deep: true,
      async handler() {
        this.debounce.stop();

        await this.debounce.wait();

        this.filter();
      },
    },
    questionFiltered() {
      if (
        !this.questionFilters.hasChangesSinceLatestCommitWith(
          this.questionFiltered
        )
      )
        return;

      this.updateAppliedCategoriesFromMetadataFilter();
    },
  },
  created() {
    this.updateAppliedCategoriesFromMetadataFilter();
  },
  setup(props) {
    return useResponseFilterViewModel(props);
  },
};
</script>
<style lang="scss" scoped>
$responses-filter-width: 300px;
.responses-filter {
  &__container {
    display: block;
    width: $responses-filter-width;
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