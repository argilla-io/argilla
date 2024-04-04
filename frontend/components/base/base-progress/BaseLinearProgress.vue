<template>
  <transition appear :duration="500" name="animate-progress">
    <div class="progress__wrapper">
      <div
        v-for="range in filteredProgressRanges"
        :key="range.id"
        role="progressbar"
        :class="[
          'progress__range',
          showTooltip ? 'progress__range--with-tooltip' : null,
        ]"
        :style="{
          width: `${getPercentage(range.value)}%`,
        }"
      >
        <div
          class="progress__bar"
          :style="{ backgroundColor: range.color }"
        ></div>
        <div v-if="showTooltip" class="progress__tooltip">
          <span
            class="progress__tooltip__percent-info"
            v-text="`${range.name}: ${getPercentage(range.value)}%`"
          />
          {{ range.tooltip }}
        </div>
      </div>
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
    progressMax: {
      type: Number,
      default: 100,
    },
    progressRanges: {
      type: Array,
      required: true,
    },
  },
  computed: {
    filteredProgressRanges() {
      return this.progressRanges.filter((range) => range.value > 0);
    },
  },
  methods: {
    getPercentage(value) {
      return ((value / this.progressMax) * 100).toFixed();
    },
  },
};
</script>

<styles lang="scss" scoped>
$progressHeight: 12px;
$progressBackgroundColor: #f2f2f2;
$tooltipBackgroundColor: #f2f2f2;
$tooltipTriangleSize: 5px;
$borderRadius: 10px;

.progress {
  $this: &;
  &__wrapper {
    position: relative;
    display: flex;
    height: $progressHeight;
    background: $progressBackgroundColor;
    border-radius: $borderRadius;
    padding-left: 4px;
  }
  &__bar {
    position: relative;
    height: 100%;
    margin: 0 -4px;
    border-radius: $borderRadius;
    box-shadow: 0 0 0 1px palette(white);
    z-index: 1;
    &:after {
      content: "";
      opacity: 0;
    }
  }
  &__tooltip {
    opacity: 0;
    position: absolute;
    display: flex;
    justify-content: space-between;
    gap: $base-space;
    white-space: nowrap;
    min-width: 100%;
    bottom: calc(100% + #{$tooltipTriangleSize} + 2px);
    left: 50%;
    transform: translateX(-50%);
    padding: 4px;
    background: $tooltipBackgroundColor;
    color: $black-87;
    border-radius: $border-radius;
    transition: opacity 0.2s 0.2s;
    @include font-size(12px);
    &__percent-info {
      font-weight: 600;
    }
  }
  &__range {
    &--with-tooltip {
      &:hover {
        #{$this}__tooltip {
          opacity: 1;
        }
        #{$this}__bar {
          &:after {
            opacity: 1;
            position: absolute;
            bottom: calc(100% - #{$tooltipTriangleSize} + 2px);
            left: 50%;
            transform: translateX(-50%);
            border-width: $tooltipTriangleSize;
            border-style: solid;
            border-color: $tooltipBackgroundColor transparent transparent
              transparent;
            transition: opacity 0.2s 0.2s;
          }
        }
      }
    }
    &:last-of-type {
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
    transition: all 3s ease-in-out;
  }
}
</styles>
