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
    <p class="filter__label">{{ filter.name }}:</p>
    <filter-dropdown
      color-type="grey"
      :class="{ highlighted: visible || filter.selected }"
      :visible="visible"
      @visibility="onVisibility"
    >
      <span slot="dropdown-header">
        <vega-lite
          class="score"
          :data="options"
          :autosize="autosize"
          :config="config"
          :mark="mark"
          :encoding="encoding"
        />
      </span>
      <div slot="dropdown-content" v-if="visible">
        <div class="score">
          <p class="score__panel">
            {{ min | percent(0, 2) }} to {{ max | percent(0, 2) }}
          </p>
          <vega-lite
            :data="options"
            :autosize="autosize"
            :config="config"
            :mark="mark"
            :encoding="encoding"
          />
          <base-range
            ref="slider"
            v-bind="rangeOptions"
            v-model="scoreRanges"
          ></base-range>
        </div>
        <div class="filter__buttons">
          <base-button class="primary outline" @click="onClose()"
            >Cancel</base-button
          >
          <base-button class="primary" @click="onApplyscoreRange"
            >Apply</base-button
          >
        </div>
      </div>
    </filter-dropdown>
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
    visible: false,
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
    onVisibility(value) {
      this.visible = value;
    },
    onApplyscoreRange() {
      this.$emit("apply", this.filter, {
        from: this.min,
        to: this.max,
      });
      this.visible = false;
    },
    onRemovescoreRange() {
      this.$emit("apply", this.filter, undefined);
      this.visible = false;
    },
    onClose() {
      this.visible = false;
    },
  },
};
</script>
<style lang="scss" scoped>
.filter {
  &__remove-button {
    position: relative;
    margin-right: 1em;
    cursor: pointer;
    flex-shrink: 0;
  }
  &__buttons {
    margin-top: 1em;
    text-align: right;
    display: flex;
    & > * {
      width: 100%;
      justify-content: center;
      &:last-child {
        margin-left: $base-space;
      }
    }
  }
  &__row {
    display: flex;
    align-items: center;
    &:not(.selected) {
      margin-left: 2em;
    }
    .dropdown {
      margin-right: 0;
      margin-left: auto;
      width: 270px;
      flex-shrink: 0;
    }
    :deep(.dropdown__header) {
      svg {
        margin-top: 5px;
        height: 30px !important;
        max-width: 90%;
      }
    }
  }
}

.score {
  text-align: center;
  padding-bottom: $base-space * 2;
  &__panel {
    display: inline-block;
    border: 1px solid palette(grey, 600);
    padding: $base-space;
  }
}
:deep(.marks) {
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
