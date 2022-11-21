<template>
  <div class="rules-metric-token" :style="cssVars">
    <h2 class="rule-metrics__title">{{ title }}</h2>
    <div class="rules-metric-token__metrics" v-if="subcardInputs">
      <div
        class="subcard"
        v-for="{ id, label, mainValue, subValue, tooltip } in subcardInputs"
        :key="id"
      >
        <TooltipComponent
          class="title"
          :message="tooltip.tooltipMessage"
          :direction="tooltip.tooltipDirection"
        >
          <h3 class="subcard__items">
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
    backgroundColor: {
      type: String,
      default: () => "#0508D9",
    },
    backgroundSubcardColor: {
      type: String,
      default: function () {
        return this.backgroundColor;
      },
    },
    textColor: {
      type: String,
      default: () => "white",
    },
    textSubcardColor: {
      type: String,
      default: () => "black",
    },
    borderColor: {
      type: String,
      default: () => "black",
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
        "--text-color": this.textColor,
        "--background-color": this.backgroundColor,
        "--text-subcard-color": this.textSubcardColor,
        "--border-color": this.borderColor,
      };
    },
  },
};
</script>

<style lang="scss" scoped>
* {
  margin: inherit;
}

.rules-metric-token {
  display: flex;
  flex-direction: column;
  flex-basis: 30em;
  padding: 2em;
  gap: 3em;
  color: var(--text-color);
  background-color: var(--background-color);
  border-radius: 10px;
  border: 1px solid var(--border-color);
  &__title {
    padding-bottom: 0;
    margin-top: 0;
    @include font-size(22px);
    line-height: 22px;
    font-weight: bold;
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
      .title {
        flex: 1;
      }
      .subcard__items {
        &:first-child {
          font-weight: bold;
          margin-bottom: 0;
          margin: inherit;
        }
        &:nth-child(2) {
          font-weight: bold;
          font-weight: 600;
        }
      }
    }
  }
}
</style>
