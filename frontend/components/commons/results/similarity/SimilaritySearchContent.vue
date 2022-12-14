<template>
  <div class="similarity-search__options">
    <p class="similarity-search__title">Select vector:</p>
    <base-radio-button
      v-for="vector in vectors"
      :key="vector.id"
      :id="vector.id"
      :value="vector"
      v-model="similaritySelectedVector"
      >{{ vector.name }}</base-radio-button
    >
  </div>
</template>
<script>
export default {
  props: {
    vectors: {
      type: Array,
      required: true,
    },
    selectedVector: {
      type: Object,
    },
  },
  model: {
    prop: "selectedVector",
    event: "vector-change",
  },
  computed: {
    similaritySelectedVector: {
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
