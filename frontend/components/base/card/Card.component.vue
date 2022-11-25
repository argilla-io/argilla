<template>
  <div class="card" :style="cssVars"><slot /></div>
</template>

<script>
export default {
  name: "CardComponent",
  props: {
    textColor: {
      type: String,
      default: () => "#4D4D4D",
    },
    backgroundColor: {
      type: String,
      default: () => "#fff",
    },
    backgroundLabelColor: {
      type: String,
      default: () => "#fff",
    },
  },
  computed: {
    cssVars() {
      return {
        "--text-color": this.textColor,
        "--background-color": this.backgroundColor,
        "--background-label-color": this.backgroundLabelColor,
      };
    },
  },
};
</script>

<style lang="scss" scoped>
.card {
  width: 100%;
  padding: 2em;
  color: var(--text-color);
  background-color: var(--background-color);
  border: 1px solid #e9eaed;
  border-radius: 10px;
}
</style>
