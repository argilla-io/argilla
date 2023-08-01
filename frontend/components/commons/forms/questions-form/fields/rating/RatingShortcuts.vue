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
      if (this.timer) clearTimeout(this.timer);

      this.keyCode += $event.key;

      if (isNaN(this.keyCode)) {
        this.keyCode = "";

        return;
      }

      const target = this.options.find(({ value }) => value == this.keyCode);

      if (!target) return;
      $event.preventDefault();

      document.getElementById(target.id).click();

      this.timer = setTimeout(() => {
        this.keyCode = "";
        this.timer = null;
      }, 300);
    },
  },
};
</script>
