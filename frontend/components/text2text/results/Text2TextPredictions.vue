<template>
  <div v-click-outside="close">
    <base-button
      class="predictions__button"
      :class="arePredictionsVisible === 'Prediction' ? '--active' : null"
      @click="toggleVisibility"
      >{{ `Predictions (${predictions.length})` }}</base-button
    >
    <div v-if="arePredictionsVisible" class="predictions__content">
      <div class="predictions__tabs">
        <base-button
          :class="selectedPredictionIndex === index ? '--active' : null"
          @click="selectPrediction(index)"
          v-for="(prediction, index) in predictions"
          :key="index"
        >
          Score: {{ prediction.score | percent }}</base-button
        >
      </div>
      <transition name="fade" appear :key="selectedPredictionIndex">
        <div class="predictions__text">{{ selectedPrediction }}</div>
      </transition>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    predictions: {
      type: Array,
      required: true,
    },
  },
  data: () => {
    return {
      arePredictionsVisible: false,
      selectedPredictionIndex: 0,
    };
  },
  computed: {
    selectedPrediction() {
      return this.predictions[this.selectedPredictionIndex].text;
    },
  },
  methods: {
    toggleVisibility() {
      return (this.arePredictionsVisible = !this.arePredictionsVisible);
    },
    close() {
      this.arePredictionsVisible = false;
    },
    selectPrediction(index) {
      this.selectedPredictionIndex = index;
    },
  },
};
</script>

<style scoped lang="scss">
.predictions {
  &__content {
    position: absolute;
    right: 0;
    z-index: 1;
    width: 400px;
    background: palette(white);
    border-radius: $border-radius;
    box-shadow: $shadow;
    padding: $base-space * 2;
  }
  &__text {
    @include font-size(13px);
    overflow: auto;
    max-height: 200px;
  }
  &__button {
    color: $primary-color;
  }
  &__tabs {
    display: flex;
    margin-bottom: $base-space * 2;
    .button {
      border-radius: 0;
      padding: $base-space;
      border-bottom: 2px solid transparent;
      color: $black-54;
      @include font-size(13px);
      &:hover {
        color: $black-87;
      }
      &.--active {
        border-color: $primary-color;
        color: $black-87;
      }
    }
  }
}
</style>
