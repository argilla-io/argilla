<template>
  <section role="alert" class="banner" :class="`--${type}`">
    <div class="banner__content">
      <svgicon
        v-if="icon"
        class="banner__icon"
        :name="icon"
        width="16px"
        height="16px"
      />
      <p class="banner__text">{{ message }}</p>
    </div>
    <BaseButton
      v-if="buttonLink"
      class="banner__link"
      :href="buttonLink"
      target="_blank"
      >{{ buttonText }}</BaseButton
    >
    <BaseButton
      class="banner__close-button"
      v-if="dismissible"
      @click="onDismiss"
      ><svgicon name="close" width="16px" height="16px"
    /></BaseButton>
  </section>
</template>

<script>
import "assets/icons/danger";
import "assets/icons/close";
export default {
  props: {
    message: {
      type: String,
      required: true,
    },
    hideBanner: {
      type: Boolean,
      default: false,
    },
    dismissible: {
      type: Boolean,
      default: false,
    },
    buttonText: {
      type: String,
    },
    buttonLink: {
      type: String,
    },
    type: {
      type: String,
      default: "info",
      validate(value) {
        return ["info", "warning", "error"].includes(value);
      },
    },
  },
  computed: {
    icon() {
      switch (this.type) {
        case "warning":
          return "danger";
        case "error":
          return "danger";
        default:
          return null;
      }
    },
  },
  methods: {
    onDismiss() {
      this.$emit("on-dismiss");
    },
  },
};
</script>

<style lang="scss" scoped>
$info-color: var(--bg-banner-info);
$warning-color: var(--bg-banner-warning);
$error-color: var(--bg-banner-error);
.banner {
  $this: &;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: $base-space;
  width: 100%;
  min-height: $base-space * 4;
  padding: calc($base-space / 2);
  background-color: $warning-color;
  &__content {
    display: flex;
    align-items: center;
    gap: $base-space;
  }
  &__text {
    @include font-size(12px);
    margin: 0;
  }
  #{$this}__link.button {
    padding: 0;
    @include font-size(12px);
    color: var(--fg-cuaternary);
    &:hover {
      color: hsl(from var(--fg-cuaternary) h s l / 90%);
    }
  }
  &__close-button {
    padding: 0;
  }
}
</style>
