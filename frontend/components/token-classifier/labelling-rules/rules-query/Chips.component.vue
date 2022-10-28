<template>
  <div class="chips">
    <div class="chips__items" v-for="chip in chips" :key="chip.id">
      <button @click="onChipsSelection(chip)">{{ chip.text }}</button>
    </div>
  </div>
  <!-- <pre>{{ chips }}</pre> -->
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
    onChipsSelection({ id, text }) {
      console.log(text, id);
      this.$emit("on-chips-selection", { text, id });
    },
  },
};
</script>

<style lang="scss" scoped>
.chips {
  flex: 1;
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
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
