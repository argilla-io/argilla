<template>
  <div class="record__actions-buttons">
    <span v-for="{ id, name, active, disable } in allowedActions" :key="id">
      <base-button
        :class="`record__actions-button--${id}`"
        @click="onAction(id)"
        :disabled="disable"
        :active="active && !disable"
      >
        <svgicon :name="id" width="14" height="14" />
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
          ["validate", "discard", "clear", "reset"].includes(action.id)
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
  validate: palette(green),
  discard: $black-54,
  clear: $black-54,
  reset: $black-54,
);
.record {
  &__actions-buttons {
    display: flex;
    gap: $base-space;
    align-items: center;
    margin-top: $base-space * 4;
  }
  @each $action, $color in $recordActions {
    &__actions-button--#{$action} {
      border: 1px solid $black-10;
      background: palette(grey, 700);
      padding: 7px 8px;
      color: $black-54;
      &:hover {
        background: darken(palette(grey, 700), 2%);
      }
      .svg-icon {
        flex-shrink: 0;
        color: $color;
      }
      &:active .svg-icon {
        animation: zoom-in-out 0.2s linear;
      }
      &[disabled] {
        opacity: 0.4;
      }
    }
  }
  &__actions-button--validate {
    color: palette(green);
    &[active] {
      border-color: palette(green);
      background: palette(white);
      opacity: 1;
    }
  }
  &__actions-button--discard {
    &[active] {
      background: palette(white);
      opacity: 1;
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
