<template>
  <div>
    <slot></slot>
  </div>
</template>

<script>
export default {
  name: "SynchronizeScroll",
  mounted() {
    this.synchronizeScrolls();
  },
  methods: {
    synchronizeScrolls() {
      const children = this.$slots.default
        .filter((child) => !!child.tag)
        .map((child) => ({
          isSyncing: false,
          element: child.elm,
        }));

      const applyProportionalScroll = (elementScrolling, elementToScroll) => {
        const elementScrollingTop = elementScrolling.scrollTop;
        const elementScrollingTotal =
          elementScrolling.scrollHeight - elementScrolling.clientHeight;

        const toScrollTotal =
          elementToScroll.scrollHeight - elementToScroll.clientHeight;

        const proportionalScrolling =
          elementScrollingTop / elementScrollingTotal;

        elementToScroll.scrollTop = toScrollTotal * proportionalScrolling;
      };

      for (const child of children) {
        child.element.onscroll = function () {
          if (!child.isSyncing) {
            children
              .filter((otherChild) => otherChild !== child)
              .forEach((otherChild) => {
                otherChild.isSyncing = true;
                applyProportionalScroll(this, otherChild.element);
              });
          }

          child.isSyncing = false;
        };
      }
    },
  },
};
</script>
<style lang="scss" scoped>
.root {
  display: flex;
  flex-direction: column;
}
</style>
