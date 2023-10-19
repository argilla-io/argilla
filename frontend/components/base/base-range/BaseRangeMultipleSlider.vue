<template>
  <div class="range__container">
    <div class="range__inputs">
      <input
        type="number"
        v-model.number.lazy="sliderValues[0]"
        :min="min"
        :max="max"
      />
      <span class="range__separator" />
      <input
        type="number"
        v-model.number.lazy="sliderValues[1]"
        :min="min"
        :max="max"
      />
    </div>
    <div class="range__control">
      <div class="range__track" ref="track">
        <input
          class="range__slider"
          ref="from"
          type="range"
          v-model.number="sliderValues[0]"
          :min="min"
          :max="max"
          :step="step"
        />
        <input
          class="range__slider"
          ref="to"
          type="range"
          v-model.number="sliderValues[1]"
          :min="min"
          :max="max"
          :step="step"
        />
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    min: {
      type: Number,
      default: 0,
    },
    max: {
      type: Number,
      default: 1,
    },
    sliderValues: {
      type: Array,
      default: () => [0, 1],
    },
    step: {
      type: Number,
      default: () => this.max / 100,
    },
  },
  watch: {
    sliderFrom(newValue) {
      if (newValue > this.sliderTo) {
        this.sliderValues = [this.sliderFrom, this.sliderFrom];
      }
      if (newValue < this.min) {
        this.sliderValues = [this.min, newValue];
      }
      this.styleRange();
    },
    sliderTo(newValue) {
      if (newValue < this.sliderFrom) {
        this.sliderValues = [this.sliderTo, this.sliderTo];
      }
      if (newValue > this.max) {
        this.sliderValues = [this.sliderFrom, this.max];
      }
      this.$refs.to.style.zIndex = newValue <= 0 ? 2 : 0;
      this.styleRange();
    },
  },
  computed: {
    sliderFrom() {
      return this.sliderValues[0];
    },
    sliderTo() {
      return this.sliderValues[1];
    },
  },
  methods: {
    styleRange() {
      const rangeDistance = this.max - this.min;
      const fromPosition = this.sliderFrom - this.min;
      const toPosition = this.sliderTo - this.min;
      this.$refs.track.style.background = `linear-gradient(
      to right,
      #ccc 0%,
      #ccc ${(fromPosition / rangeDistance) * 100}%,
      #3e5cc9 ${(fromPosition / rangeDistance) * 100}%,
      #3e5cc9 ${(toPosition / rangeDistance) * 100}%,
      #ccc ${(toPosition / rangeDistance) * 100}%,
      #ccc 100%)`;
    },
  },
  created() {
    this.$nextTick(() => {
      this.styleRange();
    });
  },
};
</script>

<style lang="scss" scoped>
.range {
  &__container {
    display: flex;
    flex-direction: column;
    width: 100%;
    padding: $base-space;
  }
  &__control {
    position: relative;
    min-height: $base-space * 4;
  }
  &__track {
    border-radius: 15px;
    height: 6px;
    background: $black-10;
  }
  &__inputs {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: $base-space * 3;
    input {
      width: 110px;
      height: $base-space * 4;
      padding: $base-space;
      border: 1px solid $black-10;
      border-radius: $border-radius;
      outline: none;
    }
  }
  &__slider {
    position: absolute;
    -webkit-appearance: none;
    appearance: none;
    width: 100%;
    cursor: pointer;
    outline: none;
    border-radius: 15px;
    height: 6px;
    background: none;
    pointer-events: none;
    &:first-of-type {
      z-index: 1;
      height: 6px;
    }
  }
  &__separator {
    height: 1px;
    width: $base-space * 3;
    background: $black-10;
  }
}

input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none;
  pointer-events: all;
  appearance: none;
  height: 15px;
  width: 15px;
  background-color: $primary-color;
  border-radius: 50%;
  border: none;
  transition: 0.2s ease-in-out;
  cursor: pointer;
}

input[type="range"]::-moz-range-thumb {
  pointer-events: all;
  height: 15px;
  width: 15px;
  background-color: $primary-color;
  border-radius: 50%;
  border: none;
  transition: 0.2s ease-in-out;
  cursor: pointer;
}

input[type="range"]::-webkit-slider-thumb:hover {
  box-shadow: 0 0 0 6px rgba(0, 26, 255, 0.1);
}
input[type="range"]:active::-webkit-slider-thumb {
  box-shadow: 0 0 0 10px rgba(0, 26, 255, 0.1);
}
input[type="range"]:focus::-webkit-slider-thumb {
  box-shadow: 0 0 0 10px rgba(0, 26, 255, 0.1);
}
input[type="range"]::-moz-range-thumb:hover {
  box-shadow: 0 0 0 6px rgba(0, 26, 255, 0.1);
}
input[type="range"]:active::-moz-range-thumb {
  box-shadow: 0 0 0 10px rgba(0, 26, 255, 0.1);
}
input[type="range"]:focus::-moz-range-thumb {
  box-shadow: 0 0 0 10px rgba(0, 26, 255, 0.1);
}
</style>
