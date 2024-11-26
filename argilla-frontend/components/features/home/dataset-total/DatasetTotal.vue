<template>
  <div class="dataset-total">
    <template v-if="!!total">
      <svgicon
        name="records"
        height="12"
        width="12"
        color="var(--fg-tertiary)"
        aria-hidden="true"
      />
      <span>{{ total | formatNumberToK(2) }} {{ $t("rows") }}</span>
    </template>
  </div>
</template>

<script>
import "assets/icons/records";

export default {
  props: {
    total: {
      type: Number,
      required: true,
    },
  },
};
</script>

<style lang="scss" scoped>
.dataset-total {
  position: relative;
  min-height: 20px;
  display: flex;
  align-items: center;
  justify-items: flex-end;
  margin-left: auto;
  gap: calc($base-space / 2);
  color: var(--fg-tertiary);
  @include font-size(12px);
}
</style>
