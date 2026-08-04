<template>
  <a-config-provider :theme="themeConfig">
    <div class="stage" aria-hidden="true">
      <div class="stage-bg"></div>
    </div>

    <!-- Inline SVG icon sprite -->
    <svg width="0" height="0" style="position: absolute" aria-hidden="true">
      <defs>
        <symbol id="i-logo" viewBox="0 0 40 40">
          <rect x="2" y="2" width="36" height="36" rx="12" fill="rgba(255,255,255,.08)" stroke="currentColor" stroke-width="1.6" />
          <path d="M8 16.5c3.8-3 7.2-3 11 0s7.2 3 11 0" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
          <path d="M8 23c3.8-3 7.2-3 11 0s7.2 3 11 0" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
          <circle cx="24" cy="12.5" r="1.8" fill="currentColor" stroke="none" />
        </symbol>
        <symbol id="i-history" viewBox="0 0 24 24">
          <circle cx="12" cy="12" r="8" />
          <path d="M12 7.5V12l3 2" />
          <path d="M4 5.5 6 8" />
        </symbol>
        <symbol id="i-map" viewBox="0 0 24 24">
          <path d="M9 4 3 6v14l6-2 6 2 6-2V4l-6 2-6-2Z" />
          <path d="M9 4v14M15 6v14" />
        </symbol>
        <symbol id="i-plus" viewBox="0 0 24 24">
          <path d="M12 5v14M5 12h14" />
        </symbol>
        <symbol id="i-pin" viewBox="0 0 24 24">
          <path d="M12 21s7-6.1 7-11.2A7 7 0 0 0 5 9.8C5 14.9 12 21 12 21Z" />
          <circle cx="12" cy="9.5" r="2.4" />
        </symbol>
        <symbol id="i-drop" viewBox="0 0 24 24">
          <path d="M12 3.5s6 6.3 6 10.3a6 6 0 0 1-12 0c0-4 6-10.3 6-10.3Z" />
        </symbol>
        <symbol id="i-sun" viewBox="0 0 24 24">
          <circle cx="12" cy="12" r="3.6" />
          <path d="M12 2.5v2.4M12 19.1v2.4M2.5 12h2.4M19.1 12h2.4M5 5l1.7 1.7M17.3 17.3 19 19M19 5l-1.7 1.7M6.7 17.3 5 19" />
        </symbol>
        <symbol id="i-arrow" viewBox="0 0 24 24">
          <path d="M19 12H5M11 6l-6 6 6 6" />
        </symbol>
        <symbol id="i-edit" viewBox="0 0 24 24">
          <path d="M4 20h4.5L20 8.5a2.1 2.1 0 0 0-3-3L5.5 17 4 20Z" />
          <path d="m14 7 3 3" />
        </symbol>
        <symbol id="i-save" viewBox="0 0 24 24">
          <path d="M5 3.5h12L20.5 7v13.5h-15V3.5Z" />
          <path d="M8 3.5V9h8V3.5M8 20.5v-6h8v6" />
        </symbol>
        <symbol id="i-close" viewBox="0 0 24 24">
          <path d="M6 6l12 12M18 6 6 18" />
        </symbol>
        <symbol id="i-pic" viewBox="0 0 24 24">
          <rect x="3.5" y="4.5" width="17" height="15" rx="2.5" />
          <circle cx="9" cy="10" r="1.8" />
          <path d="m5.5 17.5 4.5-4.5 3 3 3.5-3.5 3 3" />
        </symbol>
        <symbol id="i-star" viewBox="0 0 24 24">
          <path d="m12 3.5 2.6 5.3 5.9.9-4.3 4.1 1 5.8-5.2-2.7-5.2 2.7 1-5.8-4.3-4.1 5.9-.9L12 3.5Z" />
        </symbol>
        <symbol id="i-spark" viewBox="0 0 24 24">
          <path d="M12 2.5c.8 5.2 3.8 8.2 9 9-5.2.8-8.2 3.8-9 9-.8-5.2-3.8-8.2-9-9 5.2-.8 8.2-3.8 9-9Z" />
          <path d="M19 15.5c.35 1.8 1.2 2.65 3 3-1.8.35-2.65 1.2-3 3-.35-1.8-1.2-2.65-3-3 1.8-.35 2.65-1.2 3-3Z" />
        </symbol>
        <symbol id="i-walk" viewBox="0 0 24 24">
          <circle cx="13.5" cy="4.5" r="1.8" />
          <path d="M12 8.5 9.5 14l2.8 1.6L11 20.5M11.5 9.5l2 3.1 3 1.6-1.2 3M7.5 8.5 6 14.5l3 1" />
        </symbol>
        <symbol id="i-bed" viewBox="0 0 24 24">
          <path d="M3.5 18.5V6M3.5 12h17v6.5M3.5 15.5h17" />
          <path d="M17.5 8.5a2 2 0 0 1 2 2" />
        </symbol>
        <symbol id="i-fork" viewBox="0 0 24 24">
          <path d="M7 3v6a2.5 2.5 0 0 0 5 0V3M9.5 11.5V21M17 3c0 3-2 4.5-2 7.5V21" />
        </symbol>
        <symbol id="i-wallet" viewBox="0 0 24 24">
          <path d="M4 7.5h14a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a1.5 1.5 0 0 1-1.5-1.5v-9A1.5 1.5 0 0 1 5 7.5Z" />
          <path d="M4 7.5V6.5A1.5 1.5 0 0 1 5.5 5H18" />
          <circle cx="16.5" cy="13.5" r="1" fill="currentColor" stroke="none" />
        </symbol>
        <symbol id="i-chart" viewBox="0 0 24 24">
          <path d="M4 20h16M7 16v-5M12 16V7M17 16v-8" />
        </symbol>
        <symbol id="i-globe" viewBox="0 0 24 24">
          <circle cx="12" cy="12" r="8.5" />
          <path d="M3.5 12h17M12 3.5c2.6 2.3 3.9 5.2 3.9 8.5s-1.3 6.2-3.9 8.5c-2.6-2.3-3.9-5.2-3.9-8.5s1.3-6.2 3.9-8.5Z" />
        </symbol>
        <symbol id="i-grid" viewBox="0 0 24 24">
          <rect x="4" y="4" width="7" height="7" rx="2" />
          <rect x="13" y="4" width="7" height="7" rx="2" />
          <rect x="4" y="13" width="7" height="7" rx="2" />
          <rect x="13" y="13" width="7" height="7" rx="2" />
        </symbol>
        <symbol id="i-eye" viewBox="0 0 24 24">
          <path d="M2.5 12S6 5.5 12 5.5 21.5 12 21.5 12 18 18.5 12 18.5 2.5 12 2.5 12Z" />
          <circle cx="12" cy="12" r="2.8" />
        </symbol>
      </defs>
    </svg>

    <main class="app-main">
      <router-view />
    </main>
  </a-config-provider>
</template>

<script setup lang="ts">
import { theme } from 'ant-design-vue'

const themeConfig = {
  algorithm: theme.darkAlgorithm,
  token: {
    colorPrimary: '#ffcf7d',
    colorInfo: '#ffcf7d',
    colorBgBase: '#07141b',
    colorBgContainer: 'rgba(255,255,255,0.1)',
    colorBgElevated: 'rgba(10,26,35,0.96)',
    colorText: '#ffffff',
    colorTextSecondary: 'rgba(255,255,255,0.72)',
    colorTextTertiary: 'rgba(255,255,255,0.46)',
    colorBorder: 'rgba(255,255,255,0.2)',
    colorBorderSecondary: 'rgba(255,255,255,0.14)',
    borderRadius: 12,
    fontFamily: "'Inter','Noto Sans SC',-apple-system,'Segoe UI',Roboto,sans-serif"
  }
}
</script>
