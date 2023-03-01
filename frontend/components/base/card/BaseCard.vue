<template>
  <div class="card" :class="[cardClasses]">
    <h3 v-if="title" class="--body1 --semibold card__title">{{ title }}</h3>
    <h4 v-if="subtitle" class="--body2 --semibold card__subtitle">
      {{ subtitle }}
    </h4>
    <p v-if="text" class="--body3 card__text">
      {{ text }}
    </p>
    <div class="card__buttons">
      <base-button
        class="card__button"
        :class="[cardClasses]"
        v-if="buttonText"
        @click="action"
        >{{ buttonText }}</base-button
      >
    </div>
  </div>
</template>

<script>
export default {
  props: {
    title: {
      type: String,
    },
    subtitle: {
      type: String,
    },
    text: {
      type: String,
    },
    buttonText: {
      type: String,
    },
    cardType: {
      type: String,
      default: "default",
      validator(value) {
        return ["danger", "warm", "info", "default"].includes(value);
      },
    },
  },
  computed: {
    cardClasses() {
      return {
        "--danger": this.cardType === "danger",
        "--warm": this.cardType === "warm",
        "--info": this.cardType === "info",
        "--default": this.cardType === "default",
      };
    },
  },
  methods: {
    action() {
      this.$emit("card-action");
    },
  },
};
</script>

<style lang="scss">
.card {
  padding: $base-space * 2;
  border: 1px solid $black-10;
  border-radius: $border-radius;
  &__buttons {
    margin-top: $base-space * 4;
  }
  &__title {
    margin-top: 0;
  }
}
.--danger {
  .button {
  }
}
</style>
