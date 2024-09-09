<template>
  <BaseButton
    v-if="availableVectors.length === 1"
    class="small"
    @click="findSimilarUniqueVector"
    >{{ $t("similarity.findSimilar") }}</BaseButton
  >
  <BaseDropdown
    v-else
    boundary="viewport"
    :visible="dropdownIsVisible"
    @visibility="onChangeDropDownVisibility"
    class="similarity-filter"
  >
    <template slot="dropdown-header">
      <BaseButton class="small">{{ $t("similarity.findSimilar") }}</BaseButton>
    </template>
    <template slot="dropdown-content">
      <div class="similarity-filter__dropdown">
        <span class="similarity-filter__header">
          <SimilarityFilterOrder v-model="order" />
          {{ $t("similarity.similarUsing") }}:
        </span>
        <SimilarityFilterVectorRadioButtons
          v-model="vectorName"
          :vectors="availableVectors"
        />
        <div class="similarity-filter__buttons">
          <base-button class="primary outline small" @click="cancel">
            {{ $t("cancel") }}
          </base-button>
          <base-button class="primary small" @click="findSimilar">
            {{ $t("find") }}
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
      vectorName: null,
      order: null,
    };
  },
  mounted() {
    this.onSetDefaultVector();
    this.vectorName = this.recordCriteria.similaritySearch.vectorName;
    this.order = this.recordCriteria.similaritySearch.order;
  },
  methods: {
    onSetDefaultVector() {
      if (this.recordCriteria.similaritySearch.vectorName) return;

      this.recordCriteria.similaritySearch.vectorName =
        this.availableVectors[0].name;
    },
    onChangeDropDownVisibility(value) {
      this.dropdownIsVisible = value;
    },
    cancel() {
      this.onChangeDropDownVisibility(false);
    },
    findSimilarUniqueVector() {
      this.onSetDefaultVector();
      this.findSimilar();
    },
    findSimilar() {
      this.onChangeDropDownVisibility(false);
      this.recordCriteria.similaritySearch.recordId = this.recordId;
      this.recordCriteria.similaritySearch.vectorName = this.vectorName;
      this.recordCriteria.similaritySearch.order = this.order;

      if (!this.recordCriteria.hasChanges) return;
      this.recordCriteria.page.goToFirst();

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
    background: var(--bg-opacity-4);
    padding: calc($base-space / 2);
  }
  :deep(.dropdown__content) {
    left: 0;
    right: auto;
  }
}
</style>
