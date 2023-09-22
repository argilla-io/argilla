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
                v-if="visibleCategory.settings.type === 'terms'"
                :labels="visibleCategory.settings.values"
                v-model="selectedOptions"
              />

              <div v-else-if="visibleCategory.settings.type === 'float'">
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
import { metadataMocked } from "@/v1/domain/entities/__mocks__/metadata/mock.ts";
import "assets/icons/chevron-left";
export default {
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
      console.log("filter applied");
      this.visibleDropdown = false;
    },
  },
  computed: {
    metadataCategoriesName() {
      return this.metadataFilters.map((cat) => cat.name);
    },
  },
  created() {
    this.metadataFilters = metadataMocked;
  },
};
</script>
<style lang="scss" scoped>
$metadata-filter-width: 300px;
.metadata-filter {
  &__container {
    display: block;
    min-width: $metadata-filter-width;
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
    padding: $base-space * 2;
  }
  &__categories {
    padding: $base-space * 2;
  }
  :deep(.dropdown__content) {
    right: auto;
    left: 0;
  }
}
</style>
