<template>
  <div class="edition-user-info">
    <div class="form-group role-and-username">
      <span v-circle v-html="userNameFirstChar" />
      <div class="user-role">
        <span v-html="userRole" />
      </div>
      <span class="user-username" v-html="userInfoCloned.username" />
    </div>

    <div class="form-group user-first_name">
      <h2
        class="user-token-item --heading5 --semibold description__title"
        v-html="'Name'"
      />
      <p
        class="user-token-item --body1 description__text"
        v-html="userInfoCloned.first_name"
      />
    </div>

    <div class="form-group user-last_name" v-if="userInfoCloned.last_name">
      <h2
        class="user-token-item --heading5 --semibold description__title"
        v-html="'Surname'"
      />
      <p
        class="user-token-item --body1 description__text"
        v-html="userInfoCloned.last_name"
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
  min-height: 5em;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.user-role {
  display: inline-block;
  text-align: center;

  span {
    border: 1px solid rgba(0, 0, 0, 0.37);
    border-radius: 10px;
    color: rgba(0, 0, 0, 0.6);
    font-size: 12px;
    font-size: 0.75rem;
    line-height: 12px;
    line-height: 0.75rem;
    padding: 4px;
  }
}

.role-and-username {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 50px;
}

.user-first_name {
  display: flex;
  flex-direction: column;
}

.user-last_name {
  display: flex;
  flex-direction: column;
}
</style>
