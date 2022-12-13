<template>
  <div v-if="multipleVectors" id="dropdown" class="similarity-search">
    <base-dropdown :visible="dropdownIsvisible" @visibility="onVisibility">
      <span slot="dropdown-header">
        <base-button class="small similarity-search__button"
          >Find similar</base-button
        >
      </span>
      <span slot="dropdown-content">
        <div class="similarity-search__options">
          <p class="similarity-search__title">Select vector:</p>
          <base-radio-button
            v-for="vector in vectors"
            :key="vector.id"
            v-model="selectedVector"
            :id="vector.id"
            :value="vector"
            >{{ vector.name }}</base-radio-button
          >
        </div>
        <div class="similarity-search__buttons">
          <base-button class="primary outline small" @click="cancel">
            Cancel
          </base-button>
          <base-button class="primary small" @click="findSimilar">
            Find
          </base-button>
        </div>
      </span>
    </base-dropdown>
  </div>
  <base-button
    id="find-similar-button"
    class="small similarity-search__button"
    :disabled="vectorIsApplied"
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
      selectedVector: {},
    };
  },
  props: {
    vectors: {
      type: Array,
      required: true,
    },
  },
  beforeMount() {
    this.applyFirstVectorByDefault();
  },
  computed: {
    multipleVectors() {
      return this.vectors?.length > 1 || false;
    },
    defaultVector() {
      return this.vectors[0];
    },
    vectorIsApplied() {
      // TODO check if vector is applied in the current query (only for single vector)
      return false;
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
      if (this.selectedVector) {
        this.$emit("find-similar", this.selectedVector);
        console.log("find-similar", this.selectedVector);
      }
      this.onVisibility(false);
    },
    cancel() {
      if (this.selectedVector === this.defaultVector) {
        this.applyFirstVectorByDefault();
      }
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
  &__button {
    transition: all 0.2s ease-in;
    @include font-size(13px);
    font-weight: 500;
    &:hover {
      background: $black-4;
      transition: all 0.2s ease-in;
    }
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
