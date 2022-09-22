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
      <Rubrix class="form__logo" />
      <p class="form__title">Build, improve, and monitor data for NLP</p>
      <div class="form__input" :class="{ active: login.username }">
        <input v-model="login.username" type="text" placeholder="Username" />
      </div>
      <div class="form__input" :class="{ active: login.password }">
        <input
          v-model="login.password"
          type="password"
          placeholder="Password"
        />
      </div>
      <base-button type="submit" class="form__button primary"
        >Enter</base-button
      >
      <p v-if="error">{{ error }}</p>
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
  background: palette(grey, 700);
  display: flex;
  align-items: center;
  min-height: 100vh;
}

.form {
  border-radius: $border-radius;
  background: palette(white);
  margin: auto;
  display: inline-block;
  padding: 50px;
  box-shadow: $shadow;
  text-align: center;
  max-width: 350px;
  &__logo {
    text-align: center;
    margin-bottom: 1.5em;
  }
  &__title {
    text-align: center;
    @include font-size(26px);
    line-height: 1.2em;
    margin: 0 auto 2em auto;
    color: #010250;
    font-weight: 600;
    letter-spacing: 0.03em;
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
}
input:-webkit-autofill {
  box-shadow: 0 0 0px 1000px palette(white) inset;
}
</style>
