<!--
  - coding=utf-8
  - Copyright 2021-present, the Recognai S.L. team.
  -
  - Licensed under the Apache License, Version 2.0 (the "License");
  - you may not use this file except in compliance with the License.
  - You may obtain a copy of the License at
  -
  -     http://www.apache.org/licenses/LICENSE-2.0
  -
  - Unless required by applicable law or agreed to in writing, software
  - distributed under the License is distributed on an "AS IS" BASIS,
  - WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  - See the License for the specific language governing permissions and
  - limitations under the License.
  -->

<template>
  <div :class="[filter.selected ? 'selected' : '', 'filter__row']">
    <svgicon
      v-if="filter.selected"
      title="remove field"
      class="filter__remove-button"
      name="close"
      width="14"
      height="14"
      @click="onRemovescoreRange()"
    />
    <div class="filter__row__content">
      <p class="filter__label">{{ filter.name }}:</p>
      <div
        class="filter__item filter__item--score"
        :class="{
          'filter__item--open': scoreExpanded,
          highlighted: filter.selected,
        }"
        @click="expandScore"
      >
        <div class="score-content">
          <vega-lite
            class="score"
            :data="options"
            :autosize="autosize"
            :config="config"
            :mark="mark"
            :encoding="encoding"
          />
        </div>
      </div>
      <div
        v-if="scoreExpanded"
        v-click-outside="onClose"
        class="filter__item filter__item--score"
        :class="{ expanded: scoreExpanded }"
      >
        <div class="score-content">
          <p class="range__panel">
            {{ min | percent(0, 2) }} to {{ max | percent(0, 2) }}
          </p>
          <vega-lite
            class="score"
            :data="options"
            :autosize="autosize"
            :config="config"
            :mark="mark"
            :encoding="encoding"
          />
          <div class="range__container">
            <ReRange
              v-if="scoreExpanded"
              ref="slider"
              v-bind="rangeOptions"
              v-model="scoreRanges"
            ></ReRange>
          </div>
        </div>
        <div class="filter__buttons">
          <ReButton
            class="button-tertiary--small button-tertiary--outline"
            @click="onClose()"
            >Cancel</ReButton
          >
          <ReButton class="button-primary--small" @click="onApplyscoreRange"
            >Apply</ReButton
          >
        </div>
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
    scoreExpanded: false,
    rangeOptions: {
      height: 4,
      dotSize: 20,
      min: 0,
      max: 100,
      interval: 1,
      show: true,
    },
    scoreRanges: [],
    autosize: {
      type: "none",
      resize: true,
      contains: "padding",
    },
    mark: "area",
    config: {
      mark: {
        color: "#0508d9",
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
      x: {
        scale: { nice: 1 },
        bin: { maxbins: 100, extent: [0.0, 1.0] },
        field: "key",
        type: "quantitative",
      },
      y: { field: "count", type: "quantitative", aggregate: "sum" },
    },
  }),
  computed: {
    options() {
      let test = Object.keys(this.filter.options).map((key) => {
        return {
          key: Number(key),
          count: this.filter.options[key],
        };
      });
      return test;
    },
    visible() {
      return this.scoreExpanded;
    },
    min() {
      return this.scoreRanges[0] * 0.01;
    },
    max() {
      return this.scoreRanges[1] * 0.01;
    },
  },
  beforeMount() {
    let from = this.filter.selected
      ? this.filter.selected.from * 100
      : this.rangeOptions.min;
    let to = this.filter.selected
      ? this.filter.selected.to * 100
      : this.rangeOptions.max;
    this.scoreRanges = [from, to];
  },
  methods: {
    expandScore() {
      this.scoreExpanded = true;
    },
    onApplyscoreRange() {
      this.$emit("apply", this.filter, {
        from: this.min,
        to: this.max,
      });
      this.scoreExpanded = false;
    },
    onRemovescoreRange() {
      this.$emit("apply", this.filter, undefined);
      this.scoreExpanded = false;
    },
    onClose() {
      this.scoreExpanded = false;
    },
  },
};
</script>
<style lang="scss" scoped>
.filter__item--score {
  position: relative;
  text-align: left;
  transition: border 0.2s ease;
  background: $lighter-color;
  width: auto;
  height: 45px;
  align-items: center;
  padding: 0 1em;
  transition: all 0.2s ease;
  border-radius: $border-radius;
  &:not(.expanded) {
    border: 1px solid $line-smooth-color;
  }
  &:not(.expanded):hover,
  &:not(.expanded):focus {
    border: 1px solid $primary-color;
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
    right: 1.5em;
    top: 50%;
    pointer-events: none;
  }
  .filter__buttons,
  .button-clear {
    display: none;
  }
  .score-content {
    width: 100%;
    text-align: center;
  }
  .range__container {
    margin-top: 2px;
    padding: 0;
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
  &.highlighted {
    border: 1px solid $primary-color;
  }
  &.expanded {
    position: absolute;
    top: calc(100% + 10px);
    right: 0;
    background: $bg;
    padding: 20px 20px 10px 20px;
    width: 270px;
    overflow: visible;
    border-radius: $border-radius;
    z-index: 4;
    box-shadow: $shadow;
    min-height: 270px;
    pointer-events: all;
    &:after {
      content: none;
    }
    .score {
      ::v-deep svg {
        max-width: 100%;
        height: 100px !important;
      }
    }
    .filter__buttons {
      margin-top: 2em;
      display: flex;
      & > * {
        display: block;
        width: 100%;
        margin-right: 0.5em;
        min-height: 38px;
        &:last-child {
          margin-right: 0;
        }
      }
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
  &__remove-button {
    position: relative;
    margin-right: 1em;
    cursor: pointer;
    flex-shrink: 0;
  }
  &__item {
    &--open {
      background: $bg;
      border-color: $bg !important;
    }
  }
  &__row {
    display: flex;
    align-items: center;
    &:not(.selected) {
      margin-left: 2em;
    }
    &__content {
      position: relative;
      display: flex;
      align-items: center;
      width: 100%;
      .filter__item--score:not(.expanded) {
        margin-left: auto;
        width: 270px;
      }
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
