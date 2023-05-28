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

    <MonoSelectionContainerComponent v-model="options" styleType="style1" />
  </div>
</template>

<script>
export default {
  name: "RatingComponent",
  props: {
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
  },
  model: {
    prop: "options",
    event: "on-change-rating",
  },
  methods: {
    onChangeRating(newOptions) {
      this.$emit("on-change-rating", newOptions);

      const isAnyRatingSelected = this.isAnyRatingSelected(newOptions);
      if (this.isRequired) {
        this.$emit("on-error", !isAnyRatingSelected);
      }
    },
    isAnyRatingSelected(options) {
      return options.some((option) => option.value);
    },
  },
};
</script>

<style lang="scss" scoped>
.wrapper {
  display: flex;
  flex-direction: column;
  gap: $base-space;
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
