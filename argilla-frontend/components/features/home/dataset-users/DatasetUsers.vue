<template>
  <div class="dataset-users__wrapper" @mouseleave="expanded = false">
    <div class="dataset-users" v-if="!expanded">
      <BaseTooltip
        v-for="{ username } in users.slice(0, visibleBadges)"
        :key="username"
        :text="username"
      >
        <UserBadge class="dataset-users__item" :name="username" />
      </BaseTooltip>
    </div>
    <div
      class="dataset-users__rest__wrapper"
      v-if="users.length > visibleBadges"
    >
      <BaseButton
        @mouseenter.native="expanded = true"
        @click.prevent
        class="dataset-users__button"
        >+{{ users.length - visibleBadges }}</BaseButton
      >
      <div v-if="expanded" class="dataset-users__rest">
        <BaseTooltip
          @click.stop
          v-for="{ username } in users"
          :key="username"
          :text="username"
        >
          <UserBadge class="dataset-users__item" :name="username" />
        </BaseTooltip>
      </div>
    </div>
  </div>
</template>
<script>
export default {
  props: {
    users: {
      type: Array,
      required: true,
    },
  },
  data: () => {
    return {
      visibleBadges: 3,
      expanded: false,
    };
  },
};
</script>

<style scoped lang="scss">
.dataset-users {
  display: flex;
  flex-direction: row-reverse;
  &__wrapper {
    display: flex;
    justify-content: flex-end;
    margin-right: calc($base-space / 2);
    gap: $base-space;
  }
  &__item {
    margin-right: -6px;
  }
  &__button {
    padding: 0;
  }
  &__rest {
    position: absolute;
    top: 0;
    bottom: 0;
    right: 0;
    display: flex;
    flex-direction: row-reverse;
    justify-content: flex-start;
    border-radius: $border-radius;
    z-index: 1;
    width: 200px;
    flex-wrap: wrap;
    animation: animate-users-badges 0.2s ease;
    margin-left: -$base-space;
    &__wrapper {
      position: relative;
      display: flex;
      align-items: center;
      min-height: 26px;
    }
    .dataset-users__item {
      margin-bottom: -4px;
    }
  }
}
@keyframes animate-users-badges {
  0% {
    transform: translateX(8px);
    opacity: 0;
  }
  100% {
    transform: translateX(0);
    opacity: 1;
  }
}
</style>
