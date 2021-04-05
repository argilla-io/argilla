<template>
  <div class="container">
    <form class="form" @submit.prevent="userLogin">
      <BiomeIsotipo class="form__logo" :minimal="false" />
      <p class="form__title">Rubrix</p>
      <div class="form__input" :class="{ active: login.username }">
        <input v-model="login.username" type="text" placeholder="username" />
      </div>
      <div class="form__input" :class="{ active: login.password }">
        <input
          v-model="login.password"
          type="password"
          placeholder="password"
        />
      </div>
      <ReButton type="submit" class="form__button button-primary"
        >Submit</ReButton
      >
      <p>{{ error }}</p>
    </form>
  </div>
</template>

<script>
export default {
  layout: "app",
  data() {
    return {
      error: undefined,
      login: {
        username: "",
        password: "",
      },
    };
  },
  async mounted() {
    if (this.$auth.loggedIn) {
      return;
    }
    if (!this.$config.securityEnabled) {
      await this.$auth.setUser("local");
      await this.$auth.setUserToken("mock-token");
      this.nextRedirect();
    }
  },
  methods: {
    nextRedirect() {
      const redirect_url = this.$nuxt.$route.query.redirect || "/";
      this.$router.push({
        path: redirect_url,
      });
    },
    async userLogin() {
      try {
        await this.$store.dispatch("entities/deleteAll");
        await this.$auth.loginWith("local", {
          data: `username=${this.login.username}&password=${this.login.password}`,
        });
        this.nextRedirect();
      } catch (err) {
        this.error = err;
      }
    },
  },
};
</script>

<style lang="scss" scoped>
.container {
  background: $line-light-color;
  display: flex;
  align-items: center;
  min-height: 100vh;
}

.form {
  background: $lighter-color;
  margin: auto;
  display: inline-block;
  padding: 2em 4em 1.5em 4em;
  box-shadow: 29px 29px 57px #d0d0d1, -29px -29px 57px #ffffff;
  text-align: center;
  max-width: 300px;
  &__logo {
    text-align: center;
    margin-bottom: 1em;
  }
  &__title {
    text-align: center;
    @include font-size(20px);
  }
  &__button {
    margin: 2em auto 0 auto;
    text-align: center;
    display: block;
  }
  &__input {
    position: relative;
    display: block;
    margin-bottom: 1em;
    &.active {
      &:before {
        width: 100%;
        transition: width 0.3s ease-in-out;
      }
    }
    &:after,
    &:before {
      content: "";
      height: 1px;
      background: $line-smooth-color;
      display: block;
      position: absolute;
      bottom: 0;
    }
    &:before {
      width: 0;
      background: $secondary-color;
      transition: width 0.3s ease-in-out;
      z-index: 1;
    }
    &:after {
      width: 100%;
    }
    input {
      border: 0;
      outline: none;
      background: transparent;
      min-height: 40px;
      min-width: 200px;
    }
  }
}
</style>
