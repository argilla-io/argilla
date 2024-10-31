<template>
  <div class="suggestion-filter" v-if="suggestionFilters.hasFilters">
    <BaseDropdown
      boundary="viewport"
      :visible="visibleDropdown"
      @visibility="onToggleVisibility"
    >
      <span slot="dropdown-header">
        <FilterButtonWithBadges
          :is-active="visibleDropdown"
          :badges="appliedCategoriesFilters"
          :active-badge="selectedSuggestion"
          @click-on-badge="openSuggestionFilter"
          @click-on-clear="clearSuggestionFilter"
          @click-on-clear-all="clearAllSuggestionFilter"
          :name="$t('suggestion.plural')"
        />
      </span>
      <span slot="dropdown-content" class="suggestion-filter__container">
        <CategoriesSelector
          v-if="!selectedSuggestion"
          name="suggestions"
          class="suggestion-filter__categories"
          :categories="suggestionFilters.questions"
          @select-category="selectSuggestion"
        />
        <template v-else>
          <div
            v-if="!selectedConfiguration"
            class="suggestion-filter__header"
            @click="selectSuggestion(null)"
          >
            <span v-text="selectedSuggestion.name" />
            <svgicon
              name="chevron-left"
              width="12"
              height="12"
              aria-hidden="true"
            />
          </div>
          <div>
            <CategoriesSelector
              v-if="!selectedConfiguration"
              name="suggestionsConfiguration"
              class="suggestion-filter__categories"
              prefix-translation="suggestion.filter."
              :categories="selectedSuggestion.configurations"
              @select-category="selectConfiguration"
            />
            <template v-else>
              <div
                class="suggestion-filter__header"
                @click="selectConfiguration(null)"
              >
                <span
                  >{{ $t(`suggestion.filter.${selectedConfiguration.name}`) }} /
                  <strong>{{ selectedSuggestion.name }}</strong></span
                >
                <svgicon name="chevron-left" width="12" height="12" />
              </div>
              <div class="suggestion-filter__content">
                <div v-if="selectedConfiguration.name === 'value'">
                  <LabelsSelector
                    v-if="selectedConfiguration.isTerms"
                    :filter="selectedConfiguration"
                  />
                  <RangeSelector
                    v-else
                    :filter="selectedConfiguration.rangeValue"
                  />
                </div>
                <div v-if="selectedConfiguration.name === 'score'">
                  <RangeSelector :filter="selectedConfiguration" />
                </div>
                <div v-if="selectedConfiguration.name === 'agent'">
                  <LabelsSelector :filter="selectedConfiguration" />
                </div>
              </div>
            </template>
          </div>
        </template>
      </span>
    </BaseDropdown>
  </div>
</template>
<script>
import { useSuggestionFilterViewModel } from "./useSuggestionFilterViewModel";

export default {
  props: {
    datasetId: {
      type: String,
      required: true,
    },
    datasetQuestions: {
      type: Array,
      required: true,
    },
    suggestionFiltered: {
      type: Array,
      required: true,
    },
  },
  model: {
    prop: "suggestionFiltered",
    event: "onSuggestionFilteredChanged",
  },
  data() {
    return {
      visibleDropdown: false,
      selectedSuggestion: null,
      selectedConfiguration: null,
      appliedCategoriesFilters: [],
    };
  },
  methods: {
    onToggleVisibility(value) {
      this.visibleDropdown = value;
      this.selectedSuggestion = null;
      this.selectedConfiguration = null;
    },
    selectSuggestion(suggestion) {
      this.selectedSuggestion = null;

      this.$nextTick(() => {
        this.selectedSuggestion = suggestion;

        this.selectedConfiguration = null;
      });
    },
    selectConfiguration(configuration) {
      this.selectedConfiguration = configuration;
    },
    applyFilter() {
      this.visibleDropdown = false;

      this.filter();
    },
    filter() {
      if (!this.suggestionFilters.hasChangesSinceLatestCommit) return;

      const newFilter = this.suggestionFilters.commit();

      this.$emit("onSuggestionFilteredChanged", newFilter);

      this.appliedCategoriesFilters = this.suggestionFilters.filteredCategories;
    },
    openSuggestionFilter(suggestion) {
      this.visibleDropdown = this.visibleDropdown
        ? suggestion !== this.selectedSuggestion
        : true;

      this.selectSuggestion(suggestion);
    },
    clearSuggestionFilter(suggestion) {
      suggestion.clear();

      this.applyFilter();
    },
    clearAllSuggestionFilter(suggestions) {
      suggestions.forEach((suggestion) => {
        suggestion.clear();
      });

      this.applyFilter();
    },
    updateAppliedCategoriesFromMetadataFilter() {
      if (!this.suggestionFilters) return;

      this.suggestionFilters.complete(this.suggestionFiltered);

      this.appliedCategoriesFilters = this.suggestionFilters.filteredCategories;
    },
  },
  watch: {
    visibleDropdown() {
      if (!this.visibleDropdown) {
        this.debounce.stop();

        this.filter();
      }
    },
    "suggestionFilters.questions": {
      deep: true,
      async handler() {
        this.debounce.stop();

        await this.debounce.wait();

        this.filter();
      },
    },
    suggestionFiltered() {
      this.updateAppliedCategoriesFromMetadataFilter();
    },
  },
  created() {
    this.updateAppliedCategoriesFromMetadataFilter();
  },
  setup(props) {
    return useSuggestionFilterViewModel(props);
  },
};
</script>

<style lang="scss" scoped>
$suggestion-filter-width: 300px;
.suggestion-filter {
  &__container {
    display: block;
    width: $suggestion-filter-width;
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
