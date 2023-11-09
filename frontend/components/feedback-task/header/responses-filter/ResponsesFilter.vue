<template>
  <div class="responses-filter" v-if="!!datasetQuestions">
    <BaseDropdown :visible="visibleDropdown" @visibility="onToggleVisibility">
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
          class="responses-filter__categories"
          :categories="questionFilters.questions"
          name="metadataCategories"
          @select-category="selectResponse"
        />
        <template v-else>
          <div class="responses-filter__header" @click="selectResponse(null)">
            <span v-text="selectedResponse.name" />
            <svgicon name="chevron-left" width="12" height="12" />
          </div>
          <div class="responses-filter__content">
            <LabelsSelector :filter="selectedResponse" />
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
  },
  data() {
    return {
      visibleDropdown: false,
      selectedResponse: null,
    };
  },
  methods: {
    onToggleVisibility(value) {
      this.visibleDropdown = value;
      this.selectedResponse = null;
    },
    selectResponse(response) {
      this.selectedResponse = response;
    },
    openResponseFilter(response) {
      this.visibleDropdown = this.visibleDropdown
        ? response !== this.selectedResponse
        : true;

      this.selectResponse(response);
    },
    clearResponseFilter() {
      this.$emit("remove-suggestion-filter");
    },
    clearAllResponseFilter() {
      this.$emit("clear-all-suggestion-filter");
    },
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
