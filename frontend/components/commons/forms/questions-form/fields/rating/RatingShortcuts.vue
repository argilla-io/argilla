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
        this.onUserChange();
      }, delay);
    },
    keyboardHandlerFor($event, value, options) {
      if (!this.isValidKeyFor($event)) return;

      const currValue = +value;

      if (!options.some((option) => option.value == currValue)) return;

      const targetId = options.find(({ value }) => value == currValue)?.id;

      targetId && document.getElementById(targetId).click();
    },
    isValidKeyFor({ code }) {
      const value = code.at(-1);
      const keyIsFromNumpadOrDigit = ["Numpad", "Digit"].some((prefix) =>
        code.includes(prefix)
      );

      const valueIsValid = !isNaN(value);

      return keyIsFromNumpadOrDigit && valueIsValid;
    },
    onUserChange() {
      const { options } = this.$slots.default[0].context;

      const isAnySelectedOption = options.some((option) => option.isSelected);

      if (isAnySelectedOption) this.$emit("on-user-answer");
    },
  },
};
</script>
