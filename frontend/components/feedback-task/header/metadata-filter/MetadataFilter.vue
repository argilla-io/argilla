<template>
  <div class="metadata-filter">
    <BaseDropdown
      :visible="visibleDropdown"
      @visibility="onMetadataToggleVisibility"
    >
      <span slot="dropdown-header">
        <BaseButton>Metadata</BaseButton>
      </span>
      <span slot="dropdown-content" class="metadata-filter__container">
        <metadataCategoriesSelector
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
  methods: {
    onMetadataToggleVisibility(value) {
      this.visibleDropdown = value;
      this.selectMetadataCategory(null);
    },
    selectMetadataCategory(category) {
      this.visibleCategory = this.metadataFilters.find(
        (cat) => cat.name === category
      );
    },
    applyFilter() {
      this.visibleDropdown = false;

      this.$root.$emit("metadata-filter-changed", this.metadataFilters);
    },
  },
  computed: {
    metadataCategoriesName() {
      return this.metadataFilters.map((cat) => cat.name);
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
  }
  :deep(.dropdown__content) {
    right: auto;
    left: 0;
  }
}
</style>
