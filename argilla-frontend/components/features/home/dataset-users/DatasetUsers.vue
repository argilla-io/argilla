<template>
  <div class="dataset-users__wrapper" @mouseleave="expanded = false">
    <div class="dataset-users">
      <BaseTooltip
        v-for="user in users.slice(0, visibleBadges)"
        :key="user.name"
        :text="user.name"
      >
        <UserBadge class="dataset-users__item" :name="user.name" />
      </BaseTooltip>
    </div>
    <template v-if="users.length > visibleBadges">
      <BaseButton
        @mouseenter.native="expanded = true"
        class="dataset-users__button"
        >+{{ users.length - visibleBadges }}</BaseButton
      >
      <div v-if="expanded" class="dataset-users__rest">
        <BaseTooltip
          v-for="user in users.slice(visibleBadges, users.length)"
          :key="user.name"
          :text="user.name"
        >
          <UserBadge class="dataset-users__item" :name="user.name" />
        </BaseTooltip>
      </div>
    </template>
  </div>
</template>
<script>
export default {
  data: () => {
    return {
      visibleBadges: 3,
      expanded: false,
      users: [
        { name: "John" },
        { name: "Jane" },
        { name: "Doe" },
        { name: "Smith" },
        { name: "Mike" },
        { name: "Pepe" },
      ],
    };
  },
};
</script>

<style scoped lang="scss">
.dataset-users {
  display: flex;
  flex-direction: row-reverse;
  &__wrapper {
    position: relative;
    display: flex;
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
    right: 0;
    display: flex;
    flex-direction: column-reverse;
    border-radius: $border-radius;
    .dataset-users__item {
      margin-bottom: -4px;
    }
  }
}
</style>
