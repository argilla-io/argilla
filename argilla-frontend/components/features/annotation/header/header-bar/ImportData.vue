<template>
  <div class="import-data">
    <BaseButton
      class="primary import-data__button"
      @click.prevent="visibleSnippet = !visibleSnippet"
      >{{ $t("datasetCreation.importData") }}</BaseButton
    >
    <transition name="fade" appear>
      <dialog
        v-if="visibleSnippet"
        class="import-data__dialog"
        v-click-outside="closeDialog"
      >
        <p class="import-data__title">{{ $t("datasetCreation.addRecords") }}</p>
        <div class="import-data__code">
          <MarkdownRenderer :markdown="snippet" />
        </div>
      </dialog>
    </transition>
  </div>
</template>

<script>
export default {
  props: {
    snippet: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      visibleSnippet: false,
    };
  },
  methods: {
    copy(code) {
      this.$copyToClipboard(code);
    },
    closeDialog() {
      this.visibleSnippet = false;
    },
  },
};
</script>

<style lang="scss" scoped>
.import-data {
  position: relative;
  margin-left: auto;
  margin-right: 0;
  &__dialog {
    position: absolute;
    right: 0;
    left: auto;
    width: auto;
    min-width: 360px;
    top: calc(100% + $base-space + 2px);
    display: block;
    margin-left: auto;
    padding: $base-space * 2;
    border: 1px solid var(--bg-opacity-10);
    border-radius: $border-radius-m;
    box-shadow: $shadow;
    z-index: 2;
  }
  &__title {
    margin-top: 0;
  }
  &__code {
    position: relative;
    display: block;
    border-radius: $border-radius-m;
    white-space: pre-wrap;
    min-width: 50vw;
  }
  &__copy {
    position: absolute;
    top: $base-space;
    right: $base-space;
  }
  &__button.button {
    background: hsl(0, 1%, 18%);
    &:hover {
      background: hsl(0, 1%, 22%);
    }
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
