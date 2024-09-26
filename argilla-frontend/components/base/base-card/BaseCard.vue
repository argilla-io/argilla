<template>
  <div class="card" :class="[cardClasses]">
    <div class="card__content">
      <h3 v-if="title" class="--body1 --light card__title" v-html="title" />
      <h4 v-if="subtitle" class="--body2 --semibold card__subtitle">
        {{ subtitle }}
      </h4>
      <p v-if="text" class="--body1 card__text">
        {{ text }}
      </p>
    </div>
    <div class="card__buttons" v-if="buttonText">
      <base-button
        class="card__button outline small"
        :class="[cardClasses]"
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

<style lang="scss" scoped
  display: flex;
  align-items: flex-end;
  padding: $base-space * 2;
  border: 1px solid var(--bg-opacity-10);
  border-radius: $border-radius;
  &__buttons {
    margin-left: auto;
  }
  &__title {
    margin-top: 0;
  }
  &__text {
    margin-bottom: 0;
    color: var(--bg-opacity-37);
  }
}
</style>
