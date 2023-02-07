<!--
  - coding=utf-8
  - Copyright 2021-present, the Recognai S.L. team.
  -
  - Licensed under the Apache License, Version 2.0 (the "License");
  - you may not use this file except in compliance with the License.
  - You may obtain a copy of the License at
  -
  -     http://www.apache.org/licenses/LICENSE-2.0
  -
  - Unless required by applicable law or agreed to in writing, software
  - distributed under the License is distributed on an "AS IS" BASIS,
  - WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  - See the License for the specific language governing permissions and
  - limitations under the License.
  -->

<template>
  <div class="container">
    <form class="form" @submit.prevent="userLogin">
      <brand-logo class="form__logo" />
      <div class="form__content">
        <p class="form__title">Welcome</p>
        <p class="form__text">Please enter your details to login.</p>
        <div class="form__input" :class="{ active: login.username }">
          <label class="form__label">Username</label>
          <input
            v-model="login.username"
            type="text"
            placeholder="Enter your username"
          />
        </div>
        <div class="form__input" :class="{ active: login.password }">
          <label class="form__label">Password</label>
          <input
            v-model="login.password"
            type="password"
            placeholder="Enter your password"
          />
        </div>
        <p v-if="deployment === 'quickstart'">
          You are using the Quickstart version of Argilla. Check
          <a
            href="https://docs.argilla.io/en/latest/getting_started/quickstart.html"
            target="_blank"
            >this guide</a
          >
          to know more about usage and configuration options.
        </p>
        <base-button type="submit" class="form__button primary"
          >Enter</base-button
        >
        <p class="form__error" v-if="error">{{ formattedError }}</p>
      </div>
    </form>
    <div class="login--right">
      <p class="login__claim">Build, improve, and monitor data for NLP</p>
      <geometric-shape-a />
      <p class="login__text">
        To get support from the community, join us on
        <a
          href="https://join.slack.com/t/rubrixworkspace/shared_invite/zt-whigkyjn-a3IUJLD7gDbTZ0rKlvcJ5g"
          target="_blank"
          >Slack</a
        >
      </p>
    </div>
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
      deployment: false,
    };
  },
  async mounted() {
    try {
      fetch("deployment.json")
        .then((r) => r.json())
        .then(({ deployment }) => {
          this.deployment = deployment;
        });
    } catch (e) {
      this.deployment = null;
    }
    if (this.$auth.loggedIn) {
      return;
    }
  },
  computed: {
    formattedError() {
      if (this.error) {
        return this.error.toString().includes("401")
          ? "Wrong username or password. Try again"
          : this.error;
      }
    },
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
        await this.$auth.loginWith("authProvider", {
          data: this.encodedLoginData(),
        });
        this.nextRedirect();
      } catch (err) {
        this.error = err;
      }
    },
    encodedLoginData() {
      const { username, password } = this.login;
      return `username=${encodeURIComponent(
        username
      )}&password=${encodeURIComponent(password)}`;
    },
  },
};
</script>

<style lang="scss" scoped>
.container {
  min-height: 100vh;
  background: $brand-secondary-color;
  display: flex;
  a {
    outline: none;
    color: $brand-primary-color;
    text-decoration: none;
    &:hover {
      color: darken($brand-primary-color, 10%);
    }
  }
}
.form {
  background: palette(white);
  display: flex;
  padding: $base-space * 5;
  z-index: 1;
  min-height: 100vh;
  width: 50vw;
  flex-flow: column;
  &__content {
    max-width: 300px;
    margin: auto;
  }
  &__logo {
    text-align: left;
    max-width: 120px;
    height: auto;
  }
  &__label {
    display: block;
    margin-bottom: $base-space;
    font-weight: 500;
  }
  &__title {
    @include font-size(40px);
    line-height: 1.2em;
    margin: 0 auto $base-space auto;
    color: $black-87;
    font-weight: 500;
    letter-spacing: 0.03em;
    font-family: "raptor_v2_premiumbold", "Helvetica", "Arial", sans-serif;
  }
  &__text {
    margin-top: 0;
    margin-bottom: $base-space * 6;
    @include font-size(18px);
    line-height: 1.4em;
    font-weight: 400;
  }
  &__button {
    margin: 2em auto 0 auto;
    justify-content: center;
    width: 100%;
  }
  &__input {
    position: relative;
    display: block;
    margin-bottom: 1em;
    input {
      border: 1px solid palette(grey, 600);
      border-radius: $border-radius;
      padding: 0 1em;
      outline: none;
      background: transparent;
      min-height: 40px;
      width: 100%;
    }
  }
  &__error {
    color: #ff4f46;
  }
}
input:-webkit-autofill {
  box-shadow: 0 0 0px 1000px palette(white) inset;
}
.login {
  &--right {
    display: flex;
    flex-flow: column;
    position: relative;
    width: 50vw;
    svg {
      position: absolute;
      max-width: 380px;
      margin: auto;
      top: 0;
      bottom: 0;
      left: 0;
      right: 0;
    }
  }
  &__claim {
    margin: auto auto;
    max-width: 400px;
    z-index: 1;
    @include font-size(40px);
    line-height: 1.3em;
    color: palette(white);
    font-family: "raptor_v2_premiumbold", "Helvetica", "Arial", sans-serif;
    transform: translateX(-0.85em);
    padding-top: 1em;
  }
  &__text {
    margin-top: 0;
    text-align: center;
    margin-bottom: $base-space * 3;
    @include font-size(16px);
    line-height: 1.4em;
    font-weight: 400;
  }
}
</style>
