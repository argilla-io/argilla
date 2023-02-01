<template>
  <div v-if="multipleVectors" id="dropdown" class="similarity-search">
    <base-dropdown :visible="dropdownIsvisible" @visibility="onVisibility">
      <span slot="dropdown-header">
        <base-button class="small clear"> Find similar </base-button>
      </span>
      <span slot="dropdown-content">
        <similarity-search-content
          :formattedVectors="formattedVectors"
          v-model="selectedVector"
        />
        <similarity-search-footer
          @cancel="cancel"
          @find-similar="findSimilar"
        />
      </span>
    </base-dropdown>
  </div>
  <base-button
    id="find-similar-button"
    class="small clear"
    :disabled="isDisabled"
    v-else
    @click="findSimilar"
    >Find similar</base-button
  >
</template>

<script>
export default {
  data() {
    return {
      dropdownIsvisible: false,
      selectedVector: null,
    };
  },
  props: {
    formattedVectors: {
      type: Array,
      required: true,
    },
    isReferenceRecord: {
      type: Boolean,
      default: false,
    },
  },
  beforeMount() {
    this.applyFirstVectorByDefault();
  },
  computed: {
    multipleVectors() {
      return this.formattedVectors?.length > 1 || false;
    },
    defaultVector() {
      return this.formattedVectors[0];
    },
    isDisabled() {
      // TODO check if vector is applied in the current query (only for single vector)
      return (this.isReferenceRecord && !this.multipleVectors) || false;
    },
  },
  methods: {
    onVisibility(value) {
      this.dropdownIsvisible = value;
    },
    applyFirstVectorByDefault() {
      this.selectedVector = this.defaultVector;
    },
    findSimilar() {
      this.$emit("search-records", this.selectedVector);
      this.onVisibility(false);
    },
    cancel() {
      this.applyFirstVectorByDefault();
      this.onVisibility(false);
    },
  },
};
</script>

<style lang="scss" scoped>
.similarity-search {
  position: relative;
  &__options {
    margin-bottom: 2em;
  }
  &__title {
    color: $black-87;
    font-weight: 500;
    margin-top: 0;
  }
  &__buttons {
    display: flex;
    gap: $base-space;
    & > * {
      flex: 1;
      justify-content: center;
    }
  }
}
</style>
