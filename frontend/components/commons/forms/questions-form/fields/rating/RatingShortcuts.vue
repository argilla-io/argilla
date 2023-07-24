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
