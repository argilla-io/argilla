<template>
  <div class="similarity-search__options">
    <p class="similarity-search__title">Select vector:</p>
    <base-radio-button
      v-for="vector in formattedVectors"
      :key="vector.id"
      :id="vector.id"
      :value="vector"
      v-model="selectedName"
    >
      {{ vector.name }}
    </base-radio-button>
  </div>
</template>
<script>
export default {
  props: {
    formattedVectors: {
      type: Array,
      required: true,
    },
    selectedVector: {
      type: Object,
      required: true,
    },
  },
  model: {
    prop: "selectedVector",
    event: "vector-change",
  },
  computed: {
    selectedName: {
      get() {
        return this.selectedVector;
      },
      set(newValue) {
        this.$emit("vector-change", newValue);
      },
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
}
</style>
