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
  <div class="error">
    <div class="error__container">
      <brand-logo class="error__logo" />
    </div>
    <div class="error__code">
      {{ error.statusCode }}
    </div>
    <div class="error__container">
      <div class="error__content">
        <div class="error__pill">{{ error.message }}</div>
        <h1 class="error__title">Something went wrong.</h1>
        <h2 class="error__text">
          We can't seem to find the page you are looking for
        </h2>
        <div class="error__buttons">
          <nuxt-link class="error__button" :to="`/`"
            >Back to home page
            <svgicon name="chevron-right" width="20" height="20"></svgicon>
          </nuxt-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import "assets/icons/chevron-right";
export default {
  layout: "error",
  props: ["error"],
};
</script>
<style lang="scss" scoped>
.error {
  position: relative;
  min-height: 100vh;
  background: var(--bg-accent-grey-1);
  &__container {
    @extend %container;
    margin: auto;
    padding: 0 $base-space * 3;
  }
  &__logo {
    max-width: 150px;
    path {
      fill: var(--color-brand);
    }
  }
  &__code {
    position: absolute;
    left: -3vw;
    color: var(--bg-accent-grey-1);
    font-family: $secondary-font-family;
    text-shadow: 0 0 3px var(--color-brand);
    font-size: 34vw;
    line-height: 1em;
    @include media("<desktop") {
      position: relative;
      left: 0;
      margin-left: $base-space * 3;
      margin-bottom: 0.4em;
      @include font-size(75px);
      color: var(--color-brand);
      text-shadow: none;
    }
  }
  &__pill {
    display: inline-block;
    border: 1px solid var(--color-brand);
    padding: 5px 10px;
    border: 1px solid var(--color-brand);
    border-radius: 20px;
    margin-bottom: 20px;
    color: var(--color-brand);
  }
  &__title {
    display: block;
    margin: 0;
    font-family: $secondary-font-family;
    @include font-size(75px);
    line-height: 1em;
  }
  &__text {
    display: block;
    margin-bottom: 1em;
    margin-left: calc(4 / 12 * 100%);
    @include font-size(20px);
    font-weight: lighter;
    line-height: 1.5em;
    @include media("<desktop") {
      margin-left: 0;
    }
  }
  &__button {
    display: inline-flex;
    align-items: center;
    gap: $base-space;
    padding: 12px 20px;
    border-radius: $border-radius;
    background: var(--color-brand);
    border: 0;
    outline: 0;
    text-decoration: none;
    color: var(--color-white);
    @include font-size(16px);
    font-weight: 600;
    &:hover {
      background: var(--color-brand);
    }
    @include media(">desktop") {
      margin-left: calc(4 / 12 * 100%);
    }
  }
  &__content {
    position: relative;
    max-width: 500px;
    margin-left: calc(6 / 12 * 100%);
    margin-top: 4vh;
    @include media("<desktop") {
      margin-left: 0;
    }
  }
}
</style>
