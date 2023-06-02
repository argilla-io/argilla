<template>
  <div class="wrapper">
    <div class="title-area --body2">
      <span v-text="title" v-optional-field="isRequired ? false : true" />

      <BaseIconWithBadge
        class="icon-info"
        v-if="!!tooltipMessage"
        icon="info"
        :id="`${title}Rating`"
        :show-badge="false"
        iconColor="#acacac"
        badge-vertical-position="top"
        badge-horizontal-position="right"
        badge-border-color="white"
        v-tooltip="{ content: tooltipMessage, backgroundColor: '#FFF' }"
      />
    </div>

    <SingleLabelSelectionComponent
      :options="uniqueOptions"
      :componentId="questionId"
      :showSearch="showSearch"
      :maxOptionsToShowBeforeCollapse="maxOptionsToShowBeforeCollapse"
      @change="$emit('update:options', options)"
    />
  </div>
</template>

<script>
export default {
  name: "SingleLabelComponent",
  props: {
    questionId: {
      type: String,
      required: true,
    },
    title: {
      type: String,
      required: true,
    },
    options: {
      type: Array,
      required: true,
    },
    isRequired: {
      type: Boolean,
      default: () => false,
    },
    tooltipMessage: {
      type: String,
      default: () => "",
    },
    visibleOptions: {
      type: Number | null,
      required: false,
    },
  },
  model: {
    prop: "options",
  },
  data() {
    return {
      uniqueOptions: [],
    };
  },
  beforeMount() {
    this.uniqueOptions = this.options.reduce((accumulator, current) => {
      if (!accumulator.find((item) => item.id === current.id)) {
        accumulator.push(current);
      }
      return accumulator;
    }, []);
  },
  computed: {
    showSearch() {
      return this.uniqueOptions.length >= 12;
    },
    maxOptionsToShowBeforeCollapse() {
      return this.visibleOptions ?? -1;
    },
  },
};
</script>

<style lang="scss" scoped>
.wrapper {
  display: flex;
  flex-direction: column;
  gap: 12px;
  .title-area {
    color: $black-87;
    font-weight: 500;
  }
}

.icon {
  color: $black-37;
}

.info-icon {
  display: flex;
  flex-basis: 37px;
}

span {
  word-break: break-word;
}

.icon-info {
  display: inline-flex;
  margin: 0;
  padding: 0;
  overflow: inherit;
  &[data-title] {
    position: relative;
    overflow: visible;
    &:before,
    &:after {
      margin-top: 0;
    }
  }
}
</style>
