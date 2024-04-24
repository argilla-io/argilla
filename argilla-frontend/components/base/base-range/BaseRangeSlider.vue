<template>
  <div>
    <label :for="id"><slot /></label>
    <div class="range__wrapper">
      <span class="range__legend" v-text="min" />
      <div class="range">
        <span class="range__progress-value" ref="progress" v-text="range" />
        <input
          :id="id"
          ref="slider"
          class="range__slider"
          type="range"
          :min="min"
          :max="max"
          v-model.number="range"
        />
      </div>
      <span class="range__legend" v-text="max" />
    </div>
  </div>
</template>

<script>
export default {
  props: {
    id: String,
    min: {
      type: Number,
      default: 0,
    },
    max: {
      type: Number,
      default: 100,
    },
    value: {
      type: Number,
      required: true,
    },
  },
  data() {
    return {
      range: Math.min(this.max, this.value),
    };
  },
  model: {
    prop: "value",
    event: "change",
  },
  watch: {
    range() {
      this.$emit("change", this.range);
      this.styleRange();
    },
    value() {
      this.range = this.value;
    },
  },
  computed: {
    progress() {
      return ((this.range - this.min) * 100) / (this.max - this.min);
    },
  },
  methods: {
    styleRange() {
      this.$refs.progress.style.left = `calc(${this.progress}% + (${
        8 - this.progress * 0.15
      }px))`;
      this.$refs.slider.style.background = `linear-gradient(to right, #3e5cc9 ${this.progress}%, #ccc ${this.progress}%)`;
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
label {
  width: fit-content;
  height: 14px;
  color: $black-54;
}

.range {
  position: relative;
  max-width: 30%;
  min-width: 240px;
  &__wrapper {
    display: flex;
    gap: $base-space;
    align-items: center;
    margin-top: $base-space;
  }
  &__legend {
    color: $black-37;
    @include font-size(12px);
  }
  &__progress-value {
    position: absolute;
    top: $base-space * 3;
    margin-left: -20px;
    width: 40px;
    text-align: center;
    color: $black-54;
    @include font-size(12px);
  }
  &__slider {
    -webkit-appearance: none;
    appearance: none;
    width: 100%;
    cursor: pointer;
    outline: none;
    border-radius: 15px;
    height: 6px;
    background: $black-10;
  }
}

input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  height: 15px;
  width: 15px;
  background-color: $primary-color;
  border-radius: 50%;
  border: none;
  transition: 0.2s ease-in-out;
}

input[type="range"]::-moz-range-thumb {
  height: 15px;
  width: 15px;
  background-color: $primary-color;
  border-radius: 50%;
  border: none;
  transition: 0.2s ease-in-out;
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
