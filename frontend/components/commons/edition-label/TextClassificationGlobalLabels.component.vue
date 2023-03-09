<template>
  <div class="wrapper" :class="[showAllLabels || 'show-less-labels']">
    <div class="container" v-for="label in labels" :key="label.key">
      <div class="label-text" v-html="label.text" />
    </div>
    <button>Daboudi</button>
  </div>
</template>

<script>
export default {
  name: "TextClassificationGlobalLabelsComponent",
  props: {
    labels: {
      type: Array,
      required: true,
    },
    showAllLabels: {
      type: Boolean,
      default: () => true,
    },
  },
};
</script>

<style lang="scss" scoped>
.wrapper {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  gap: 8px;
  max-width: 600px;
  scroll-behavior: auto;
  background: transparent;
  .container {
    display: flex;
  }
}

.label-text {
  outline: none;
  background: #f0f0fe;
  border-radius: 50em;
  height: 40px;
  line-height: 40px;
  padding-left: 16px;
  padding-right: 16px;
  width: 100%;
  display: flex;
  font-weight: 500;
  overflow: hidden;
  color: #4c4ea3;
  box-shadow: 0;
  transition: all 0.2s ease-in-out;
}

.show-less-labels {
  max-height: 189px;
  // overflow: auto;
}
</style>
