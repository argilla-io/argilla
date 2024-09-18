/* eslint-disable */
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
  <svg
    v-if="color === 'default'"
    width="169"
    height="88"
    viewBox="0 0 169 88"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <path
      d="M43.94 87.88C68.2074 87.88 87.88 68.2074 87.88 43.94C87.88 19.6726 68.2074 0 43.94 0C19.6726 0 0 19.6726 0 43.94C0 68.2074 19.6726 87.88 43.94 87.88Z"
      fill="url(#paint0_linear_620_12184)"
    />
    <path
      d="M168.13 87.73C144.892 87.7035 122.613 78.4605 106.181 62.0286C89.7495 45.5968 80.5065 23.3181 80.48 0.0799561H111.05C111.066 15.2136 117.085 29.7229 127.786 40.4241C138.487 51.1252 152.996 57.1441 168.13 57.16V87.73Z"
      fill="#F8C0A7"
    />
    <defs>
      <linearGradient
        id="paint0_linear_620_12184"
        x1="19.41"
        y1="20.91"
        x2="74.11"
        y2="72.26"
        gradientUnits="userSpaceOnUse"
      >
        <stop offset="0.02" stop-color="#FF675F" />
        <stop offset="1" stop-color="#F73D3D" />
      </linearGradient>
    </defs>
  </svg>
  <svg
    v-else-if="color === 'white'"
    width="169"
    height="89"
    viewBox="0 0 169 89"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <path
      d="M43.94 88.12C68.2074 88.12 87.8799 68.4474 87.8799 44.18C87.8799 19.9126 68.2074 0.23999 43.94 0.23999C19.6726 0.23999 6.10352e-05 19.9126 6.10352e-05 44.18C6.10352e-05 68.4474 19.6726 88.12 43.94 88.12Z"
      fill="white"
    />
    <path
      d="M168.13 87.9699C144.892 87.9435 122.613 78.7005 106.181 62.2686C89.7496 45.8368 80.5065 23.558 80.48 0.319946H111.05C111.066 15.4536 117.085 29.9629 127.786 40.6641C138.487 51.3652 152.996 57.3841 168.13 57.3999V87.9699Z"
      fill="white"
    />
  </svg>
</template>

<script>
export default {
  props: {
    color: {
      type: String,
      default: "default",
      validator: (value) => ["default", "white"].includes(value),
    },
  },
};
</script>
<style lang="scss" scoped></style>
