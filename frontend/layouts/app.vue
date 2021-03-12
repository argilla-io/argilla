<template>
  <div>
    <Nuxt v-if="!$slots.default" />
    <slot />
  </div>
</template>

<script>
import { Notification } from "@/models/Notifications";
export default {
  name: 'index',
  computed: {
    imOffline() {
      return this.$nuxt.isOffline
    }
  },
  watch: {
    imOffline() {
      return Notification.dispatch("notify", {
        message: 'You are offline',
        type: "error",
      });
    }
  }
};
</script>

<style></style>

