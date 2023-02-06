<template>
  <div class="record__actions-buttons">
    <span v-for="{ id, name, active } in activeActions" :key="id">
      <base-button
        :class="[`record__actions-button--${id}`]"
        @click="onAction(id)"
        :disabled="!active"
      >
        <svgicon :name="id" width="22" height="22" />
        {{ name }}
      </base-button></span
    >
  </div>
</template>

<script>
import "assets/icons/validate";
import "assets/icons/discard";
import "assets/icons/clear";
export default {
  props: {
    actions: {
      type: Array,
      required: true,
      validator(actions) {
        return actions.map((action) =>
          ["validate", "discard", "clear"].includes(action.id)
        );
      },
    },
  },
  computed: {
    activeActions() {
      return this.actions.filter((action) => action.active);
    },
  },
  methods: {
    onAction(id) {
      this.$emit(id);
    },
  },
};
</script>

<style lang="scss" scoped>
$recordActions: (
  validate: palette(green),
  discard: palette(grey, 400),
  clear: palette(blue, 100),
);
.record {
  &__actions-buttons {
    display: flex;
    gap: $base-space * 4;
    align-items: center;
    margin-top: 1.5em;
  }
  @each $action, $color in $recordActions {
    &__actions-button--#{$action} {
      padding: 0;
      color: $color;
      @include font-size(14px);
      &:hover {
        color: darken($color, 10%);
        border-color: darken($color, 10%);
      }
      &:active .svg-icon {
        animation: zoom-in-out 0.2s linear;
      }
    }
  }
  &__actions-button--validate {
    border: 1px solid palette(green);
    line-height: 13px;
    padding: 9px 18px;
  }
}
@keyframes zoom-in-out {
  0% {
    transform: scale(1);
  }
  30% {
    transform: scale(0.8);
  }
  100% {
    transform: scale(1);
  }
}
</style>
