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
  <section id="header" ref="header" class="header">
    <base-topbar-brand>
      <base-breadcrumbs
        :breadcrumbs="breadcrumbs"
        @breadcrumb-action="onBreadcrumbAction"
      />

      <user-avatar-tooltip />
    </base-topbar-brand>
  </section>
</template>

<script>
import "assets/icons/code";

export default {
  data() {
    return {
      headerHeight: null,
    };
  },
  props: {
    breadcrumbs: {
      type: Array,
    },
  },
  methods: {
    onBreadcrumbAction(action) {
      this.$emit("breadcrumb-action", action);
    },
  },
};
</script>

<style lang="scss" scoped>
$header-button-color: #262a2e;
.header {
  opacity: 1;
  transition: none;
  top: 0;
  right: 0;
  left: 0;
  transform: translateY(0);
  position: sticky;
  background: $bg;
  z-index: 3;
}
</style>
