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
  <span> {{ formattedDate }} </span>
</template>

<script>
export default {
  props: {
    date: {
      type: String,
    },
    format: {
      type: String,
    },
  },
  computed: {
    timeDifference() {
      return new Date().getTimezoneOffset();
    },
    formattedDate() {
      if (this.format === "date-relative-now") {
        return this.$moment(this.date)
          .locale("utc")
          .subtract(this.timeDifference, "minutes")
          .from(Date.now());
      }
      return this.$moment(this.date).locale("utc").format("YYYY-MM-DD HH:mm");
    },
  },
};
</script>
