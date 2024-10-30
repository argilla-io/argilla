<template>
  <div class="responses-filter" v-if="questionFilters.hasFilters">
    <BaseDropdown
      boundary="viewport"
      :visible="visibleDropdown"
      @visibility="onToggleVisibility"
    >
      <span slot="dropdown-header">
        <FilterButtonWithBadges
          :is-active="visibleDropdown"
          :badges="appliedCategoriesFilters"
          :active-badge="selectedResponse"
          @click-on-badge="openResponseFilter"
          @click-on-clear="clearResponseFilter"
          @click-on-clear-all="clearAllResponseFilter"
          :name="$t('responses')"
        />
      </span>
      <span slot="dropdown-content" class="responses-filter__container">
        <CategoriesSelector
          v-if="!selectedResponse"
          name="responsesCategories"
          class="responses-filter__categories"
          :categories="questionFilters.responses"
          @select-category="selectResponse"
        />
        <template v-else>
          <div class="responses-filter__header" @click="selectResponse(null)">
            <span v-text="selectedResponse.name" />
            <svgicon
              name="chevron-left"
              width="12"
              height="12"
              aria-hidden="true"
            />
          </div>
          <div class="responses-filter__content">
            <LabelsSelector
              v-if="selectedResponse.isTerms"
              :filter="selectedResponse.options"
            />
            <RangeSelector v-else :filter="selectedResponse.rangeValue" />
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
    responseFiltered: {
      type: Array,
      required: true,
    },
  },
  model: {
    prop: "responseFiltered",
    event: "onResponseFilteredChanged",
  },
  data() {
    return {
      visibleDropdown: false,
      selectedResponse: null,
      appliedCategoriesFilters: [],
    };
  },
  methods: {
    onToggleVisibility(value) {
      this.visibleDropdown = value;
      this.selectedResponse = null;
    },
    selectResponse(response) {
      this.selectedResponse = null;

      this.$nextTick(() => {
        this.selectedResponse = response;
      });
    },
    applyFilter() {
      this.visibleDropdown = false;

      this.filter();
    },
    filter() {
      if (!this.questionFilters.hasChangesSinceLatestCommit) return;

      const newFilter = this.questionFilters.commit();

      this.$emit("onResponseFilteredChanged", newFilter);

      this.appliedCategoriesFilters = this.questionFilters.filteredCategories;
    },
    openResponseFilter(response) {
      this.visibleDropdown = this.visibleDropdown
        ? response !== this.selectedResponse
        : true;

      this.selectResponse(response);
    },
    clearResponseFilter(response) {
      response.clear();

      this.applyFilter();
    },
    clearAllResponseFilter(response) {
      response.forEach((response) => {
        response.clear();
      });

      this.applyFilter();
    },
    updateAppliedCategoriesFromMetadataFilter() {
      if (!this.questionFilters) return;

      this.questionFilters.complete(this.responseFiltered);

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
    "questionFilters.responses": {
      deep: true,
      async handler() {
        this.debounce.stop();

        await this.debounce.wait();

        this.filter();
      },
    },
    responseFiltered() {
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
