<template>
  <div class="range__container">
    <div class="range__inputs">
      <input
        type="number"
        v-model.number.lazy="values[0]"
        :min="min"
        :max="max"
        @keydown.arrow-up.stop=""
        @keydown.arrow-down.stop=""
        @keydown.arrow-right.exact.stop=""
        @keydown.arrow-left.exact.stop=""
      />
      <span class="range__separator" />
      <input
        type="number"
        v-model.number.lazy="values[1]"
        :min="min"
        :max="max"
        @keydown.arrow-up.stop=""
        @keydown.arrow-down.stop=""
        @keydown.arrow-right.exact.stop=""
        @keydown.arrow-left.exact.stop=""
      />
    </div>
    <div class="range__control">
      <div class="range__track" ref="track">
        <input
          class="range__slider"
          ref="from"
          type="range"
          v-model.number="values[0]"
          :min="min"
          :max="max"
          :step="step"
        />
        <input
          class="range__slider"
          ref="to"
          type="range"
          v-model.number="values[1]"
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
  model: {
    prop: "sliderValues",
    event: "onSliderValuesChanged",
  },
  data() {
    return {
      values: this.sliderValues,
    };
  },
  watch: {
    sliderValues() {
      this.values = this.sliderValues;
    },
    values() {
      this.$emit("onSliderValuesChanged", this.values);
    },
    sliderFrom(newValue) {
      if (newValue > this.sliderTo) {
        this.values = [this.sliderFrom, this.sliderFrom];
      }
      if (newValue < this.min) {
        this.values = [this.min, newValue];
      }

      this.styleRange();

      if (newValue === this.max) {
        this.$refs.from.style.zIndex = 4;
        this.$refs.to.style.zIndex = 3;
      }
    },
    sliderTo(newValue) {
      if (newValue < this.sliderFrom) {
        this.values = [this.sliderTo, this.sliderTo];
      }
      if (newValue > this.max) {
        this.values = [this.sliderFrom, this.max];
      }

      this.styleRange();

      if (newValue === this.min) {
        this.$refs.from.style.zIndex = 3;
        this.$refs.to.style.zIndex = 4;
      }
    },
  },
  computed: {
    sliderFrom() {
      return this.values[0];
    },
    sliderTo() {
      return this.values[1];
    },
  },
  methods: {
    styleRange() {
      const rangeDistance = this.max - this.min;
      const fromPosition = this.sliderFrom - this.min;
      const toPosition = this.sliderTo - this.min;
      this.$refs.track.style.background = `linear-gradient(
      to right,
      var(--bg-opacity-10) 0%,
      var(--bg-opacity-10) ${(fromPosition / rangeDistance) * 100}%,
      #3e5cc9 ${(fromPosition / rangeDistance) * 100}%,
      #3e5cc9 ${(toPosition / rangeDistance) * 100}%,
      var(--bg-opacity-10) ${(toPosition / rangeDistance) * 100}%,
      var(--bg-opacity-10) 100%)`;

      this.$refs.from.style.zIndex = 2;
      this.$refs.to.style.zIndex = 3;
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
$thumbColor: hsla(from var(--fg-cuaternary) h s l / 20%);
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
    background: var(--bg-opacity-10);
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
      border: 1px solid var(--bg-opacity-10);
      border-radius: $border-radius;
      outline: none;
      background: transparent;
      color: var(--bg-primary);
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
    background: var(--bg-opacity-10);
  }
}

input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none;
  pointer-events: all;
  appearance: none;
  height: 15px;
  width: 15px;
  background-color: var(--fg-cuaternary);
  border-radius: 50%;
  border: none;
  transition: 0.2s ease-in-out;
  cursor: pointer;
}

input[type="range"]::-moz-range-thumb {
  pointer-events: all;
  height: 15px;
  width: 15px;
  background-color: var(--fg-cuaternary);
  border-radius: 50%;
  border: none;
  transition: 0.2s ease-in-out;
  cursor: pointer;
}

input[type="range"]::-webkit-slider-thumb:hover {
  box-shadow: 0 0 0 6px $thumbColor;
}
input[type="range"]:active::-webkit-slider-thumb {
  box-shadow: 0 0 0 10px $thumbColor;
}
input[type="range"]:focus::-webkit-slider-thumb {
  box-shadow: 0 0 0 10px $thumbColor;
}
input[type="range"]::-moz-range-thumb:hover {
  box-shadow: 0 0 0 6px $thumbColor;
}
input[type="range"]:active::-moz-range-thumb {
  box-shadow: 0 0 0 10px $thumbColor;
}
input[type="range"]:focus::-moz-range-thumb {
  box-shadow: 0 0 0 10px $thumbColor;
}
</style>
