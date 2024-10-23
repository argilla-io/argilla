<template>
  <div class="import-from-python" v-click-outside="closeDialog">
    <BaseButton class="import-from-python__button" @click="toggleVisibleSnippet"
      ><svgicon
        class="import-from-python__button__icon"
        name="code"
        width="18"
        height="18"
        color="var(--bg-opacity-87)"
      ></svgicon
      >{{ $t("home.importFromPython") }}</BaseButton
    >
    <transition name="fade" appear>
      <dialog class="import-from-python__dialog" v-if="visibleSnippet">
        <div class="import-from-python__content">
          <BaseActionTooltip
            class="import-from-python__copy-button"
            :tooltip="$t('copied')"
          >
            <a href="#" @click.prevent="copy(snippet)">
              <svgicon
                name="copy"
                width="16"
                height="16"
                color="var(--color-white)"
              />
            </a>
          </BaseActionTooltip>
          <pre><code class="import-from-python__code" language="python" v-highlight>{{ snippet }}</code></pre>
        </div>
      </dialog>
    </transition>
  </div>
</template>

<script>
import { useImportFromPython } from "../sidebar/useImportFromPython";
import "assets/icons/code";
export default {
  data() {
    return {
      visibleSnippet: false,
    };
  },
  methods: {
    toggleVisibleSnippet() {
      this.visibleSnippet = !this.visibleSnippet;
    },
    closeDialog() {
      this.visibleSnippet = false;
    },
    copy(snippet) {
      this.$copyToClipboard(snippet);
    },
  },
  setup() {
    return useImportFromPython();
  },
};
</script>

<style lang="scss" scoped>
.import-from-python {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  &__code {
    border-radius: $border-radius-m;
  }
  &__copy-button {
    position: absolute !important;
    top: $base-space * 3;
    right: $base-space * 3;
  }
  &__dialog {
    position: absolute;
    right: -$base-space * 2;
    top: calc(100% + $base-space);
    left: auto;
    width: 50vw;
    min-width: 400px;
    display: flex;
    flex-direction: column;
    gap: $base-space;
    background: var(--bg-accent-grey-1);
    padding: $base-space * 2;
    border: 1px solid var(--bg-opacity-10);
    border-radius: $border-radius-m;
    box-shadow: $shadow;
    z-index: 2;
    &__content {
      display: flex;
      flex-direction: column;
      gap: $base-space;
    }
    pre {
      white-space: pre-wrap;
      margin: 0;
      overflow: auto;
      max-height: 500px;
    }
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
  &__button__icon {
    flex-shrink: 0;
  }
}
.fade-enter-active,
.fade-leave-active {
  transition: all 0.4s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
