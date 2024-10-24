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
        <span
          v-if="!isRunningOnHF"
          class="import-from-python__warning"
          v-html="$t('home.importFromPythonHFWarning')"
        />
        <div class="import-from-python__content" v-copy-code>
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
  &__warning {
    background: var(--bg-banner-warning);
    padding: calc($base-space / 2) $base-space;
    border-top-left-radius: $border-radius-m;
    border-top-right-radius: $border-radius-m;
    @include font-size(12px);
    :deep(a) {
      color: var(--fg-primary);
      outline: none;
      &:hover {
        opacity: 0.8;
      }
    }
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
    padding: 0;
    background: var(--bg-accent-grey-1);
    border: 1px solid var(--bg-opacity-10);
    border-radius: $border-radius-m;
    box-shadow: $shadow;
    z-index: 2;
    pre {
      margin: 0;
      overflow: auto;
      max-height: 500px;
    }
  }
  &__content {
    display: flex;
    flex-direction: column;
    gap: $base-space;
    padding: $base-space * 2;
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
