<template>
  <div class="predictions">
    <div
      class="predictions__panel"
      :class="arePredictionsVisible ? '--expanded' : '--collapsed'"
    >
      <div class="predictions__header" @click="toggleVisibility">
        <base-button
          v-if="!arePredictionsVisible"
          class="predictions__button"
          :class="arePredictionsVisible === 'Prediction' ? '--active' : null"
          >Prediction</base-button
        >
        <svgicon
          @click="arePredictionsVisible && toggleVisibility"
          class="predictions__icon"
          :name="arePredictionsVisible ? 'chevron-up' : 'chevron-down'"
          width="16"
          height="16"
        />
      </div>
      <div v-if="arePredictionsVisible" class="predictions__content">
        <div class="predictions__tabs">
          <p class="predictions__title">Prediction:</p>
          <base-button
            :class="selectedPredictionIndex === index ? '--active' : null"
            @click="selectPrediction(index)"
            v-for="(prediction, index) in predictions"
            :key="index"
          >
            {{ prediction.score | percent }}</base-button
          >
        </div>
        <transition name="fade" appear :key="selectedPredictionIndex">
          <div class="predictions__text">{{ selectedPrediction }}</div>
        </transition>
      </div>
    </div>
  </div>
</template>

<script>
import "assets/icons/chevron-down";
import "assets/icons/chevron-up";
import { IdState } from "vue-virtual-scroller";
export default {
  mixins: [
    IdState({
      // You can customize this
      idProp: (vm) => `${vm.record.id}`,
    }),
  ],
  props: {
    record: {
      type: Object,
      required: true,
    },
    predictions: {
      type: Array,
      required: true,
    },
  },
  idState() {
    return {
      arePredictionsVisible: false,
      selectedPredictionIndex: 0,
    };
  },
  computed: {
    arePredictionsVisible: {
      get: function () {
        return this.idState.arePredictionsVisible;
      },
      set: async function (newValue) {
        this.idState.arePredictionsVisible = newValue;
      },
    },
    selectedPredictionIndex: {
      get: function () {
        return this.idState.selectedPredictionIndex;
      },
      set: async function (newValue) {
        this.idState.selectedPredictionIndex = newValue;
      },
    },
    selectedPrediction() {
      return this.predictions[this.selectedPredictionIndex].text;
    },
  },
  methods: {
    toggleVisibility() {
      console.log(this.arePredictionsVisible);
      return (this.arePredictionsVisible = !this.arePredictionsVisible);
    },
    selectPrediction(index) {
      this.selectedPredictionIndex = index;
    },
  },
};
</script>

<style scoped lang="scss">
.predictions {
  position: relative;
  &__panel {
    position: absolute;
    left: 0;
    z-index: 1;
    width: 340px;
    background: palette(white);
    border-radius: $border-radius;
    box-shadow: 0px 0px 4px 0px rgb(0 0 0 / 15%);
    border: 1px solid transparent;
    &:hover,
    &.--expanded {
      border-color: $black-10;
    }
    &.--expanded {
      .predictions__header {
        padding: 0;
      }
    }
  }
  &__header {
    display: flex;
    align-items: center;
    padding: $base-space * 2;
    cursor: pointer;
  }
  &__icon {
    position: absolute;
    top: $base-space * 2;
    right: $base-space * 2;
    color: $black-37;
    cursor: pointer;
  }
  &__content {
    padding: $base-space * 2;
  }
  &__title {
    margin: 0;
    @include font-size(13px);
    color: $primary-color;
    line-height: 1;
    font-weight: 500;
  }
  &__text {
    @include font-size(13px);
    overflow: auto;
    max-height: 200px;
  }
  &__button {
    padding: 0;
    color: $primary-color;
    @include font-size(13px);
  }
  &__tabs {
    display: flex;
    gap: $base-space;
    margin-bottom: $base-space * 2;
    align-items: center;
    .button {
      padding: 2px 6px;
      @include font-size(12px);
      color: $black-54;
      border: 1px solid $black-20;
      border-radius: $border-radius;
      background-color: $black-4;
      &.--active,
      &:hover {
        background-color: palette(white);
      }
      &.--active {
        color: $primary-color;
        border-color: $primary-color;
        background-color: palette(white);
      }
      &[data-title] {
        position: relative;
        overflow: visible;
        @extend %has-tooltip--top;
      }
    }
  }
}
</style>
