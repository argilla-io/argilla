<template>
  <div class="chips-area">
    <button>Chip Label</button>
    <pre>{{ chips }}</pre>
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
};
</script>

<style lang="scss" scoped>
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
