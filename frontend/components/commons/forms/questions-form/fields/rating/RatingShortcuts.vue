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
      if ($event.key == "Tab") return;

      if (this.timer) clearTimeout(this.timer);
      $event.preventDefault();

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
