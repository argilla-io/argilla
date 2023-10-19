<template>
  <BaseButton
    v-if="availableVectors.length === 1"
    class="small"
    @click="findSimilar"
    >Find similar</BaseButton
  >
  <BaseDropdown
    v-else
    :visible="dropdownIsVisible"
    @visibility="onVisibility"
    class="similarity-filter"
  >
    <template slot="dropdown-header">
      <BaseButton class="small">Find similar</BaseButton>
    </template>
    <template slot="dropdown-content">
      <div class="similarity-filter__dropdown">
        <span class="similarity-filter__header">
          <SimilarityFilterOrder
            v-model="recordCriteria.similaritySearch.order"
          />
          similar using:
        </span>
        <SimilarityFilterVectors
          v-model="recordCriteria.similaritySearch.vectorId"
          :vectors="availableVectors"
        />
        <div class="similarity-filter__buttons">
          <base-button class="primary outline small" @click="cancel">
            Cancel
          </base-button>
          <base-button class="primary small" @click="findSimilar">
            Find
          </base-button>
        </div>
      </div>
    </template>
  </BaseDropdown>
</template>

<script>
export default {
  props: {
    availableVectors: {
      type: Array,
      required: true,
    },
    recordCriteria: {
      type: Object,
      required: true,
    },
    recordId: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      dropdownIsVisible: false,
    };
  },
  methods: {
    onVisibility(value) {
      this.dropdownIsVisible = value;
    },
    cancel() {
      this.dropdownIsVisible = false;
    },
    findSimilar() {
      this.dropdownIsVisible = false;

      if (!this.recordCriteria.hasChanges) return;
      this.recordCriteria.page = 1;
      this.recordCriteria.similaritySearch.recordId = this.recordId;

      this.$root.$emit("on-change-record-criteria-filter", this.recordCriteria);
    },
  },
};
</script>

<style lang="scss" scoped>
.similarity-filter {
  &__dropdown {
    padding: $base-space;
    min-width: 200px;
  }
  &__header {
    display: flex;
    align-items: center;
    gap: calc($base-space / 2);
    .button:hover {
      background: none;
    }
  }
  &__buttons {
    display: flex;
    gap: $base-space;
    .button {
      width: 100%;
      justify-content: center;
    }
  }
}
.similarity-config {
  :deep(.dropdown__header) {
    background: $black-4;
    padding: calc($base-space / 2);
  }
  :deep(.dropdown__content) {
    left: 0;
    right: auto;
  }
}
</style>
