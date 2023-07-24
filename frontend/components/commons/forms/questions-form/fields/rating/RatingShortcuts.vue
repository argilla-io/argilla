<template>
  <div @keydown="respondToRatingFor">
    <slot></slot>
  </div>
</template>

<script>
export default {
  data() {
    return {
      value: "",
    };
  },
  methods: {
    respondToRatingFor($event) {
      this.value += $event.key;

      this.debounce(() => {
        this.keyboardHandlerFor($event, this.value);

        this.value = "";
      })();
    },
    debounce(callback, delay = 800) {
      let timer;

      return () => {
        clearTimeout(timer);
        timer = setTimeout(() => {
          callback.apply(this);
        }, delay);
      };
    },
    keyboardHandlerFor($event, value) {
      if (!this.isValidKeyFor($event)) return;

      const currValue = +value;

      const { options } = this.$slots.default[0].context;

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
  },
};
</script>
