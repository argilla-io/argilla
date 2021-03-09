<template>
  <div>
    <LabelPill class="predictions" :labels="labels" :showConfidence="true"/>
  </div>
</template>
<script>
import "assets/icons/ignore";

export default {
  props: {
    labels: {
      type: Array,
      required: true,
    },
  },
  data: () => ({
    searchText: undefined,
    componentLabels: undefined,
    maxLabelsShown: 1,
    selectedLabel: undefined,
    dropdownLabels: undefined,
  }),
  computed: {
    dropdownLabelSelected() {
      let [selectedLabel] = this.labels
        .slice(this.maxLabelsShown)
        .filter((label) => label.class === this.selectedLabel);
      return selectedLabel || false;
    },
  },
  methods: {
    decorateConfidence(confidence) {
      return confidence * 100;
    },
  },
};
</script>
<style lang="scss" scoped>
// @import "@recognai/re-commons/src/assets/scss/components/tooltip.scss";
.feedback-interactions {
  margin: 1.5em auto 0 auto;
  padding-right: 0;
  &__items {
    display: flex;
    flex-flow: wrap;
    margin-left: -1%;
    margin-right: -1%;
    & > * {
      // flex-basis: 31%;
      width: 30%;
      min-width: 225px;
      flex-grow: 0;
      flex-shrink: 0;
      margin-left: 1% !important;
      margin-right: 1% !important;
      max-width: 240px;
    }
  }
}
::v-deep .dropdown__header {
  border: 1px solid $line-smooth-color;
  margin: auto auto 20px auto;
  width: auto;
  height: 42px;
  line-height: 42px;
  @include font-size(14px);
  padding-left: 0.5em;
  font-weight: 600;
}
::v-deep .dropdown__content {
  max-height: 280px;
  overflow: scroll;
}
.select--label {
  ::v-deep .--checked {
    color: $lighter-color;
    font-weight: 600;
    text-transform: none;
    display: flex;
    width: calc(100% - 1em);
    span:first-child {
      width: 112px;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    span:last-child {
      margin-left: 5px;
    }
  }
  &.checked ::v-deep {
    .dropdown__header {
      background: palette(green, highlight);
      border: 0;
      margin: auto auto 20px auto;
      border: 1px solid $line-light-color;
      border-radius: 5px;
      transition: all 0.3s ease;
      max-width: 240px;
      &:after {
        border-color: $lighter-color;
      }
    }
  }
}
</style>
