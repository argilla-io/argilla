<template>
  <div
    class="rules-metric-token"
    :class="`rules-metric-token--${rulesMetricType}`"
    :style="cssVars"
  >
    <h2 class="rules-metric-token__title">{{ title }}</h2>
    <div class="rules-metric-token__metrics" v-if="subcardInputs">
      <div
        class="subcard"
        v-for="{ id, label, mainValue, subValue, tooltip } in subcardInputs"
        :key="id"
      >
        <TooltipComponent
          :message="tooltip.tooltipMessage"
          :direction="tooltip.tooltipDirection"
        >
          <h3 class="rules-metric-token__subtitle">
            {{ label }}
          </h3>
        </TooltipComponent>
        <span class="subcard__items"> {{ mainValue }}</span>
        <span class="subcard__items"> {{ subValue }}</span>
      </div>
    </div>
  </div>
</template>

<script>
import TooltipComponent from "@/components/base/tooltip/Tooltip.component.vue";
export default {
  name: "RulesMetricsToken",
  components: {
    TooltipComponent,
  },
  props: {
    title: {
      type: String,
      required: true,
    },
    subcardInputs: {
      type: Array,
      required: true,
    },
    numberOfColumns: {
      type: Number,
      default: () => 2,
    },
    rulesMetricType: {
      type: String,
      default: "info",
      validator: (value) => ["info", "warning", "error"].includes(value),
    },
    btnLabel: {
      type: String,
    },
  },
  computed: {
    numberOfSubcard() {
      return this.subcardInputs.length;
    },
    numberOfRows() {
      return Math.round(this.numberOfSubcard / this.numberOfColumns);
    },
    cssVars() {
      return {
        "--number-of-rows": this.numberOfRows,
        "--number-of-columns": this.numberOfColumns,
      };
    },
  },
};
</script>

<style lang="scss" scoped>
.rules-metric-token {
  $this: &;
  display: flex;
  flex-direction: column;
  flex-basis: 30em;
  padding: 2em;
  gap: 1em;
  border-radius: 10px;
  border-width: 1px;
  border-style: solid;
  &__title {
    padding-bottom: 0;
    margin-top: 0;
    @include font-size(22px);
    line-height: 22px;
    font-weight: 600;
  }
  &__subtitle {
    font-weight: 400;
    margin-bottom: 0.2em;
    display: inline-flex;
  }
  &__metrics {
    display: grid;
    grid-gap: 10px;
    grid-template-columns: repeat(var(--number-of-columns), 1fr);
    grid-template-rows: repeat(var(--number-of-rows), 7em);
    .subcard {
      display: flex;
      flex-direction: column;
      border-radius: 10px;
      gap: 5px;
      color: var(--text-subcard-color);
      .subcard__items {
        &:nth-child(1) {
          font-weight: lighter;
          margin-bottom: 0;
        }
        &:nth-child(2) {
          @include font-size(20px);
          font-weight: bold;
          font-weight: 600;
        }
      }
    }
  }
  // info type of card
  &--info {
    background: $black-4;
    color: $black-54;
    border-color: $black-4;
    border-radius: $border-radius-m;
    #{$this}__title {
      padding-bottom: 0;
      @include font-size(18px);
      margin-top: 0;
    }
    #{$this}__subtitle {
      @include font-size(14px);
      color: $black-37;
    }
    .subcard__items {
      &:nth-child(1) {
        color: $black-37;
      }
    }
  }
}
</style>
