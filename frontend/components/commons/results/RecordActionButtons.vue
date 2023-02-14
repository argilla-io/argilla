<template>
  <div class="record__actions-buttons">
    <span v-for="{ id, name, active } in allowedActions" :key="id">
      <base-button
        :class="`record__actions-button--${id}`"
        @click="onAction(id)"
        :disabled="!active"
      >
        <svgicon :name="id" width="18" height="18" />
        {{ name }}
      </base-button></span
    >
  </div>
</template>

<script>
import "assets/icons/validate";
import "assets/icons/discard";
import "assets/icons/clear";
import "assets/icons/reset";
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
    allowedActions() {
      return this.actions.filter((action) => action.allow);
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
  validate: palette(white),
  discard: $black-37,
  clear: palette(blue, 100),
  reset: #b6b9ff,
);
.record {
  &__actions-buttons {
    display: flex;
    gap: $base-space * 2;
    align-items: center;
    margin-top: 1.5em;
  }
  @each $action, $color in $recordActions {
    &__actions-button--#{$action} {
      border: 1px solid $black-20;
      background: palette(grey, 700);
      padding: 5px 8px;
      color: $black-54;
      &:hover {
        background: palette(grey, 700);
      }
      .svg-icon {
        color: $color;
      }
      &:active .svg-icon {
        animation: zoom-in-out 0.2s linear;
      }
      &[disabled] {
        opacity: 0.3;
      }
    }
  }
  &__actions-button--validate {
    border: 1px solid palette(green);
    background: palette(green);
    color: palette(white);
    line-height: 13px;
    &:hover {
      background: darken(palette(green), 5%);
    }
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
