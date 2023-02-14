<template>
  <div class="record__actions-buttons">
    <span v-for="{ id, name, active } in mainActions" :key="id">
      <base-button
        :class="[
          !active ? `--selected` : null,
          `record__actions-button--${id}`,
        ]"
        @click="onAction(id)"
      >
        <svgicon :name="id" width="14" height="14" />
        {{ name }}
      </base-button></span
    >
    <div class="record__actions-buttons--secondary">
      <span v-for="{ id, name, active } in secondaryActions" :key="id">
        <base-button
          :disabled="!active"
          :data-title="name"
          :class="`record__actions-button--${id}--secondary`"
          @click="onAction(id)"
        >
          <svgicon :name="id" width="18" height="18" /> </base-button
      ></span>
    </div>
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
    mainActions() {
      return this.allowedActions.filter((action) =>
        ["validate", "discard"].includes(action.id)
      );
    },
    secondaryActions() {
      return this.allowedActions.filter((action) =>
        ["clear", "reset"].includes(action.id)
      );
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
    gap: $base-space;
    align-items: center;
    margin-top: 3em;
    &--secondary {
      display: flex;
      margin-right: 0;
      margin-left: auto;
      gap: $base-space;
    }
  }
  @each $action, $color in $recordActions {
    &__actions-button--#{$action} {
      border: 1px solid $black-10;
      background: palette(grey, 700);
      padding: 7px 8px;
      color: $black-54;
      &--secondary {
        overflow: visible;
        padding: $base-space;
        @extend %has-tooltip--top;
        &[disabled] {
          opacity: 0.3;
        }
        &:hover {
          background: $black-4;
        }
      }
      &:hover {
        background: darken(palette(grey, 700), 5%);
      }

      .svg-icon {
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
    border: 1px solid palette(green);
    background: palette(green);
    color: palette(white);
    line-height: 13px;
    &.--selected {
      border: 1px solid palette(green);
      background: palette(white);
      color: palette(green);
      .svg-icon {
        color: palette(green);
      }
      &:hover {
        background: none;
      }
    }
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
