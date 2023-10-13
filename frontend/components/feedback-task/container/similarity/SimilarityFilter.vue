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
          <SimilarityConfigDropdown
            :value="mostOrLeastSimilar"
            :options="['Most', 'Least']"
          />
          similar using:
        </span>
        <BaseRadioButton
          v-for="vector in availableVectors"
          :key="vector.id"
          :id="vector.id"
          :value="vector"
          v-model="selectedVector"
        >
          {{ vector.id }}
        </BaseRadioButton>
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
  },
  data() {
    return {
      dropdownIsVisible: false,
      selectedVector: this.availableVectors[0],
      mostOrLeastSimilar: "Most",
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
      console.log(
        "Search similarity...",
        this.mostOrLeastSimilar,
        this.selectedVector
      );
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
