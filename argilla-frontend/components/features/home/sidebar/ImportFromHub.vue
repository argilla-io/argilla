<template>
  <div class="import-from-hub" :class="isExpanded ? '--expanded' : null">
    <BaseButton
      class="import-from-hub__button"
      @click="$emit('on-expand')"
      v-if="!isExpanded"
      ><svgicon
        class="import-from-hub__button__icon"
        name="link"
        width="18"
        height="18"
        color="#F6C000"
      ></svgicon
      >{{ $t("home.importFromHub") }}</BaseButton
    >
    <template v-else>
      <BaseButton
        class="import-from-hub__close-button"
        @click="$emit('on-close')"
      >
        <svgicon name="close" width="8"></svgicon>Close</BaseButton
      >
      <form @submit.prevent="$emit('on-import-dataset', repositoryId)">
        <transition name="slide-right" appear>
          <BaseInputContainer class="import-from-hub__input">
            <svgicon
              class="import-from-hub__button__icon"
              name="link"
              width="20"
              height="20"
            ></svgicon>
            <BaseInput v-model="repositoryId" placeholder="Repository ID" />
            <BaseButton
              :disabled="!repositoryId"
              class="secondary import-from-hub__button-submit"
              type="submit"
            >
              <svgicon name="chevron-right" width="16"></svgicon
            ></BaseButton>
          </BaseInputContainer>
        </transition>
      </form>
    </template>
  </div>
</template>

<script>
import "assets/icons/link";
import "assets/icons/chevron-right";
export default {
  props: {
    isExpanded: {
      type: Boolean,
    },
  },
  data() {
    return {
      repositoryId: "argilla/FinePersonas-v0.1",
    };
  },
};
</script>

<style lang="scss" scoped>
.import-from-hub {
  &.--expanded {
    width: 100%;
  }
  &__button.button {
    min-height: 42px;
    color: var(--fg-primary);
    background: linear-gradient(
      177.33deg,
      var(--bg-accent-grey-5) 20%,
      var(--bg-opacity-4) 100%
    );
    box-shadow: 0 0 0 1px var(--bg-opacity-10);
    &:hover {
      background: linear-gradient(
        177.33deg,
        var(--bg-accent-grey-5) 20%,
        var(--bg-opacity-2) 100%
      );
    }
  }
  &__input {
    display: flex;
    align-items: center;
    min-height: 42px;
    gap: $base-space * 2;
    padding: 0 calc($base-space / 2) 0 $base-space * 2;
    width: 100%;
    background: var(--bg-accent-grey-2);
    border-radius: $border-radius;
    box-shadow: 0 0 0 1px var(--bg-opacity-10);
    &.re-has-value:focus-within {
      box-shadow: 0 0 0 1px var(--fg-cuaternary);
      .import-from-hub__button__icon {
        fill: var(--fg-secondary);
      }
      .button {
        background: var(--bg-action);
        * {
          fill: var(--color-white);
        }
      }
    }
    input {
      color: var(--fg-secondary);
      @include input-placeholder {
        color: var(--fg-tertiary);
      }
    }
  }
  &__button {
    &__icon {
      fill: hsl(47, 100%, 48%);
    }
  }
  &__close-button.button {
    margin-left: auto;
    margin-top: -$base-space * 2;
    padding: calc($base-space / 2);
    @include font-size(12px);
  }
  &__button-submit.button {
    padding: $base-space;
  }
}
.slide-right-enter-active,
.slide-right-leave-active {
  transition: transform 0.3s;
}
.slide-right-enter,
.slide-right-leave-to {
  transform: translateX(50px);
}
</style>
