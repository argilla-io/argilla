<template>
  <div @keydown="answerRatingFor">
    <slot></slot>
  </div>
</template>

<script>
export default {
  methods: {
    options() {
      return this.$slots.default[0].context;
    },
  },
  methods: {
    answerRatingFor($event) {
      if (!this.isValidKeyFor($event)) return;

      const { options } = this.$slots.default[0].context;

      const currValue = $event.key == 0 ? 10 : +$event.key;

      if (!options.some((option) => option.value == currValue)) return;

      const target = options.find(({ value }) => value == currValue);

      target?.id && document.getElementById(target.id).click();

      target.isSelected && this.$emit("on-user-answer");
    },
    isValidKeyFor({ code }) {
      const value = code.at(-1);
      const keyIsFromNumpadOrDigit = ["Numpad", "Digit"].some((prefix) =>
        code.includes(prefix)
      );

      const valueIsValid = !isNaN(value);

      return keyIsFromNumpadOrDigit && valueIsValid;
    },
  },
};
</script>
