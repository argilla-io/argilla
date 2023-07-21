<template>
  <div @keydown="keyboardHandlerFor">
    <slot></slot>
  </div>
</template>

<script>
export default {
  methods: {
    keyboardHandlerFor($event) {
      $event.preventDefault();

      if (!this.isNumeric($event.key)) return;

      const { options } = this.$slots.default[0].context;

      if ($event.key > options.length) return;

      let offset = 0;

      const isShiftKeyPressed = !!$event.shiftKey;
      if (isShiftKeyPressed) {
        offset = 10;
      }

      const targetId = options.find(
        ({ value }) => value == +$event.key + offset
      )?.id;

      targetId && document.getElementById(targetId).click();
    },
    isNumeric(num) {
      return !isNaN(num);
    },
  },
};
</script>
