<template>
  <div class="edition-user-info">
    <div class="form-group circle-and-role">
      <span v-circle="{ size: 'MEDIUM' }" v-html="userNameFirstChar" />
      <div class="user-role" v-text="userRole" />
    </div>

    <div class="form-group user-first_name">
      <h2
        class="--heading5 --semibold description__title"
        v-text="'Username'"
      />
      <p class="--body1 description__text" v-text="userInfoCloned.username" />
    </div>

    <div class="form-group user-first_name">
      <h2 class="--heading5 --semibold description__title" v-text="'Name'" />
      <p class="--body1 description__text" v-text="userInfoCloned.first_name" />
    </div>

    <div class="form-group user-last_name">
      <h2 class="--heading5 --semibold description__title" v-text="'Surname'" />
      <p
        class="--body1 description__text"
        v-text="userInfoCloned.last_name ?? '-'"
      />
    </div>
  </div>
</template>

<script>
import { cloneDeep } from "lodash";
export default {
  name: "EditionUserInfoComponent",
  props: {
    userInfo: {
      type: Object,
      required: true,
    },
  },
  created() {
    this.userInfoCloned = cloneDeep(this.userInfo);
  },
  computed: {
    userName() {
      return this.userInfoCloned.username;
    },
    userNameFirstChar() {
      return this.userName.slice(0, 2);
    },
    userRole() {
      return this.$options.filters.capitalize(this.userInfoCloned.role);
    },
  },
};
</script>

<style lang="scss" scoped>
.form-group {
  padding: $base-space * 3 0;
  &:not(:first-child):not(:last-child) {
    border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  }
}

.user-role {
  border: 1px solid rgba(0, 0, 0, 0.37);
  border-radius: 10px;
  color: rgba(0, 0, 0, 0.6);
  font-size: 12px;
  font-size: 0.75rem;
  line-height: 12px;
  line-height: 0.75rem;
  padding: 4px;
}

.circle-and-role {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: $base-space * 2;
  padding-bottom: 0;
}

.user-first_name {
  display: flex;
  flex-direction: column;
}

.user-last_name {
  display: flex;
  flex-direction: column;
}

.user-username {
  @include font-size(16px);
}

.description {
  &__title {
    margin-top: 0;
    margin-bottom: $base-space;
  }
  &__text {
    margin: 0;
  }
}
</style>
