<template>
  <div class="engineering-visual">
    <div class="visual-label"><span class="status-dot" /> ЦИФРОВАЯ МОДЕЛЬ → ГОТОВАЯ ДЕТАЛЬ</div>
    <svg viewBox="0 0 640 530" role="img" aria-label="Техническая иллюстрация: геометрия детали и её цифровая модель">
      <defs>
        <linearGradient id="metal" x1="0" x2="1" y1="0" y2="1"><stop stop-color="#b7c7dc"/><stop offset=".45" stop-color="#657d9e"/><stop offset="1" stop-color="#27364c"/></linearGradient>
        <linearGradient id="side" x1="0" x2="1"><stop stop-color="#3b5272"/><stop offset="1" stop-color="#152337"/></linearGradient>
        <linearGradient id="blue" x1="0" x2="1" y2="1"><stop stop-color="#6498ff"/><stop offset="1" stop-color="#1750bb"/></linearGradient>
        <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="#32435a" stroke-width=".6"/></pattern>
        <filter id="shadow"><feGaussianBlur stdDeviation="18"/></filter>
      </defs>
      <path d="M30 376 340 194 625 360 315 540Z" fill="url(#grid)" opacity=".5"/>
      <ellipse cx="340" cy="431" rx="200" ry="45" fill="#000" opacity=".5" filter="url(#shadow)"/>
      <g class="part-float">
        <path d="m144 267 235-122 151 84v102L296 458l-152-88Z" fill="url(#side)" stroke="#7c96b8" stroke-width="1"/>
        <path d="m144 267 235-122 151 84-234 128Z" fill="url(#metal)" stroke="#adc0d8" stroke-width="1.5"/>
        <path d="M296 357v101M144 299l152 89 234-128M144 331l152 89 234-128" fill="none" stroke="#6f86a4" opacity=".25"/>
        <path d="m189 270 190-98 105 58-188 102Z" fill="#0d1725" stroke="#aabbd0"/>
        <path d="m189 270 190-98v48l-147 76Z" fill="#253950"/>
        <path d="m232 296 147-76 61 34-144 78Z" fill="#496587"/>
        <path d="m192 284 184-95M201 290l175-89M212 295l164-84" stroke="#6d86a6" opacity=".4"/>
        <g fill="#101a29" stroke="#a5bad5"><ellipse cx="171" cy="266" rx="8" ry="4"/><ellipse cx="379" cy="158" rx="8" ry="4"/><ellipse cx="501" cy="231" rx="8" ry="4"/><ellipse cx="296" cy="343" rx="8" ry="4"/></g>
        <path d="m325 362 158-86v56l-158 87Z" fill="#121e30" stroke="#627a9b"/>
        <g stroke="#6684ad" stroke-width="4"><path d="M341 362v41M358 353v41M375 344v41M392 335v41M409 326v41M426 317v41M443 308v41M460 299v41"/></g>
        <path d="m144 270 152 88v100l-152-88Z" fill="#345178" opacity=".25"/>
        <g fill="#243d5d" stroke="#7d9cc3"><ellipse cx="177" cy="323" rx="9" ry="13" transform="rotate(-30 177 323)"/><ellipse cx="259" cy="371" rx="9" ry="13" transform="rotate(-30 259 371)"/></g>
        <path d="m144 167 235-122 151 84-234 128Z" fill="url(#blue)" fill-opacity=".09" stroke="#4e8cff" stroke-width="1.5"/>
        <path d="m144 167 152 90 234-128M144 167v36l152 89 234-128v-35M296 257v35" fill="none" stroke="#4e8cff"/>
        <path d="m171 168 208-108 123 69-206 113Z" fill="none" stroke="#4e8cff" opacity=".6"/>
        <path d="M171 168v98M379 60v98M501 129v102M296 242v101" stroke="#5c90e9" stroke-dasharray="3 7" opacity=".6"/>
      </g>
      <g stroke="#6384af" fill="none" stroke-width="1"><path d="m134 390-25 15 171 97 26-15M109 398v14M280 495v14"/><path d="m550 230 27 17v108l-27-16M571 247h12M571 355h12"/><path d="m505 149 52-30h52M189 231l-68-39H42"/></g>
      <g fill="#8da8cd" font-family="monospace" font-size="11"><text x="167" y="474" transform="rotate(29 167 474)">ПАРАМЕТРИЧЕСКАЯ ГЕОМЕТРИЯ</text><text x="565" y="110">CAD</text><text x="42" y="180">ПОСАДОЧНЫЕ МЕСТА</text><text x="590" y="310" transform="rotate(-90 590 310)">FDM / СЛОЙ ЗА СЛОЕМ</text></g>
      <circle cx="505" cy="149" r="4" fill="#4d89ff"/><circle cx="189" cy="231" r="4" fill="#4d89ff"/>
    </svg>
    <div class="visual-caption"><span>01 / ИНЖЕНЕРНАЯ ВИЗУАЛИЗАЦИЯ</span><span>XYZ ↗</span></div>
  </div>
</template>
