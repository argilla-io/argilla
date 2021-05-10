<template>
  <div class="filter__row">
    <p class="filter__label">{{ filter.name }}:</p>
    <div
      class="filter__item filter__item--confidence"
      :class="{ 'filter__item--open': confidenceExpanded }"
      @click="expandConfidence"
    >
      <div class="confidence-content">
        <vega-lite
          class="confidence"
          :data="options"
          :autosize="autosize"
          :config="config"
          :mark="mark"
          :encoding="encoding"
        />
      </div>
    </div>
    <div
      v-if="confidenceExpanded"
      v-click-outside="onClose"
      class="filter__item filter__item--confidence"
      :class="{ expanded: confidenceExpanded }"
    >
      <div class="confidence-content">
        <p class="range__panel">{{ min }}% to {{ max }}%</p>
        <vega-lite
          class="confidence"
          :data="options"
          :autosize="autosize"
          :config="config"
          :mark="mark"
          :encoding="encoding"
        />
        <div class="range__container">
          <ReRange
            v-if="confidenceExpanded"
            ref="slider"
            v-bind="rangeOptions"
            v-model="confidenceRanges"
          ></ReRange>
        </div>
      </div>
      <div class="filter__buttons">
        <ReButton
          class="button-tertiary--small button-tertiary--outline"
          @click="onClose()"
          >Cancel</ReButton
        >
        <ReButton
          class="button-primary--small"
          @click="onApplyConfidenceRange()"
          >Apply</ReButton
        >
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    filter: {
      type: Object,
      default: () => ({}),
    },
  },
  data: () => ({
    confidenceExpanded: false,
    rangeOptions: {
      height: 4,
      dotSize: 20,
      min: 0,
      max: 100,
      interval: 1,
      show: true,
    },
    confidenceRanges: [],
    autosize: {
      type: "none",
      resize: true,
      contains: "padding",
    },
    mark: "area",
    config: {
      mark: {
        color: "#D9D7E4",
        binSpacing: 0,
      },
      bar: {
        binSpacing: 0,
        discreteBandSize: 0,
        continuousBandSize: 0,
      },
      axis: {
        labels: false,
      },
      view: {
        height: 100,
        width: 400,
      },
    },
    encoding: {
      x: { field: "key", type: "ordinal", scale: { rangeStep: null } },
      y: { field: "count", type: "quantitative", aggregate: "sum" },
    },
  }),
  computed: {
    options() {
      let test = Object.keys(this.filter.options).map((key) => {
        return {
          key: key,
          count: this.filter.options[key],
        };
      });
      return test;
    },
    visible() {
      return this.confidenceExpanded;
    },
    min() {
      return this.confidenceRanges[0];
    },
    max() {
      return this.confidenceRanges[1];
    },
  },
  created() {
    this.confidenceRanges = [this.rangeOptions.min, this.rangeOptions.max];
  },
  methods: {
    expandConfidence() {
      this.confidenceExpanded = true;
    },
    onApplyConfidenceRange() {
      this.$emit("apply", this.filter, {
        from: this.min * 0.01,
        to: this.max * 0.01,
      });
      this.confidenceExpanded = false;
    },
    onClose() {
      this.confidenceExpanded = false;
    },
  },
};
</script>
<style lang="scss" scoped>
.filter__item--confidence {
  position: relative;
  text-align: left;
  transition: border 0.2s ease;
  background: $lighter-color;
  width: auto;
  height: 45px;
  border: 2px solid $line-smooth-color;
  align-items: center;
  padding: 0 1em;
  transition: all 0.2s ease;
  border-radius: 0;
  &:hover,
  &:focus {
    border: 2px solid $primary-color;
    background: $lighter-color;
    transition: border 0.2s ease, background 0.2s ease;
  }
  &:after {
    content: "";
    border-color: $line-medium-color;
    border-style: solid;
    border-width: 1px 1px 0 0;
    display: inline-block;
    height: 8px;
    width: 8px;
    transform: translateY(-50%) rotate(133deg);
    transition: all 1.5s ease;
    position: absolute;
    right: 2.1em;
    top: 50%;
    pointer-events: none;
  }
  .filter__buttons,
  .button-clear {
    display: none;
  }
  .confidence-content {
    width: 100%;
    padding-right: 0.8em;
    padding-left: 0.8em;
    text-align: center;
  }
  .range__container {
    margin-top: -8px;
    padding: 0 0.5em;
  }
  .range {
    @include font-size(14px);
    text-align: center;
    display: none;
    &__panel {
      display: inline-block;
      border: 1px solid $line-smooth-color;
      padding: 0.5em 1em;
    }
  }
  ::v-deep svg {
    margin-top: 5px;
    height: 30px !important;
    max-width: 90%;
  }
  &.expanded {
    margin-top: 10px;
    position: absolute;
    top: 0;
    background: $lighter-color;
    padding: 0.8em 0.8em 0 0.8em;
    min-height: auto;
    height: auto;
    min-height: auto;
    transition: height 0.1s ease-in-out;
    overflow: visible;
    border-radius: 2px;
    z-index: 4;
    width: 400px;
    max-width: 100vw;
    min-height: 210px;
    border: 2px solid $primary-color;
    pointer-events: all;
    &:after {
      content: none;
    }
    .confidence {
      ::v-deep svg {
        max-width: 100%;
        height: 100px !important;
      }
    }
    .filter__buttons {
      margin-top: 2em;
      display: block;
    }
    .range {
      display: block;
    }
    .range__container {
      pointer-events: visible;
    }
    .label-default {
      display: block;
    }
  }
}
.filter {
  position: relative;
  &__row {
    display: flex;
    align-items: center;
    .filter__item--confidence:not(.expanded) {
      margin-right: 0;
      margin-left: auto;
      width: 220px;
    }
  }
}

::v-deep .marks {
  .background {
    stroke: none !important;
  }
  line {
    stroke: none !important;
  }
  .role-axis {
    display: none !important;
  }
  .role-legend {
    display: none !important;
  }
  text {
    font-weight: normal !important;
    font-family: $ff !important;
  }
}
</style>
