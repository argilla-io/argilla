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
  <div
    v-show="show"
    ref="wrap"
    :class="[
      'vue-slider-component',
      flowDirection,
      disabledClass,
      stateClass,
      { 'vue-slider-has-label': piecewiseLabel },
    ]"
    :style="wrapStyles"
    @click="wrapClick"
  >
    <div
      ref="elem"
      aria-hidden="true"
      class="vue-slider"
      :style="[elemStyles, bgStyle]"
    >
      <div v-if="isRange">
        <div
          ref="dot0"
          :class="[
            tooltipStatus,
            'vue-slider-dot',
            {
              'vue-slider-dot-focus': focusFlag && focusSlider === 0,
              'vue-slider-dot-dragging': flag && currentSlider === 0,
            },
          ]"
          :style="[
            dotStyles,
            sliderStyles[0],
            focusFlag && focusSlider === 0 ? focusStyles[0] : null,
          ]"
          @mousedown="moveStart($event, 0)"
          @touchstart="moveStart($event, 0)"
        >
          <span
            :class="[
              'vue-slider-tooltip-' + tooltipDirection[0],
              'vue-slider-tooltip-wrap',
            ]"
          >
            <slot name="tooltip" :value="val[0]" :index="0">
              <span class="vue-slider-tooltip" :style="tooltipStyles[0]">{{
                formatter ? formatting(val[0]) : val[0]
              }}</span>
            </slot>
          </span>
        </div>
        <div
          ref="dot1"
          :class="[
            tooltipStatus,
            'vue-slider-dot',
            {
              'vue-slider-dot-focus': focusFlag && focusSlider === 1,
              'vue-slider-dot-dragging': flag && currentSlider === 1,
            },
          ]"
          :style="[
            dotStyles,
            sliderStyles[1],
            focusFlag && focusSlider === 1 ? focusStyles[1] : null,
          ]"
          @mousedown="moveStart($event, 1)"
          @touchstart="moveStart($event, 1)"
        >
          <span
            :class="[
              'vue-slider-tooltip-' + tooltipDirection[1],
              'vue-slider-tooltip-wrap',
            ]"
          >
            <slot name="tooltip" :value="val[1]" :index="1">
              <span class="vue-slider-tooltip" :style="tooltipStyles[1]">{{
                formatter ? formatting(val[1]) : val[1]
              }}</span>
            </slot>
          </span>
        </div>
      </div>
      <div v-else>
        <div
          ref="dot"
          :class="[
            tooltipStatus,
            'vue-slider-dot',
            {
              'vue-slider-dot-focus': focusFlag && focusSlider === 0,
              'vue-slider-dot-dragging': flag && currentSlider === 0,
            },
          ]"
          :style="[
            dotStyles,
            sliderStyles,
            focusFlag && focusSlider === 0 ? focusStyles : null,
          ]"
          @mousedown="moveStart"
          @touchstart="moveStart"
        >
          <span
            :class="[
              'vue-slider-tooltip-' + tooltipDirection,
              'vue-slider-tooltip-wrap',
            ]"
          >
            <slot name="tooltip" :value="val">
              <span class="vue-slider-tooltip" :style="tooltipStyles">{{
                formatter ? formatting(val) : val
              }}</span>
            </slot>
          </span>
        </div>
      </div>
      <ul class="vue-slider-piecewise">
        <li
          v-for="(piecewiseObj, index) in piecewiseDotWrap"
          :key="index"
          class="vue-slider-piecewise-item"
          :style="[piecewiseDotStyle, piecewiseObj.style]"
        >
          <slot
            name="piecewise"
            :label="piecewiseObj.label"
            :index="index"
            :first="index === 0"
            :last="index === piecewiseDotWrap.length - 1"
            :active="piecewiseObj.inRange"
          >
            <span
              v-if="piecewise"
              class="vue-slider-piecewise-dot"
              :style="[
                piecewiseStyle,
                piecewiseObj.inRange ? piecewiseActiveStyle : null,
              ]"
            ></span>
          </slot>

          <slot
            name="label"
            :label="piecewiseObj.label"
            :index="index"
            :first="index === 0"
            :last="index === piecewiseDotWrap.length - 1"
            :active="piecewiseObj.inRange"
          >
            <span
              v-if="piecewiseLabel"
              class="vue-slider-piecewise-label"
              :style="[
                labelStyle,
                piecewiseObj.inRange ? labelActiveStyle : null,
              ]"
              >{{ piecewiseObj.label }}</span
            >
          </slot>
        </li>
      </ul>
      <div
        ref="process"
        :class="[
          'vue-slider-process',
          { 'vue-slider-process-dragable': isRange && processDragable },
        ]"
        :style="processStyle"
        @click="processClick"
        @mousedown="moveStart($event, 0, true)"
        @touchstart="moveStart($event, 0, true)"
      ></div>
    </div>
    <input
      v-if="!isRange && !data"
      v-model="val"
      class="vue-slider-sr-only"
      type="range"
      :min="min"
      :max="max"
    />
  </div>
</template>

<script>
// Unsharp text [#166](https://github.com/NightCatSama/vue-slider-component/issues/166)
const roundToDPR = (function () {
  const r = typeof window !== "undefined" ? window.devicePixelRatio || 1 : 1;
  return (value) => Math.round(value * r) / r;
})();

export default {
  props: {
    width: {
      type: [Number, String],
      default: "auto",
    },
    height: {
      type: [Number, String],
      default: 6,
    },
    data: {
      type: Array,
      default: null,
    },
    dotSize: {
      type: Number,
      default: 16,
    },
    dotWidth: {
      type: Number,
      required: false,
    },
    dotHeight: {
      type: Number,
      required: false,
    },
    min: {
      type: Number,
      default: 0,
    },
    max: {
      type: Number,
      default: 100,
    },
    interval: {
      type: Number,
      default: 1,
    },
    show: {
      type: Boolean,
      default: true,
    },
    disabled: {
      type: Boolean,
      default: false,
    },
    piecewise: {
      type: Boolean,
      default: false,
    },
    tooltip: {
      type: [String, Boolean],
      default: "always",
    },
    eventType: {
      type: String,
      default: "auto",
    },
    direction: {
      type: String,
      default: "horizontal",
    },
    reverse: {
      type: Boolean,
      default: false,
    },
    lazy: {
      type: Boolean,
      default: false,
    },
    clickable: {
      type: Boolean,
      default: true,
    },
    speed: {
      type: Number,
      default: 0.5,
    },
    realTime: {
      type: Boolean,
      default: false,
    },
    stopPropagation: {
      type: Boolean,
      default: false,
    },
    value: {
      type: [String, Number, Array, Object],
      default: 0,
    },
    piecewiseLabel: {
      type: Boolean,
      default: false,
    },
    debug: {
      type: Boolean,
      default: true,
    },
    fixed: {
      type: Boolean,
      default: false,
    },
    processDragable: {
      type: Boolean,
      default: false,
    },
    useKeyboard: {
      type: Boolean,
      default: false,
    },
    actionsKeyboard: {
      type: Array,
      default() {
        return [(i) => i - 1, (i) => i + 1];
      },
    },
    sliderStyle: [Array, Object, Function],
    focusStyle: [Array, Object, Function],
    tooltipDir: [Array, String],
    formatter: [String, Function],
    piecewiseStyle: Object,
    piecewiseActiveStyle: Object,
    processStyle: Object,
    bgStyle: Object,
    tooltipStyle: [Array, Object, Function],
    labelStyle: Object,
    labelActiveStyle: Object,
  },
  data() {
    return {
      flag: false,
      keydownFlag: null,
      focusFlag: false,
      processFlag: false,
      processSign: null,
      size: 0,
      fixedValue: 0,
      focusSlider: 0,
      currentValue: 0,
      currentSlider: 0,
      isComponentExists: true,
    };
  },
  computed: {
    dotWidthVal() {
      return typeof this.dotWidth === "number" ? this.dotWidth : this.dotSize;
    },
    dotHeightVal() {
      return typeof this.dotHeight === "number" ? this.dotHeight : this.dotSize;
    },
    flowDirection() {
      return `vue-slider-${this.direction + (this.reverse ? "-reverse" : "")}`;
    },
    tooltipDirection() {
      const dir =
        this.tooltipDir || (this.direction === "vertical" ? "left" : "top");
      if (Array.isArray(dir)) {
        return this.isRange ? dir : dir[1];
      }
      return this.isRange ? [dir, dir] : dir;
    },
    tooltipStatus() {
      return this.tooltip === "hover" && this.flag
        ? "vue-slider-always"
        : this.tooltip
        ? `vue-slider-${this.tooltip}`
        : "";
    },
    tooltipClass() {
      return [
        `vue-slider-tooltip-${this.tooltipDirection}`,
        "vue-slider-tooltip",
      ];
    },
    isDisabled() {
      return this.eventType === "none" ? true : this.disabled;
    },
    disabledClass() {
      return this.disabled ? "vue-slider-disabled" : "";
    },
    stateClass() {
      return {
        "vue-slider-state-process-drag": this.processFlag,
        "vue-slider-state-drag":
          this.flag && !this.processFlag && !this.keydownFlag,
        "vue-slider-state-focus": this.focusFlag,
      };
    },
    isRange() {
      return Array.isArray(this.value);
    },
    slider() {
      return this.isRange ? [this.$refs.dot0, this.$refs.dot1] : this.$refs.dot;
    },
    minimum() {
      return this.data ? 0 : this.min;
    },
    val: {
      get() {
        return this.data
          ? this.isRange
            ? [this.data[this.currentValue[0]], this.data[this.currentValue[1]]]
            : this.data[this.currentValue]
          : this.currentValue;
      },
      set(val) {
        if (this.data) {
          if (this.isRange) {
            const index0 = this.data.indexOf(val[0]);
            const index1 = this.data.indexOf(val[1]);
            if (index0 > -1 && index1 > -1) {
              this.currentValue = [index0, index1];
            }
          } else {
            const index = this.data.indexOf(val);
            if (index > -1) {
              this.currentValue = index;
            }
          }
        } else {
          this.currentValue = val;
        }
      },
    },
    currentIndex() {
      if (this.isRange) {
        return this.data
          ? this.currentValue
          : [
              this.getIndexByValue(this.currentValue[0]),
              this.getIndexByValue(this.currentValue[1]),
            ];
      }
      return this.getIndexByValue(this.currentValue);
    },
    indexRange() {
      if (this.isRange) {
        return this.currentIndex;
      }
      return [0, this.currentIndex];
    },
    maximum() {
      return this.data ? this.data.length - 1 : this.max;
    },
    multiple() {
      const decimals = `${this.interval}`.split(".")[1];
      return decimals ? Math.pow(10, decimals.length) : 1;
    },
    spacing() {
      return this.data ? 1 : this.interval;
    },
    total() {
      if (this.data) {
        return this.data.length - 1;
      }
      if (
        Math.floor((this.maximum - this.minimum) * this.multiple) %
          (this.interval * this.multiple) !==
        0
      ) {
        this.printError(
          "Prop[interval] is illegal, Please make sure that the interval can be divisible"
        );
      }
      return (this.maximum - this.minimum) / this.interval;
    },
    gap() {
      return this.size / this.total;
    },
    position() {
      return this.isRange
        ? [
            ((this.currentValue[0] - this.minimum) / this.spacing) * this.gap,
            ((this.currentValue[1] - this.minimum) / this.spacing) * this.gap,
          ]
        : ((this.currentValue - this.minimum) / this.spacing) * this.gap;
    },
    limit() {
      /* eslint-disable indent */
      return this.isRange
        ? this.fixed
          ? [
              [
                0,
                ((this.maximum - this.fixedValue * this.spacing) /
                  this.spacing) *
                  this.gap,
              ],
              [
                ((this.minimum + this.fixedValue * this.spacing) /
                  this.spacing) *
                  this.gap,
                this.size,
              ],
            ]
          : [
              [0, this.position[1]],
              [this.position[0], this.size],
            ]
        : [0, this.size];
    },
    valueLimit() {
      return this.isRange
        ? this.fixed
          ? [
              [this.minimum, this.maximum - this.fixedValue * this.spacing],
              [this.minimum + this.fixedValue * this.spacing, this.maximum],
            ]
          : [
              [this.minimum, this.currentValue[1]],
              [this.currentValue[0], this.maximum],
            ]
        : [this.minimum, this.maximum];
    },
    idleSlider() {
      return this.currentSlider === 0 ? 1 : 0;
    },
    wrapStyles() {
      return this.direction === "vertical"
        ? {
            height:
              typeof this.height === "number"
                ? `${this.height}px`
                : this.height,
            padding: `${this.dotHeightVal / 2}px ${this.dotWidthVal / 2}px`,
          }
        : {
            width:
              typeof this.width === "number" ? `${this.width}px` : this.width,
            padding: `${this.dotHeightVal / 2}px ${this.dotWidthVal / 2}px`,
          };
    },
    sliderStyles() {
      if (Array.isArray(this.sliderStyle)) {
        return this.isRange ? this.sliderStyle : this.sliderStyle[1];
      }
      if (typeof this.sliderStyle === "function") {
        return this.sliderStyle(this.val, this.currentIndex);
      }
      return this.isRange
        ? [this.sliderStyle, this.sliderStyle]
        : this.sliderStyle;
    },
    focusStyles() {
      if (Array.isArray(this.focusStyle)) {
        return this.isRange ? this.focusStyle : this.focusStyle[1];
      }
      if (typeof this.focusStyle === "function") {
        return this.focusStyle(this.val, this.currentIndex);
      }
      return this.isRange
        ? [this.focusStyle, this.focusStyle]
        : this.focusStyle;
    },
    tooltipStyles() {
      if (Array.isArray(this.tooltipStyle)) {
        return this.isRange ? this.tooltipStyle : this.tooltipStyle[1];
      }
      if (typeof this.tooltipStyle === "function") {
        return this.tooltipStyle(this.val, this.currentIndex);
      }
      return this.isRange
        ? [this.tooltipStyle, this.tooltipStyle]
        : this.tooltipStyle;
    },
    elemStyles() {
      return this.direction === "vertical"
        ? {
            width: `${this.width}px`,
            height: "100%",
          }
        : {
            height: `${this.height}px`,
          };
    },
    dotStyles() {
      return this.direction === "vertical"
        ? {
            width: `${this.dotWidthVal}px`,
            height: `${this.dotHeightVal}px`,
            left: `${-(this.dotWidthVal - this.width) / 2}px`,
          }
        : {
            width: `${this.dotWidthVal}px`,
            height: `${this.dotHeightVal}px`,
            top: `${-(this.dotHeightVal - this.height) / 2}px`,
          };
    },
    piecewiseDotStyle() {
      return this.direction === "vertical"
        ? {
            width: `${this.width}px`,
            height: `${this.width}px`,
          }
        : {
            width: `${this.height}px`,
            height: `${this.height}px`,
          };
    },
    piecewiseDotWrap() {
      if (!this.piecewise && !this.piecewiseLabel) {
        return false;
      }

      const arr = [];
      for (let i = 0; i <= this.total; i++) {
        const style =
          this.direction === "vertical"
            ? {
                bottom: `${this.gap * i - this.width / 2}px`,
                left: 0,
              }
            : {
                left: `${this.gap * i - this.height / 2}px`,
                top: 0,
              };
        const index = this.reverse ? this.total - i : i;
        const label = this.data
          ? this.data[index]
          : this.spacing * index + this.min;
        arr.push({
          style,
          label: this.formatter ? this.formatting(label) : label,
          inRange: index >= this.indexRange[0] && index <= this.indexRange[1],
        });
      }
      return arr;
    },
  },
  watch: {
    value(val) {
      this.flag || this.setValue(val, true);
    },
    max(val) {
      if (val < this.min) {
        return this.printError(
          "The maximum value can not be less than the minimum value."
        );
      }

      const resetVal = this.limitValue(this.val);
      this.setValue(resetVal);
      this.refresh();
    },
    min(val) {
      if (val > this.max) {
        return this.printError(
          "The minimum value can not be greater than the maximum value."
        );
      }

      const resetVal = this.limitValue(this.val);
      this.setValue(resetVal);
      this.refresh();
    },
    show(bool) {
      if (bool && !this.size) {
        this.$nextTick(() => {
          this.refresh();
        });
      }
    },
    fixed() {
      this.computedFixedValue();
    },
  },
  mounted() {
    this.isComponentExists = true;

    if (typeof window === "undefined" || typeof document === "undefined") {
      this.printError(
        "window or document is undefined, can not be initialization."
      );
    }

    this.$nextTick(() => {
      if (this.isComponentExists) {
        this.getStaticData();
        this.setValue(this.limitValue(this.value), true, 0);
        this.bindEvents();
      }
    });
  },
  beforeDestroy() {
    this.isComponentExists = false;
    this.unbindEvents();
  },
  methods: {
    bindEvents() {
      document.addEventListener("touchmove", this.moving, { passive: false });
      document.addEventListener("touchend", this.moveEnd, { passive: false });
      document.addEventListener("mousedown", this.blurSlider);
      document.addEventListener("mousemove", this.moving);
      document.addEventListener("mouseup", this.moveEnd);
      document.addEventListener("mouseleave", this.moveEnd);
      document.addEventListener("keydown", this.handleKeydown);
      document.addEventListener("keyup", this.handleKeyup);
      window.addEventListener("resize", this.refresh);
    },
    unbindEvents() {
      document.removeEventListener("touchmove", this.moving);
      document.removeEventListener("touchend", this.moveEnd);
      document.removeEventListener("mousedown", this.blurSlider);
      document.removeEventListener("mousemove", this.moving);
      document.removeEventListener("mouseup", this.moveEnd);
      document.removeEventListener("mouseleave", this.moveEnd);
      document.removeEventListener("keydown", this.handleKeydown);
      document.removeEventListener("keyup", this.handleKeyup);
      window.removeEventListener("resize", this.refresh);
    },
    handleKeydown(e) {
      if (!this.useKeyboard || !this.focusFlag) {
        return false;
      }
      switch (e.keyCode) {
        case 37:
        case 40:
          e.preventDefault();
          this.keydownFlag = true;
          this.flag = true;
          this.changeFocusSlider(this.actionsKeyboard[0]);
          break;
        case 38:
        case 39:
          e.preventDefault();
          this.keydownFlag = true;
          this.flag = true;
          this.changeFocusSlider(this.actionsKeyboard[1]);
          break;
      }
    },
    handleKeyup() {
      if (this.keydownFlag) {
        this.keydownFlag = false;
        this.flag = false;
      }
    },
    changeFocusSlider(fn) {
      if (this.isRange) {
        let arr = this.currentIndex.map((index, i) => {
          if (i === this.focusSlider || this.fixed) {
            const val = fn(index);
            const range = this.fixed
              ? this.valueLimit[i]
              : [this.minimum, this.maximum];
            if (val <= range[1] && val >= range[0]) {
              return val;
            }
          }
          return index;
        });
        if (arr[0] > arr[1]) {
          this.focusSlider = this.focusSlider === 0 ? 1 : 0;
          arr = arr.reverse();
        }
        this.setIndex(arr);
      } else {
        this.setIndex(fn(this.currentIndex));
      }
    },
    blurSlider(e) {
      const dot = this.isRange
        ? this.$refs[`dot${this.focusSlider}`]
        : this.$refs.dot;
      if (!dot || dot === e.target) {
        return false;
      }
      this.focusFlag = false;
    },
    formatting(value) {
      return typeof this.formatter === "string"
        ? this.formatter.replace(/\{value\}/, value)
        : this.formatter(value);
    },
    getPos(e) {
      this.realTime && this.getStaticData();
      return this.direction === "vertical"
        ? this.reverse
          ? e.pageY - this.offset
          : this.size - (e.pageY - this.offset)
        : this.reverse
        ? this.size - (e.clientX - this.offset)
        : e.clientX - this.offset;
    },
    processClick(e) {
      if (this.fixed) {
        e.stopPropagation();
      }
    },
    wrapClick(e) {
      if (this.isDisabled || !this.clickable || this.processFlag) return false;
      const pos = this.getPos(e);
      if (this.isRange) {
        this.currentSlider =
          pos > (this.position[1] - this.position[0]) / 2 + this.position[0]
            ? 1
            : 0;
      }
      this.setValueOnPos(pos);
    },
    moveStart(e, index = 0, isProcess) {
      if (this.isDisabled) {
        return false;
      }
      if (this.stopPropagation) {
        e.stopPropagation();
      }
      if (this.isRange) {
        this.currentSlider = index;

        if (isProcess) {
          if (!this.processDragable) {
            return false;
          }
          this.processFlag = true;
          this.processSign = {
            pos: this.position,
            start: this.getPos(
              e.targetTouches && e.targetTouches[0] ? e.targetTouches[0] : e
            ),
          };
        }
      }
      if (!isProcess && this.useKeyboard) {
        this.focusFlag = true;
        this.focusSlider = index;
      }
      this.flag = true;
      this.$emit("drag-start", this);
    },
    moving(e) {
      if (this.stopPropagation) {
        e.stopPropagation();
      }

      if (!this.flag) return false;
      e.preventDefault();

      if (e.targetTouches && e.targetTouches[0]) e = e.targetTouches[0];
      if (this.processFlag) {
        this.currentSlider = 0;
        this.setValueOnPos(
          this.processSign.pos[0] + this.getPos(e) - this.processSign.start,
          true
        );
        this.currentSlider = 1;
        this.setValueOnPos(
          this.processSign.pos[1] + this.getPos(e) - this.processSign.start,
          true
        );
      } else {
        this.setValueOnPos(this.getPos(e), true);
      }
    },
    moveEnd(e) {
      if (this.stopPropagation) {
        e.stopPropagation();
      }
      if (this.flag) {
        this.$emit("drag-end", this);
        if (this.lazy && this.isDiff(this.val, this.value)) {
          this.syncValue();
        }
      } else {
        return false;
      }
      this.flag = false;
      window.setTimeout(() => {
        this.processFlag = false;
      }, 0);
      this.setPosition();
    },
    setValueOnPos(pos, isDrag) {
      const range = this.isRange ? this.limit[this.currentSlider] : this.limit;
      const valueRange = this.isRange
        ? this.valueLimit[this.currentSlider]
        : this.valueLimit;
      if (pos >= range[0] && pos <= range[1]) {
        this.setTransform(pos);
        const v = this.getValueByIndex(Math.round(pos / this.gap));
        this.setCurrentValue(v, isDrag);
        if (this.isRange && this.fixed) {
          this.setTransform(
            pos +
              this.fixedValue * this.gap * (this.currentSlider === 0 ? 1 : -1),
            true
          );
          this.setCurrentValue(
            v +
              this.fixedValue *
                this.spacing *
                (this.currentSlider === 0 ? 1 : -1),
            isDrag,
            true
          );
        }
      } else if (pos < range[0]) {
        this.setTransform(range[0]);
        this.setCurrentValue(valueRange[0]);
        if (this.isRange && this.fixed) {
          this.setTransform(this.limit[this.idleSlider][0], true);
          this.setCurrentValue(
            this.valueLimit[this.idleSlider][0],
            isDrag,
            true
          );
        } else if (!this.fixed && this.currentSlider === 1) {
          this.focusSlider = 0;
          this.currentSlider = 0;
        }
      } else {
        this.setTransform(range[1]);
        this.setCurrentValue(valueRange[1]);
        if (this.isRange && this.fixed) {
          this.setTransform(this.limit[this.idleSlider][1], true);
          this.setCurrentValue(
            this.valueLimit[this.idleSlider][1],
            isDrag,
            true
          );
        } else if (!this.fixed && this.currentSlider === 0) {
          this.focusSlider = 1;
          this.currentSlider = 1;
        }
      }
    },
    isDiff(a, b) {
      if (
        Object.prototype.toString.call(a) !== Object.prototype.toString.call(b)
      ) {
        return true;
      }
      if (Array.isArray(a) && a.length === b.length) {
        return a.some((v, i) => v !== b[i]);
      }
      return a !== b;
    },
    setCurrentValue(val, bool, isIdleSlider) {
      const slider = isIdleSlider ? this.idleSlider : this.currentSlider;
      if (val < this.minimum || val > this.maximum) return false;
      if (this.isRange) {
        if (this.isDiff(this.currentValue[slider], val)) {
          this.currentValue.splice(slider, 1, val);
          if (!this.lazy || !this.flag) {
            this.syncValue();
          }
        }
      } else if (this.isDiff(this.currentValue, val)) {
        this.currentValue = val;
        if (!this.lazy || !this.flag) {
          this.syncValue();
        }
      }
      bool || this.setPosition();
    },
    getValueByIndex(index) {
      return (
        (this.spacing * this.multiple * index + this.minimum * this.multiple) /
        this.multiple
      );
    },
    getIndexByValue(value) {
      return (
        ((value - this.minimum) * this.multiple) /
        (this.spacing * this.multiple)
      );
    },
    setIndex(val) {
      if (Array.isArray(val) && this.isRange) {
        let value;
        if (this.data) {
          value = [this.data[val[0]], this.data[val[1]]];
        } else {
          value = [this.getValueByIndex(val[0]), this.getValueByIndex(val[1])];
        }
        this.setValue(value);
      } else {
        val = this.getValueByIndex(val);
        if (this.isRange) {
          this.currentSlider =
            val >
            (this.currentValue[1] - this.currentValue[0]) / 2 +
              this.currentValue[0]
              ? 1
              : 0;
        }
        this.setCurrentValue(val);
      }
    },
    setValue(val, noCb, speed) {
      if (this.isDiff(this.val, val)) {
        const resetVal = this.limitValue(val);
        this.val = this.isRange ? resetVal.concat() : resetVal;
        this.computedFixedValue();
        this.syncValue(noCb);
      }

      this.$nextTick(() => this.setPosition(speed));
    },
    computedFixedValue() {
      if (!this.fixed) {
        this.fixedValue = 0;
        return false;
      }

      this.fixedValue = this.currentIndex[1] - this.currentIndex[0];
    },
    setPosition(speed) {
      this.flag ||
        this.setTransitionTime(speed === undefined ? this.speed : speed);
      if (this.isRange) {
        this.setTransform(this.position[0], this.currentSlider === 1);
        this.setTransform(this.position[1], this.currentSlider === 0);
      } else {
        this.setTransform(this.position);
      }
      this.flag || this.setTransitionTime(0);
    },
    setTransform(val, isIdleSlider) {
      const slider = isIdleSlider ? this.idleSlider : this.currentSlider;
      const value = roundToDPR(
        (this.direction === "vertical"
          ? this.dotHeightVal / 2 - val
          : val - this.dotWidthVal / 2) * (this.reverse ? -1 : 1)
      );
      const translateValue =
        this.direction === "vertical"
          ? `translateY(${value}px)`
          : `translateX(${value}px)`;
      const processSize = this.fixed
        ? `${this.fixedValue * this.gap}px`
        : `${slider === 0 ? this.position[1] - val : val - this.position[0]}px`;
      const processPos = this.fixed
        ? `${slider === 0 ? val : val - this.fixedValue * this.gap}px`
        : `${slider === 0 ? val : this.position[0]}px`;
      if (this.isRange) {
        this.slider[slider].style.transform = translateValue;
        this.slider[slider].style.WebkitTransform = translateValue;
        this.slider[slider].style.msTransform = translateValue;
        if (this.direction === "vertical") {
          this.$refs.process.style.height = processSize;
          this.$refs.process.style[this.reverse ? "top" : "bottom"] =
            processPos;
        } else {
          this.$refs.process.style.width = processSize;
          this.$refs.process.style[this.reverse ? "right" : "left"] =
            processPos;
        }
      } else {
        this.slider.style.transform = translateValue;
        this.slider.style.WebkitTransform = translateValue;
        this.slider.style.msTransform = translateValue;
        if (this.direction === "vertical") {
          this.$refs.process.style.height = `${val}px`;
          this.$refs.process.style[this.reverse ? "top" : "bottom"] = 0;
        } else {
          this.$refs.process.style.width = `${val}px`;
          this.$refs.process.style[this.reverse ? "right" : "left"] = 0;
        }
      }
    },
    setTransitionTime(time) {
      // In order to avoid browser merge style and modify together
      time || this.$refs.process.offsetWidth;

      if (this.isRange) {
        for (let i = 0; i < this.slider.length; i++) {
          this.slider[i].style.transitionDuration = `${time}s`;
          this.slider[i].style.WebkitTransitionDuration = `${time}s`;
        }
        this.$refs.process.style.transitionDuration = `${time}s`;
        this.$refs.process.style.WebkitTransitionDuration = `${time}s`;
      } else {
        this.slider.style.transitionDuration = `${time}s`;
        this.slider.style.WebkitTransitionDuration = `${time}s`;
        this.$refs.process.style.transitionDuration = `${time}s`;
        this.$refs.process.style.WebkitTransitionDuration = `${time}s`;
      }
    },
    limitValue(val) {
      if (this.data) {
        return val;
      }

      const inRange = (v) => {
        if (v < this.min) {
          this.printError(
            `The value of the slider is ${val}, the minimum value is ${this.min}, the value of this slider can not be less than the minimum value`
          );
          return this.min;
        }
        if (v > this.max) {
          this.printError(
            `The value of the slider is ${val}, the maximum value is ${this.max}, the value of this slider can not be greater than the maximum value`
          );
          return this.max;
        }
        return v;
      };

      if (this.isRange) {
        return val.map((v) => inRange(v));
      }
      return inRange(val);
    },
    syncValue(noCb) {
      const val = this.isRange ? this.val.concat() : this.val;
      this.$emit("input", val);
      noCb || this.$emit("callback", val);
    },
    getValue() {
      return this.val;
    },
    getIndex() {
      return this.currentIndex;
    },
    getStaticData() {
      if (this.$refs.elem) {
        this.size =
          this.direction === "vertical"
            ? this.$refs.elem.offsetHeight
            : this.$refs.elem.offsetWidth;
        this.offset =
          this.direction === "vertical"
            ? this.$refs.elem.getBoundingClientRect().top +
                window.pageYOffset || document.documentElement.scrollTop
            : this.$refs.elem.getBoundingClientRect().left;
      }
    },
    refresh() {
      if (this.$refs.elem) {
        this.getStaticData();
        this.computedFixedValue();
        this.setPosition();
      }
    },
    printError(msg) {
      if (this.debug) {
        console.error(`[VueSlider error]: ${msg}`);
      }
    },
  },
};
</script>

<style lang="scss" scoped>
.vue-slider-component {
  position: relative;
  box-sizing: border-box;
  user-select: none;
  -webkit-user-select: none;
  -moz-user-select: none;
  -o-user-select: none;
  padding: 0;
  &.vue-slider-disabled {
    .vue-slider-dot {
      background: $line-light-color;
      border: 0;
      box-shadow: none;
    }
  }
}

.vue-slider-component.vue-slider-disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.vue-slider-component.vue-slider-has-label {
  margin-bottom: 15px;
}

.vue-slider-component.vue-slider-disabled .vue-slider-dot {
  cursor: not-allowed;
}

.vue-slider-component .vue-slider {
  position: relative;
  display: block;
  border-radius: 15px;
  background-color: $line-smooth-color;
  border-radius: 3px;
}

.vue-slider-component .vue-slider::after {
  content: "";
  position: absolute;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
  z-index: 2;
}

.vue-slider-component .vue-slider-process {
  position: absolute;
  border-radius: 15px;
  background-color: #3b3269;
  transition: all 0s;
  z-index: 1;
}

.vue-slider-component .vue-slider-process.vue-slider-process-dragable {
  cursor: pointer;
  z-index: 3;
}

.vue-slider-component.vue-slider-horizontal .vue-slider-process {
  width: 0;
  height: 100%;
  top: 0;
  left: 0;
  will-change: width;
}

.vue-slider-component.vue-slider-vertical .vue-slider-process {
  width: 100%;
  height: 0;
  bottom: 0;
  left: 0;
  will-change: height;
}

.vue-slider-component.vue-slider-horizontal-reverse .vue-slider-process {
  width: 0;
  height: 100%;
  top: 0;
  right: 0;
}

.vue-slider-component.vue-slider-vertical-reverse .vue-slider-process {
  width: 100%;
  height: 0;
  top: 0;
  left: 0;
}

.vue-slider-component .vue-slider-dot {
  position: absolute;
  border-radius: 50%;
  border: 1px solid $secondary-color;
  background-color: #fff;
  transition: all 0s;
  will-change: transform;
  cursor: pointer;
  z-index: 4;
}

.vue-slider-component .vue-slider-dot.vue-slider-dot-dragging {
  z-index: 5;
}

.vue-slider-component.vue-slider-horizontal .vue-slider-dot {
  left: 0;
}

.vue-slider-component.vue-slider-vertical .vue-slider-dot {
  bottom: 0;
}

.vue-slider-component.vue-slider-horizontal-reverse .vue-slider-dot {
  right: 0;
}

.vue-slider-component.vue-slider-vertical-reverse .vue-slider-dot {
  top: 0;
}

.vue-slider-component .vue-slider-tooltip-wrap {
  display: none;
  position: absolute;
  z-index: 9;
}

.vue-slider-component .vue-slider-tooltip {
  display: none;
}

.vue-slider-component
  .vue-slider-dot.vue-slider-hover:hover
  .vue-slider-tooltip-wrap {
  display: block;
}

.vue-slider-component
  .vue-slider-dot.vue-slider-always
  .vue-slider-tooltip-wrap {
  display: block !important;
}

.vue-slider-component .vue-slider-piecewise {
  position: absolute;
  width: 100%;
  padding: 0;
  margin: 0;
  left: 0;
  top: 0;
  height: 100%;
  list-style: none;
}

.vue-slider-component .vue-slider-piecewise-item {
  position: absolute;
  width: 8px;
  height: 8px;
}

.vue-slider-component .vue-slider-piecewise-dot {
  @include absoluteCenter;
  width: 100%;
  height: 100%;
  display: inline-block;
  background-color: rgba(0, 0, 0, 0.16);
  border-radius: 50%;
  z-index: 2;
  transition: all 0.3s;
}

.vue-slider-component
  .vue-slider-piecewise-item:first-child
  .vue-slider-piecewise-dot,
.vue-slider-component
  .vue-slider-piecewise-item:last-child
  .vue-slider-piecewise-dot {
  visibility: hidden;
}

.vue-slider-component.vue-slider-horizontal .vue-slider-piecewise-label,
.vue-slider-component.vue-slider-horizontal-reverse
  .vue-slider-piecewise-label {
  position: absolute;
  display: inline-block;
  top: 100%;
  left: 50%;
  white-space: nowrap;
  font-size: 12px;
  color: #333;
  transform: translate(-50%, 8px);
  visibility: visible;
}

.vue-slider-component.vue-slider-vertical .vue-slider-piecewise-label,
.vue-slider-component.vue-slider-vertical-reverse .vue-slider-piecewise-label {
  position: absolute;
  display: inline-block;
  top: 50%;
  left: 100%;
  white-space: nowrap;
  font-size: 12px;
  color: #333;
  transform: translate(8px, -50%);
  visibility: visible;
}

.vue-slider-component .vue-slider-sr-only {
  clip: rect(1px, 1px, 1px, 1px);
  height: 1px;
  width: 1px;
  overflow: hidden;
  position: absolute !important;
}

.vue-slider {
  .filter & {
    background: $line-smooth-color;
    border-radius: 3px;
    margin-top: -12px;
  }
}

.vue-slider-dot {
  .filter & {
    border: 1px solid $secondary-color;
    &:before {
      content: "";
      @include absoluteCenter;
      height: 7px;
      width: 7px;
      border-left: 1px solid $secondary-color;
      border-right: 1px solid $secondary-color;
    }
    &:after {
      content: "";
      @include absoluteCenter;
      height: 7px;
      width: 1px;
      background: $secondary-color;
    }
  }
}

.vue-slider-process {
  .filter & {
    background: $line-smooth-color;
    border-radius: 3px;
  }
}
</style>
