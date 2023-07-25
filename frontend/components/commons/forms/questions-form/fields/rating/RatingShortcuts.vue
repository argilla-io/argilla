<template>
  <div @keydown="answerRatingFor">
    <slot></slot>
  </div>
</template>

<script>
export default {
  data() {
    return {
      value: "",
      timer: 0,
    };
  },
  methods: {
    answerRatingFor($event) {
      if (this.timer) clearTimeout(this.timer);

      this.value += $event.key;

      const { options } = this.$slots.default[0].context;

      this.keyboardHandlerFor($event, this.value, options);

      const delay = options.length >= 10 ? 800 : 10;

      this.timer = setTimeout(() => {
        this.value = "";
      }, delay);
    },
    keyboardHandlerFor($event, value, options) {
      if (!this.isValidKeyFor($event)) return;

      const currValue = +value;

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
