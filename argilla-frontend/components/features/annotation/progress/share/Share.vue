<template>
  <div class="share" @click.stop="copyOnClipboard">
    <BaseActionTooltip :tooltip="$t('copiedToClipboard')">
      <BaseButton
        class="share__button"
        :title="$t('button.tooltip.copyToClipboard')"
        @mouseover="openDialog"
        @mouseleave="closeDialog"
      >
        <svgicon class="share__icon" name="link" width="14" height="14" />
        {{ $t("share") }}
      </BaseButton>
    </BaseActionTooltip>
    <transition name="fade" appear>
      <dialog
        v-if="isDialogOpen"
        class="share__dialog"
        v-click-outside="closeDialog"
      >
        <div class="share__dialog--container">
          <BaseSpinner v-if="!sharingImage.loaded" :size="20" />
          <img v-else :src="sharingImage.src" />
        </div>
      </dialog>
    </transition>
  </div>
</template>
<script>
import { useShareViewModel } from "./useShareViewModel";

export default {
  setup() {
    return useShareViewModel();
  },
};
</script>

<style lang="scss" scoped>
$bullet-size: 8px;
.share {
  z-index: 2;
  margin-left: auto;
  margin-right: 0;

  &__dialog {
    position: absolute;
    right: 1em;
    left: auto;
    width: auto;
    height: 204px;
    min-width: 360px;
    max-width: 360px;
    bottom: calc(100% + $base-space + 2px);
    display: block;
    padding: $base-space * 2;
    border: 1px solid var(--bg-opacity-10);
    border-radius: $border-radius-m;
    box-shadow: $shadow;
    z-index: 2;

    &--container {
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100%;
    }
  }

  &__button {
    @include font-size(12px);
    height: 24px;
    padding: $base-space;
    background: var(--bg-opacity-3);
    border-radius: $border-radius;
  }

  &__icon {
    padding: 0;
    flex-shrink: 0;
  }
}
</style>
