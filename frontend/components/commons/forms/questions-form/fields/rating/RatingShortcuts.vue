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

      this.debounce($event);
    },
    debounce($event, debounceDuration = 500) {
      if (this.timeoutId !== null) {
        clearTimeout(this.timeoutId);
      }

      this.timeoutId = setTimeout(() => {
        this.keyboardHandlerFor($event, this.value);
      }, debounceDuration);
    },
    keyboardHandlerFor($event, value) {
      this.value = "";

      const prefix = $event.code?.substring(0, 6);
      if (!this.isValidKeyFor({ value, prefix })) return;

      const currValue = +value;

      const { options } = this.$slots.default[0].context;

      if (!options.some((option) => option.value == currValue)) return;

      const targetId = options.find(({ value }) => value == currValue)?.id;

      targetId && document.getElementById(targetId).click();
    },
    isValidKeyFor({ value, prefix }) {
      const keyIsFromNumpad = prefix === "Numpad";
      const valueIsValid = !isNaN(value);

      return keyIsFromNumpad && valueIsValid;
    },
  },
};
</script>
