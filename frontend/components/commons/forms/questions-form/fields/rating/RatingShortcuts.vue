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
      return this.$slots.default[0].context?.question.answer.values;
    },
  },
  methods: {
    reset() {
      this.keyCode = "";
      this.timer = null;
    },
    answerRatingFor($event) {
      if (this.timer) clearTimeout(this.timer);
      if ($event.key == "Tab") return;

      $event.preventDefault();

      if ($event.code == "Space") {
        document.activeElement.click();

        return;
      }

      this.keyCode += $event.key;

      if (isNaN(this.keyCode)) {
        this.reset();

        return;
      }

      const target = this.options.find(({ value }) => value == this.keyCode);

      this.timer = setTimeout(() => {
        if (target) document.getElementById(target.id).click();

        this.reset();
      }, 300);
    },
  },
};
</script>
