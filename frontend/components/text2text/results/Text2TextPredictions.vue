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
          <div class="predictions__tabs__wrapper">
            <base-button
              :class="selectedPredictionIndex === index ? '--active' : null"
              @click="selectPrediction(index)"
              v-for="(prediction, index) in predictions"
              :key="index"
              data-title="Score"
            >
              {{ prediction.score | percent }}</base-button
            >
          </div>
        </div>
        <transition name="fade" appear :key="selectedPredictionIndex">
          <div class="predictions__text">
            {{ selectedPrediction }}
          </div>
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
      return (this.arePredictionsVisible = !this.arePredictionsVisible);
    },
    selectPrediction(index) {
      this.selectedPredictionIndex = index;
    },
  },
  beforeDestroy() {
    this.arePredictionsVisible = false;
  },
};
</script>

<style scoped lang="scss">
.predictions {
  $this: &;
  position: relative;
  margin-bottom: 3em;
  &__panel {
    position: absolute;
    left: 0;
    z-index: 1;
    width: 340px;
    background: palette(white);
    border-radius: $border-radius;
    box-shadow: $shadow;
    border: 1px solid $black-10;
    transition: all 0.2s ease;
    max-height: 60px;
    &.--collapsed #{$this}__icon {
      opacity: 0;
    }
    #{$this}__text {
      transition: all 0.3s ease;
      transform: rotateX(-50deg);
    }
    &:hover {
      background: palette(grey, 800);
      transition: all 0.2s ease;
      &.--collapsed #{$this}__icon {
        opacity: 1;
      }
      #{$this}__button {
        color: $primary-color;
      }
    }
    &.--expanded {
      background: palette(white);
      max-height: 400px;
      transition: all 0.2s ease-in;
      #{$this}__header {
        padding: 0;
      }
      #{$this}__text {
        transition: all 1s ease;
        transform: rotateX(0);
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
    top: 1.2em;
    right: 1.2em;
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
    overflow: auto;
    max-height: 200px;
    line-height: 1.5em;
    @include font-size(13px);
  }
  &__button {
    min-height: 20px;
    padding: 0;
    color: $black-54;
    @include font-size(13px);
  }
  &__tabs {
    display: flex;
    gap: $base-space;
    margin-bottom: $base-space * 2;
    align-items: center;
    &__wrapper {
      display: flex;
      gap: $base-space;
      overflow: auto;
      max-width: 200px;
      @extend %hide-scrollbar;
    }
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
