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
    formattedDate() {
      const date = new Date(this.date);

      if (this.format === "date-relative-now") {
        return this.timeAgo(date);
      }

      return date.toLocaleString("sv", {
        year: "numeric",
        month: "numeric",
        day: "numeric",
        hour: "numeric",
        minute: "numeric",
        hour12: false,
      });
    },
  },
  methods: {
    timeAgo(date) {
      const formatter = new Intl.RelativeTimeFormat("en", {
        numeric: "auto",
      });
      const ranges = {
        years: 3600 * 24 * 365,
        months: 3600 * 24 * 30,
        weeks: 3600 * 24 * 7,
        days: 3600 * 24,
        hours: 3600,
        minutes: 60,
        seconds: 1,
      };

      const now = new Date();
      const time = new Date(date.getTime() - now.getTime());
      time.setMinutes(time.getMinutes() - now.getTimezoneOffset());

      const secondsElapsed = time / 1000;
      for (const key in ranges) {
        if (ranges[key] <= Math.abs(secondsElapsed)) {
          const delta = secondsElapsed / ranges[key];
          return formatter.format(Math.round(delta), key);
        }
      }
    },
  },
};
</script>
