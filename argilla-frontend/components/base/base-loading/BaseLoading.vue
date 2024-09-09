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
  <div class="loading">
    <div class="spinner">
      <svg
        width="608"
        height="116"
        viewBox="0 0 608 116"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          class="one"
          d="M246.18 1.99799H263.48L250.19 50.248H277L263.48 1.99799H281.15L305.84 89.728H288L281.23 65.658H246.06L239.41 89.728H222L246.18 1.99799Z"
          fill="black"
        />
        <path
          class="two"
          d="M315.49 25.678H331.28V34.208C333.661 31.0053 336.762 28.4066 340.331 26.6211C343.9 24.8355 347.839 23.9131 351.83 23.928V40.218C338.55 37.718 331.28 43.478 331.28 54.128V89.728H315.49V25.678Z"
          fill="black"
        />
        <path
          class="three"
          d="M361.73 93.988H380C382.13 97.868 387.52 100.508 394.29 100.508C404.44 100.508 411.21 94.238 411.21 82.958V82.078C406.32 88.218 398.92 91.478 389.9 91.478C374.49 91.478 359.7 79.828 359.7 57.768C359.7 35.708 374.49 23.928 389.9 23.928C398.9 23.928 406.32 27.188 411.21 33.458V25.678H427V82.958C427 102.258 412.84 115.288 394.29 115.288C379 115.288 365.62 107.778 361.73 93.988ZM393.73 76.688C404.01 76.688 411.28 69.798 411.28 57.768C411.28 45.738 404.01 38.768 393.73 38.768C383.45 38.768 376.19 45.658 376.19 57.768C376.19 69.878 383.54 76.688 393.69 76.688H393.73Z"
          fill="red"
        />
        <path
          class="four"
          d="M452.85 0.867956C454.096 0.824683 455.338 1.03823 456.498 1.49531C457.658 1.95239 458.711 2.64323 459.593 3.52488C460.475 4.40653 461.166 5.46013 461.623 6.62016C462.08 7.7802 462.293 9.02187 462.25 10.268C462.25 11.5024 462.007 12.7247 461.534 13.8652C461.062 15.0056 460.37 16.0419 459.497 16.9148C458.624 17.7876 457.588 18.48 456.447 18.9524C455.307 19.4248 454.084 19.668 452.85 19.668C451.616 19.668 450.393 19.4248 449.253 18.9524C448.112 18.48 447.076 17.7876 446.203 16.9148C445.33 16.0419 444.638 15.0056 444.166 13.8652C443.693 12.7247 443.45 11.5024 443.45 10.268C443.393 9.01841 443.597 7.77072 444.05 6.60451C444.502 5.4383 445.192 4.37916 446.077 3.49468C446.961 2.6102 448.02 1.91981 449.187 1.46754C450.353 1.01527 451.6 0.811068 452.85 0.867956V0.867956ZM445 25.678H460.79V89.728H445V25.678Z"
        />
        <path
          class="five"
          d="M477.54 1.99799H493.33V89.728H477.54V1.99799Z"
          fill="black"
        />
        <path
          class="six"
          d="M510.12 1.99799H525.91V89.728H510.12V1.99799Z"
          fill="black"
        />
        <path
          class="seven"
          d="M539.7 57.768C539.7 35.588 554.49 23.928 569.9 23.928C579.05 23.928 586.45 27.188 591.21 33.578V25.678H607V89.728H591.21V81.958C586.45 88.218 579.05 91.478 569.9 91.478C554.49 91.478 539.7 79.868 539.7 57.768ZM573.7 76.688C583.98 76.688 591.25 69.798 591.25 57.768C591.25 45.738 583.98 38.768 573.7 38.768C563.42 38.768 556.16 45.658 556.16 57.768C556.16 69.878 563.51 76.688 573.66 76.688H573.7Z"
          fill="black"
        />
        <path
          class="one"
          d="M44.3 90.0894C68.5674 90.0894 88.24 70.4167 88.24 46.1494C88.24 21.882 68.5674 2.20935 44.3 2.20935C20.0326 2.20935 0.359985 21.882 0.359985 46.1494C0.359985 70.4167 20.0326 90.0894 44.3 90.0894Z"
          fill="black"
        />
        <path
          class="one"
          d="M168.48 90.0093C145.242 89.9829 122.963 80.7399 106.531 64.308C90.0996 47.8762 80.8565 25.5974 80.8301 2.35931H111.4C111.419 17.4922 117.438 32 128.139 42.7006C138.839 53.4011 153.347 59.4208 168.48 59.4393V90.0093Z"
          fill="black"
        />
      </svg>
    </div>
  </div>
</template>

<script>
export default {
  methods: {},
};
</script>

<style lang="scss" scoped>
.loading {
  background: var(--bg-solid-grey-1);
  height: 100vh;
  width: 100vw;
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 9998;
}
.spinner {
  width: 200px;
  height: 80px;
  margin: auto;
  text-align: center;
  display: flex;
  position: absolute;
  bottom: 0;
  top: 0;
  right: 0;
  left: 0;
  z-index: 9999;
}

@keyframes letterflash {
  0% {
    fill: hsla(0, 92%, 60%, 40%);
  }
  50% {
    fill: hsl(0, 92%, 60%);
  }
  100% {
    fill: hsla(0, 92%, 60%, 40%);
  }
}
.one,
.two,
.three,
.four,
.five,
.six,
.seven {
  animation: letterflash 1.8s linear infinite;
  animation-fill-mode: backwards;
}

.seven {
  animation-delay: 0.5s;
}
.six {
  animation-delay: 0.4s;
}
.five {
  animation-delay: 0.4s;
}
.four {
  animation-delay: 0.3s;
}
.three {
  animation-delay: 0.2s;
}
.two {
  animation-delay: 0.1s;
}
.one {
  animation-delay: 0s;
}
</style>
