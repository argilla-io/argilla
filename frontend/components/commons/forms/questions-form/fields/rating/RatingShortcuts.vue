<template>
  <div @keydown="keyboardHandlerFor">
    <slot></slot>
  </div>
</template>

<script>
export default {
  methods: {
    keyboardHandlerFor($event) {
      const currValue = +$event.code.at(-1);
      const prefix = $event.code.substring(0, 6);

      if (!this.isValidKeyFor({ value: currValue, prefix })) return;

      const { options } = this.$slots.default[0].context;

      if (currValue > options.length) return;

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
