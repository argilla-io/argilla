<template>
  <app>
    <NuxtChild />
  </app>
</template>

<script>
import app from '~/layouts/app.vue';
export default {
  name: 'exploration',
  head() {
    return {
      bodyAttrs: {
        class: [ "theme-exploration"],
      },
    };
  },
  components: {
    app
  }
};
</script>

<style lang="scss">
.theme-exploration {
  background: $bg;
    //   height: 100vh;
    // overflow: hidden;
}
</style>
