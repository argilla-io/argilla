<template>
  <div class="share" @click.stop="">
    <BaseActionTooltip
      :tooltip="$t('copiedToClipboard')"
      tooltipPosition="down"
      @click.stop="copyOnClipboard"
    >
      <BaseButton
        :title="$t('button.tooltip.copyToClipboard')"
        @mouseover="openDialog"
        @mouseleave="closeDialog"
      >
        Share
      </BaseButton>
    </BaseActionTooltip>
    <transition name="fade" appear>
      <dialog
        v-if="isDialogOpen"
        class="share__dialog"
        v-click-outside="closeDialog"
      >
        <div>
          <img :src="imageLink" />
          <p class="share__link" v-text="imageLink" />
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
.share {
  z-index: 2;
  margin-left: auto;
  margin-right: 0;

  &__dialog {
    position: absolute;
    right: 1em;
    left: auto;
    width: auto;
    min-width: 360px;
    max-width: 360px;
    bottom: calc(100% + $base-space + 2px);
    display: block;
    padding: $base-space * 2;
    border: 1px solid var(--bg-opacity-10);
    border-radius: $border-radius-m;
    box-shadow: $shadow;
    z-index: 2;
  }

  &__link {
    width: 95%;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
    font-size: 10px;
    color: var(--fg-secondary);
  }
}
</style>
