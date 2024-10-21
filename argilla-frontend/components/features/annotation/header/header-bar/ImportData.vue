<template>
  <div class="import-data">
    <BaseButton
      class="primary"
      @click.prevent="visibleSnippet = !visibleSnippet"
      >Import data</BaseButton
    >
    <transition name="fade" appear>
      <dialog
        v-if="visibleSnippet"
        class="import-data__dialog"
        v-click-outside="closeDialog"
      >
        <p class="import-data__title">Add records to your dataset</p>
        <code class="import-data__code">
          <pre v-text="snippet" />
          <base-action-tooltip
            class="import-data__copy"
            :tooltip="$t('copied')"
          >
            <a href="#" @click.prevent="copy(snippet)">
              <svgicon
                color="var(--fg-secondary)"
                name="copy"
                width="16"
                height="16"
              />
            </a>
          </base-action-tooltip>
        </code>
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
    top: calc(100% + $base-space);
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
    padding: $base-space * 2;
    background: var(--bg-opacity-4);
    border-radius: $border-radius-m;
    white-space: pre-wrap;
    max-width: 70vw;
    pre {
      margin: 0;
      overflow: auto;
      white-space: pre-wrap;
    }
  }
  &__copy {
    position: absolute;
    top: $base-space;
    right: $base-space;
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
