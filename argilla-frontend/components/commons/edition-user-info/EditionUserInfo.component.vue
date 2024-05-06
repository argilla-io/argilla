<template>
  <div class="edition-user-info">
    <div class="form-group circle-and-role">
      <span v-circle="{ size: 'MEDIUM' }">
        {{ userInfo.username.slice(0, 2) }}
      </span>
      <BaseBadge class="--capitalized" :text="userInfo.role" />
    </div>

    <div class="form-group">
      <h2
        class="--heading5 --medium description__title"
        v-text="$t('userSettings.fields.userName')"
      />
      <p class="--body1 description__text" v-text="userInfo.username" />
    </div>

    <div class="form-group">
      <h2
        class="--heading5 --medium description__title"
        v-text="$t('userSettings.fields.firstName')"
      />
      <p class="--body1 description__text" v-text="userInfo.first_name" />
    </div>

    <div class="form-group">
      <h2
        class="--heading5 --medium description__title"
        v-text="$t('userSettings.fields.lastName')"
      />
      <p class="--body1 description__text" v-text="userInfo.last_name" />
    </div>

    <div class="form-group">
      <h2
        class="--heading5 --medium description__title"
        v-text="$t('userSettings.fields.workspaces')"
      />
      <div class="workspaces" v-if="userInfo.workspaces.length">
        <BaseBadge
          v-for="workspace in userInfo.workspaces"
          :key="workspace"
          :text="workspace"
          @on-click="goToWorkspace(workspace)"
        />
      </div>
      <p v-else class="--body1 description__text">-</p>
    </div>
  </div>
</template>

<script>
export default {
  name: "EditionUserInfoComponent",
  props: {
    userInfo: {
      type: Object,
      required: true,
    },
  },
  methods: {
    goToWorkspace(workspace) {
      this.$router.push(`/datasets?workspaces=${workspace}`);
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

.workspaces {
  gap: 5px;
  display: flex;
  flex-wrap: wrap;
  width: 90%;
}

.circle-and-role {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: $base-space * 2;
  padding-bottom: 0;
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
