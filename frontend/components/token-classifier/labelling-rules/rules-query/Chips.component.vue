<template>
  <div class="chips">
    <div class="chips-wrapper">
      <div class="chips__items" v-for="chip in chips" :key="chip.id">
        <button @click="onChipsSelection(chip)">{{ chip.text }}</button>
      </div>
    </div>
    <!-- <pre>{{ chips }}</pre> -->
  </div>
</template>

<script>
export default {
  component: "ChipsComponent",
  props: {
    chips: {
      type: Array,
      required: true,
    },
  },
  methods: {
    onChipsSelection({ text }) {
      console.log(text);
      this.$emit("on-chips-selection", { text });
    },
  },
};
</script>

<style lang="scss" scoped>
.chips {
  // display: flex;
  flex: 1;
  &__items {
    display: inline-flex;
  }
}
button {
  border: none;
  min-height: 50px;
  min-width: 100px;
  border-radius: 8px;
  color: black;
  background-color: #e0e1ff;
  cursor: pointer;
}
</style>
