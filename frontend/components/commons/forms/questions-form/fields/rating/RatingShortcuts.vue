<template>
  <div @keydown="answerRatingFor">
    <slot></slot>
  </div>
</template>

<script>
export default {
  data() {
    return {
      timer: null,
      keyCode: "",
    };
  },
  computed: {
    options() {
      return this.$slots.default[0].context?.options;
    },
  },
  methods: {
    answerRatingFor($event) {
      if (!this.isValidKeyFor($event)) return;
      if (this.timer) clearTimeout(this.timer);

      this.keyCode += +$event.key;

      if (this.keyCode.length > 2 || this.keyCode > 10) {
        this.keyCode = "";
        return;
      }

      if (!this.options.some((option) => option.value == this.keyCode)) return;

      const target = this.options.find(({ value }) => value == this.keyCode);

      target?.id && document.getElementById(target.id).click();
      if (target.isSelected) {
        $event.preventDefault();

        this.$emit("on-user-answer");
      }

      this.timer = setTimeout(() => {
        this.keyCode = "";
        this.timer = null;
      }, 300);
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
