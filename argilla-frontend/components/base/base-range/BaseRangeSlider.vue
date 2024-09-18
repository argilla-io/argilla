<template>
  <div>
    <label :for="id"><slot /></label>
    <div class="range__wrapper">
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
      <div class="range__legends">
        <span v-text="min" />
        <span v-text="max" />
      </div>
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
      this.$refs.slider.style.background = `linear-gradient(to right, #3e5cc9 ${this.progress}%, rgba(0, 0, 0, 0.2) ${this.progress}%)`;
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
$slider-color: var(--bg-action);
$slider-light-color: hsla(from var(--fg-cuaternary) h s l / 20%);
$slider-thumb-size: 16px;
label {
  width: fit-content;
  height: 14px;
  color: var(--fg-secondary);
}

.range {
  position: relative;
  max-width: 30%;
  min-width: 240px;
  &__wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-top: $base-space;
  }
  &__legends {
    display: flex;
    width: 100%;
    justify-content: space-between;
    color: var(--fg-tertiary);
    @include font-size(12px);
  }
  &__progress-value {
    display: none;
    position: absolute;
    top: $base-space * 3;
    margin-left: -15px;
    width: 30px;
    text-align: center;
    color: var(--color-white);
    background: var(--color-black);
    border-radius: $border-radius-s;
    @include font-size(12px);
    &:before {
      position: absolute;
      left: calc(50% - 6px);
      top: 0;
      transform: translateY(-50%);
      @include triangle(top, 6px, 6px, var(--color-black));
    }
    .range:hover & {
      display: block;
    }
  }
  &__slider {
    -webkit-appearance: none;
    appearance: none;
    width: 100%;
    cursor: pointer;
    outline: none;
    border-radius: 15px;
    height: 6px;
    background: var(--bg-opacity-10);
  }
}

input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  height: $slider-thumb-size;
  width: $slider-thumb-size;
  background-color: $slider-color;
  border-radius: 50%;
  border: none;
  transition: 0.2s ease-in-out;
}

input[type="range"]::-moz-range-thumb {
  height: $slider-thumb-size;
  width: $slider-thumb-size;
  background-color: $slider-color;
  border-radius: 50%;
  border: none;
  transition: 0.2s ease-in-out;
}

input[type="range"]::-webkit-slider-thumb:hover {
  box-shadow: 0 0 0 4px $slider-light-color;
}
input[type="range"]:active::-webkit-slider-thumb {
  box-shadow: 0 0 0 6px $slider-light-color;
}
input[type="range"]:focus::-webkit-slider-thumb {
  box-shadow: 0 0 0 6px $slider-light-color;
}
input[type="range"]::-moz-range-thumb:hover {
  box-shadow: 0 0 0 4px $slider-light-color;
}
input[type="range"]:active::-moz-range-thumb {
  box-shadow: 0 0 0 6px $slider-light-color;
}
input[type="range"]:focus::-moz-range-thumb {
  box-shadow: 0 0 0 6px $slider-light-color;
}
</style>
