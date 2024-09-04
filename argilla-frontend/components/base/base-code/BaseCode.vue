<template>
  <base-action-tooltip class="button" :tooltip="t('copied')">
    <a href="#" @click.prevent="copy(code)">
      <svgicon name="copy" width="16" height="16" />
    </a>
  </base-action-tooltip>
</template>

<script>
import { useTranslate } from "~/v1/infrastructure/services";
import "assets/icons/copy";

export default {
  props: {
    code: {
      type: String,
      required: true,
    },
  },
  methods: {
    copy(code) {
      this.$copyToClipboard(code);
    },
  },
  setup() {
    return useTranslate();
  },
};
</script>

<style lang="scss" scoped>
.button {
  position: absolute !important;
  top: 1em;
  right: 1em;
  svg {
    fill: var(--color-white);
  }
}
</style>
