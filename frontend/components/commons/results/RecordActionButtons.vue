<template>
  <div class="record__actions-buttons">
    <base-button
      v-for="{ id, name, active } in actions"
      :key="id"
      :class="`record__actions-button--${id}`"
      :disabled="!active"
      @click="onAction(id)"
    >
      <svgicon :name="id" width="22" height="22" />
      {{ name }}
    </base-button>
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
    margin-top: 1.5em;
  }
  @each $action, $color in $recordActions {
    &__actions-button--#{$action} {
      padding: 0;
      color: $color;
      @include font-size(14px);
      &:hover {
        color: darken($color, 10%);
      }
      &:active .svg-icon {
        animation: zoom-in-out 0.2s linear;
      }
      &[disabled] {
        opacity: 30%;
      }
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
