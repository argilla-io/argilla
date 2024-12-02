<template>
  <div v-circle="{ size: 'MINI' }" class="user-badge">
    {{ getTwoFirstChars }}
  </div>
</template>

<script>
export default {
  props: {
    name: {
      type: String,
      required: true,
    },
  },
  computed: {
    getTwoFirstChars() {
      return this.name.slice(0, 2).toUpperCase();
    },
  },
};
</script>

<style scoped lang="scss">
.user-badge {
  background: var(--color-avatar-bg);
  color: var(--color-avatar-fg);
}
</style>
