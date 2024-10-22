<template></template>
<template>
  <div class="card">
    <h2 class="card__title" v-text="title" />
    <p class="card__text" v-text="text" />
    <BaseButton
      class="card__button"
      :class="buttonType"
      @click="$emit('on-click', buttonAction)"
      >{{ buttonText }}</BaseButton
    >
  </div>
</template>

<script>
export default {
  props: {
    title: {
      type: String,
      required: true,
    },
    text: {
      type: String,
      required: true,
    },
    buttonText: {
      type: String,
      required: true,
    },
    buttonAction: {
      type: String,
      required: true,
    },
    buttonType: {
      type: String,
      default: "primary",
    },
  },
};
</script>

<style scoped lang="scss">
.card {
  display: flex;
  flex-direction: column;
  text-align: center;
  gap: $base-space * 2;
  border: 1px dashed var(--bg-opacity-10);
  border-radius: $border-radius-m;
  padding: $base-space * 2;
  &__title {
    @include font-size(18px);
    font-weight: 600;
    margin: 0;
  }

  &__text {
    margin: 0;
  }

  &__button.button {
    margin: auto;
    background: linear-gradient(177.33deg, #ffffff 16.49%, #eeeeee 114.03%);
    border: 1px solid #f6bf00;
  }
}
</style>
