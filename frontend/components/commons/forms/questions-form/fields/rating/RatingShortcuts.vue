<template>
  <div @keydown="answerRatingFor">
    <slot></slot>
  </div>
</template>

<script>
export default {
  computed: {
    options() {
      return this.$slots.default[0].context?.options;
    },
  },
  methods: {
    answerRatingFor($event) {
      if (!this.isValidKeyFor($event)) return;

      const currValue = $event.key == 0 ? 10 : +$event.key;

      if (!this.options.some((option) => option.value == currValue)) return;

      const target = this.options.find(({ value }) => value == currValue);

      target?.id && document.getElementById(target.id).click();

      if (target.isSelected) {
        $event.preventDefault();

        this.$emit("on-user-answer");
      }
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
