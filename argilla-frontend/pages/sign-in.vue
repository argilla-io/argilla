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
  <AuthenticationLayout>
    <div class="login__form">
      <form class="form" @submit.prevent="onLoginUser">
        <p class="form__title" v-text="$t('login.title')" />
        <LoginInput
          v-model="login.username"
          :name="$t('login.username')"
          type="text"
          :autofocus="true"
          autocomplete="on"
        />
        <LoginInput
          v-model="login.password"
          :name="$t('login.password')"
          type="password"
          autocomplete="on"
        />
        <p
          v-if="deployment == 'quickstart'"
          v-html="
            $t('login.quickstart', {
              link: $config.documentationSiteQuickStart,
            })
          "
        />
        <base-button
          type="submit"
          :disabled="!isButtonEnabled"
          class="form__button primary full-width"
          >{{ $t("button.login") }}</base-button
        >
        <p class="form__error" v-if="error">{{ formattedError }}</p>
      </form>

      <OAuthLogin />
    </div>
  </AuthenticationLayout>
</template>

<script>
import AuthenticationLayout from "@/layouts/AuthenticationLayout";
import { Notification } from "@/models/Notifications";

export default {
  data() {
    return {
      error: undefined,
      login: {
        username: "",
        password: "",
      },
      deployment: false,
      hasAuthToken: false,
    };
  },
  components: {
    AuthenticationLayout,
  },
  async created() {
    const rawAuthToken = this.$route.query.auth;

    if (!rawAuthToken) return;

    try {
      const [username, password] = atob(rawAuthToken).split(":");

      if (username && password) {
        this.hasAuthToken = true;

        try {
          await this.loginUser({ username, password });
        } catch {
          this.hasAuthToken = false;
        }
      }
    } catch {
      /* lint:disable:no-empty */
    }
  },
  async mounted() {
    try {
      const response = await fetch("deployment.json");

      const { deployment } = await response.json();

      this.deployment = deployment;
    } catch {
      this.deployment = null;
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
    isButtonEnabled() {
      return !!this.login.username && !!this.login.password;
    },
  },
  methods: {
    nextRedirect() {
      const redirect_url = this.$nuxt.$route.query.redirect || "/";
      this.$router.push({
        path: redirect_url,
      });
    },
    async loginUser(authData) {
      await this.$auth.logout();
      await this.$store.dispatch("entities/deleteAll");
      await this.$auth.loginWith("basic", {
        data: this.encodedLoginData(authData),
      });

      Notification.dispatch("clear");

      this.nextRedirect();
    },
    async onLoginUser() {
      try {
        await this.loginUser(this.login);
      } catch (err) {
        this.error = err;
      }
    },
    encodedLoginData({ username, password }) {
      return `username=${encodeURIComponent(
        username
      )}&password=${encodeURIComponent(password)}`;
    },
  },
};
</script>

<style lang="scss" scoped>
// .form {
//   display: flex;
//   flex-flow: column;
//   &__label {
//     display: block;
//     margin-bottom: $base-space;
//     font-weight: 500;
//   }
//   &__title {
//     @include font-size(36px);
//     line-height: 1.2em;
//     margin: 0 auto $base-space * 5 auto;
//     color: $black-87;
//     font-weight: 500;
//     letter-spacing: 0.03em;
//     font-family: "raptor_v2_premiumbold", "Helvetica", "Arial", sans-serif;
//   }
//   &__input {
//     border: 1px solid palette(grey, 600);
//     border-radius: $border-radius;
//     padding: 0 1em;
//     outline: none;
//     background: transparent;
//     min-height: 40px;
//     width: 100%;
//     .active:focus-within & {
//       border-color: $primary-color;
//     }
//   }
//   &__error {
//     color: palette(orange-red-crayola);
//   }
// }

// input:-webkit-autofill {
//   box-shadow: 0 0 0px 1000px palette(white) inset;
// }
// .login {
//   &__form {
//     width: 340px;
//     margin: auto;
//     height: 90%;
//     display: flex;
//     flex-direction: column;
//     justify-content: center;
//     @include media("<=tablet") {
//       width: 100%;
//       margin: auto 0;
//     }
//   }
// }
</style>
