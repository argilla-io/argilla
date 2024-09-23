<template>
  <transition appear :duration="500" name="animate-progress">
    <div class="progress__wrapper">
      <div class="progress__container">
        <div
          v-for="(range, index) in filteredProgressRanges"
          :key="range.name"
          role="progressbar"
          :class="[
            'progress__range',
            showTooltip ? 'progress__range--with-tooltip' : null,
          ]"
          :style="{
            width: `${getPercentage(range.value)}%`,
            zIndex: filteredProgressRanges.length - index,
          }"
          @mouseenter="hoveredRange = range"
          @mouseleave="hoveredRange = null"
        >
          <div class="progress__bar" :style="{ background: range.color }"></div>
        </div>
      </div>
      <template v-if="showTooltip && !!hoveredRange">
        <span
          class="progress__tooltip__triangle"
          :style="{ left: `${getTrianglePosition(hoveredRange)}%` }"
        />
        <div
          class="progress__tooltip"
          :style="{
            left: tooltipPositionFixed
              ? '50%'
              : `${getTrianglePosition(hoveredRange)}%`,
          }"
        >
          <span class="progress__tooltip__percent-info"
            >{{ hoveredRange.name }}:
            <span v-if="showPercentInTooltip"
              >{{ getPercentage(hoveredRange.value) }}%</span
            >
          </span>
          {{ hoveredRange.tooltip }}
        </div>
      </template>
    </div>
  </transition>
</template>

<script>
export default {
  props: {
    showTooltip: {
      type: Boolean,
      default: false,
    },
    showPercentInTooltip: {
      type: Boolean,
      default: true,
    },
    tooltipPositionFixed: {
      type: Boolean,
      default: true,
    },
    progressMax: {
      type: Number,
      default: 100,
    },
    progressRanges: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      hoveredRange: null,
    };
  },
  computed: {
    filteredProgressRanges() {
      return this.progressRanges.filter((range) => range.value > 0);
    },
  },
  methods: {
    getPercentage(value) {
      return ((value / this.progressMax) * 100).toFixed(2);
    },
    getTrianglePosition(range) {
      if (!range) return;

      return this.getPercentage(
        range.value / 2 + this.getPreviousRangesPercent(range)
      );
    },
    getPreviousRangesPercent(range) {
      return this.filteredProgressRanges
        .slice(0, this.filteredProgressRanges.indexOf(range))
        .reduce((acc, r) => acc + r.value, 0);
    },
  },
};
</script>

<styles lang="scss" scoped>
$progressHeight: 14px;
$tooltipBackgroundColor: var(--bg-solid-grey-3);
$tooltipTriangleSize: 5px;
$borderRadius: 3px;

.progress {
  $this: &;
  &__wrapper {
    position: relative;
  }
  &__container {
    position: relative;
    display: flex;
    width: 100%;
    height: $progressHeight;
    border-radius: $borderRadius;
    overflow: hidden;
    background: var(--bg-solid-grey-3);
    box-shadow: 0 0 0 1px var(--bg-accent-grey-2);
  }
  &__bar {
    position: relative;
    height: 100%;
    border-radius: $borderRadius;
    margin: 0 -1px;
    box-shadow: 0 0 0 1px var(--bg-accent-grey-2);
    z-index: 1;
    &:after {
      content: "";
      opacity: 0;
    }
  }
  &__tooltip {
    position: absolute;
    display: flex;
    justify-content: space-between;
    gap: $base-space;
    white-space: nowrap;
    min-width: 180px;
    bottom: calc(100% + #{$tooltipTriangleSize} + 2px);
    transform: translateX(-50%);
    padding: calc($base-space / 2);
    background: $tooltipBackgroundColor;
    color: var(--fg-secondary);
    border-radius: $border-radius;
    transition: opacity 0.2s 0.2s;
    @include font-size(12px);
    &__percent-info {
      font-weight: 600;
      text-transform: capitalize;
    }
    &__triangle {
      opacity: 1;
      position: absolute;
      bottom: calc(100% - #{$tooltipTriangleSize} + 2px);
      left: 50%;
      transform: translateX(-50%);
      border-width: $tooltipTriangleSize;
      border-style: solid;
      border-color: $tooltipBackgroundColor transparent transparent transparent;
      transition: opacity 0.2s 0.2s;
    }
  }
  &__range {
    &:last-of-type:not(:first-of-type) {
      #{$this}__bar {
        margin: 0;
        border-top-left-radius: 0;
        border-bottom-left-radius: 0;
        box-shadow: none;
        z-index: 0;
      }
    }
  }
}
.animate-progress-enter-active,
.animate-progress-leave-active {
  .progress__range {
    max-width: 0;
  }
}
.animate-progress-enter-to,
.animate-progress-leave-to {
  .progress__range {
    max-width: 100%;
    transition: all 0.5s ease-in-out;
  }
}
</styles>
