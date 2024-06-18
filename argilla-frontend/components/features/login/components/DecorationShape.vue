<template>
  <svg
    class="deco--bottom"
    width="768"
    height="426"
    viewBox="0 0 768 426"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <ellipse
      cx="80"
      cy="77.5"
      rx="80"
      ry="77.5"
      transform="matrix(-1 0 0 1 535.681 81.3438)"
      fill="url(#paint0_linear_5489_5425)"
      fill-opacity="0.8"
    />
    <path
      d="M699.425 124.148C687.842 167.308 639.621 191.982 591.576 179.236C543.532 166.491 513.883 121.159 525.217 77.9325L699.425 124.148V124.148Z"
      fill="url(#paint1_linear_5489_5425)"
    />
    <path
      d="M719.702 46.2155C708.119 89.3753 659.898 114.05 611.854 101.304C563.809 88.5583 534.16 43.2263 545.494 0.000206481L719.702 46.2155V46.2155Z"
      fill="url(#paint2_linear_5489_5425)"
    />
    <path
      d="M749.549 292.202C713.431 352.213 635.641 371.697 575.708 335.7L522.397 424.277C462.597 388.058 443.272 310.152 479.391 250.141C515.509 190.13 593.343 170.824 653.276 206.821L706.587 118.244C766.343 154.285 785.667 232.191 749.549 292.202Z"
      fill="#FF675F"
    />
    <path
      d="M170.504 326.13C170.504 380.886 214.892 425.275 269.648 425.275C324.404 425.275 368.792 380.886 368.792 326.13C368.792 271.374 324.404 226.986 269.648 226.986C214.892 226.986 170.504 271.374 170.504 326.13Z"
      fill="url(#paint3_linear_5489_5425)"
    />
    <path
      d="M172.399 306.102C157.97 338.915 119.371 353.664 86.0435 339.115C52.7158 324.566 37.3265 286.147 51.542 253.344L172.399 306.102Z"
      fill="url(#paint4_linear_5489_5425)"
      fill-opacity="0.9"
    />
    <path
      d="M-0.00985357 371.436C14.4187 338.623 53.0176 323.875 86.3453 338.423C119.673 352.972 135.062 391.391 120.847 424.195L-0.00985357 371.436Z"
      fill="url(#paint5_linear_5489_5425)"
      fill-opacity="0.9"
    />
    <path
      d="M482.85 419.346C432.727 431.142 382.45 399.591 370.347 348.775C358.244 297.958 389.035 247.1 438.962 235.068L482.85 419.346Z"
      fill="url(#paint6_linear_5489_5425)"
    />
    <defs>
      <linearGradient
        id="paint0_linear_5489_5425"
        x1="-29.0036"
        y1="59.9977"
        x2="122.023"
        y2="272.284"
        gradientUnits="userSpaceOnUse"
      >
        <stop offset="0.0151877" stop-color="#FF675F" />
        <stop offset="1" stop-color="#F73D3D" />
      </linearGradient>
      <linearGradient
        id="paint1_linear_5489_5425"
        x1="722.974"
        y1="162.794"
        x2="636.418"
        y2="295.563"
        gradientUnits="userSpaceOnUse"
      >
        <stop offset="0.0151877" stop-color="#FF675F" />
        <stop offset="1" stop-color="#F73D3D" />
      </linearGradient>
      <linearGradient
        id="paint2_linear_5489_5425"
        x1="743.251"
        y1="84.8613"
        x2="656.695"
        y2="217.63"
        gradientUnits="userSpaceOnUse"
      >
        <stop offset="0.0151877" stop-color="#FF675F" />
        <stop offset="1" stop-color="#F73D3D" />
      </linearGradient>
      <linearGradient
        id="paint3_linear_5489_5425"
        x1="404.737"
        y1="303.74"
        x2="209.598"
        y2="569.461"
        gradientUnits="userSpaceOnUse"
      >
        <stop offset="0.0151877" stop-color="#FF675F" />
        <stop offset="1" stop-color="#F73D3D" />
      </linearGradient>
      <linearGradient
        id="paint4_linear_5489_5425"
        x1="94.9906"
        y1="355.839"
        x2="68.1842"
        y2="206.951"
        gradientUnits="userSpaceOnUse"
      >
        <stop offset="0.0151877" stop-color="#FF675F" />
        <stop offset="1" stop-color="#F73D3D" />
      </linearGradient>
      <linearGradient
        id="paint5_linear_5489_5425"
        x1="69.3656"
        y1="414.539"
        x2="42.5592"
        y2="265.652"
        gradientUnits="userSpaceOnUse"
      >
        <stop offset="0.0151877" stop-color="#FF675F" />
        <stop offset="1" stop-color="#F73D3D" />
      </linearGradient>
      <linearGradient
        id="paint6_linear_5489_5425"
        x1="472.366"
        y1="302.489"
        x2="324.673"
        y2="461.903"
        gradientUnits="userSpaceOnUse"
      >
        <stop offset="0.0151877" stop-color="#FF675F" />
        <stop offset="1" stop-color="#F73D3D" />
      </linearGradient>
    </defs>
  </svg>
</template>

<style lang="scss" scoped>
%deco {
  display: none;
  @include media(">desktop") {
    display: block;
    position: absolute;
    height: auto;
  }
}
.deco {
  &--bottom {
    right: 0;
    bottom: 0;
    width: clamp(560px, 70%, 800px);
    @extend %deco;
  }
}
</style>
