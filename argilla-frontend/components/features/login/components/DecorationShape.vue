<template>
  <svg
    class="deco--bottom"
    width="771"
    height="426"
    viewBox="0 0 771 426"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <ellipse
      cx="80"
      cy="77.5"
      rx="80"
      ry="77.5"
      transform="matrix(-1 0 0 1 515 104)"
      fill="url(#paint0_linear_5492_324)"
      fill-opacity="0.8"
    />
    <path
      d="M702.435 124.147C690.852 167.307 642.631 191.982 594.586 179.236C546.542 166.49 516.893 121.158 528.227 77.9322L702.435 124.147Z"
      fill="url(#paint1_linear_5492_324)"
    />
    <path
      d="M722.712 46.2153C711.129 89.3752 662.908 114.049 614.863 101.304C566.819 88.5582 537.17 43.2261 548.504 8.43773e-05L722.712 46.2153Z"
      fill="url(#paint2_linear_5492_324)"
    />
    <path
      d="M752.559 292.202C716.44 352.212 638.651 371.697 578.718 335.7L525.406 424.276C465.607 388.058 446.282 310.152 482.4 250.141C518.519 190.13 596.352 170.824 656.285 206.82L709.597 118.244C769.352 154.285 788.677 232.191 752.559 292.202Z"
      fill="#FF675F"
    />
    <path
      d="M181.513 326.13C181.513 380.886 225.902 425.274 280.658 425.274C335.414 425.274 379.802 380.886 379.802 326.13C379.802 271.374 335.414 226.986 280.658 226.986C225.902 226.986 181.513 271.374 181.513 326.13Z"
      fill="url(#paint3_linear_5492_324)"
    />
    <path
      d="M183.408 311.102C168.98 343.915 130.381 358.663 97.0533 344.115C63.7256 329.566 48.3363 291.147 62.5518 258.343L183.408 311.102Z"
      fill="url(#paint4_linear_5492_324)"
      fill-opacity="0.9"
    />
    <path
      d="M-2.74348e-05 371.436C14.4286 338.623 53.0274 323.874 86.3551 338.423C119.683 352.972 135.072 391.391 120.857 424.194L-2.74348e-05 371.436Z"
      fill="url(#paint5_linear_5492_324)"
      fill-opacity="0.9"
    />
    <path
      d="M494.736 418.9C451.341 435.651 402.455 413.562 385.352 369.497C368.248 325.431 389.522 276.043 432.713 259.104L494.736 418.9Z"
      fill="url(#paint6_linear_5492_324)"
    />
    <defs>
      <linearGradient
        id="paint0_linear_5492_324"
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
        id="paint1_linear_5492_324"
        x1="725.984"
        y1="162.793"
        x2="639.428"
        y2="295.562"
        gradientUnits="userSpaceOnUse"
      >
        <stop offset="0.0151877" stop-color="#FF675F" />
        <stop offset="1" stop-color="#F73D3D" />
      </linearGradient>
      <linearGradient
        id="paint2_linear_5492_324"
        x1="746.261"
        y1="84.8612"
        x2="659.705"
        y2="217.63"
        gradientUnits="userSpaceOnUse"
      >
        <stop offset="0.0151877" stop-color="#FF675F" />
        <stop offset="1" stop-color="#F73D3D" />
      </linearGradient>
      <linearGradient
        id="paint3_linear_5492_324"
        x1="415.747"
        y1="303.74"
        x2="220.608"
        y2="569.46"
        gradientUnits="userSpaceOnUse"
      >
        <stop offset="0.0151877" stop-color="#FF675F" />
        <stop offset="1" stop-color="#F73D3D" />
      </linearGradient>
      <linearGradient
        id="paint4_linear_5492_324"
        x1="106"
        y1="360.838"
        x2="79.194"
        y2="211.951"
        gradientUnits="userSpaceOnUse"
      >
        <stop offset="0.0151877" stop-color="#FF675F" />
        <stop offset="1" stop-color="#F73D3D" />
      </linearGradient>
      <linearGradient
        id="paint5_linear_5492_324"
        x1="69.3754"
        y1="414.539"
        x2="42.569"
        y2="265.651"
        gradientUnits="userSpaceOnUse"
      >
        <stop offset="0.0151877" stop-color="#FF675F" />
        <stop offset="1" stop-color="#F73D3D" />
      </linearGradient>
      <linearGradient
        id="paint6_linear_5492_324"
        x1="470.928"
        y1="315.43"
        x2="358.151"
        y2="476.337"
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
