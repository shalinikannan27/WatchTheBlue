---
name: Abyssal Command
colors:
  surface: '#001524'
  surface-dim: '#001524'
  surface-bright: '#213c50'
  surface-container-lowest: '#00101c'
  surface-container-low: '#001e30'
  surface-container: '#022235'
  surface-container-high: '#0f2c40'
  surface-container-highest: '#1c374b'
  on-surface: '#cbe6ff'
  on-surface-variant: '#bac9cc'
  inverse-surface: '#cbe6ff'
  inverse-on-surface: '#173347'
  outline: '#849396'
  outline-variant: '#3b494c'
  surface-tint: '#00dbf0'
  primary: '#cdf8ff'
  on-primary: '#00363c'
  primary-container: '#1de9ff'
  on-primary-container: '#006570'
  inverse-primary: '#006973'
  secondary: '#ffb598'
  on-secondary: '#591d00'
  secondary-container: '#b14101'
  on-secondary-container: '#ffddd1'
  tertiary: '#b5ffeb'
  on-tertiary: '#00382e'
  tertiary-container: '#20eecc'
  on-tertiary-container: '#006858'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#94f1ff'
  primary-fixed-dim: '#00dbf0'
  on-primary-fixed: '#001f24'
  on-primary-fixed-variant: '#004f57'
  secondary-fixed: '#ffdbcd'
  secondary-fixed-dim: '#ffb598'
  on-secondary-fixed: '#360f00'
  on-secondary-fixed-variant: '#7e2c00'
  tertiary-fixed: '#3ffddb'
  tertiary-fixed-dim: '#00dfbf'
  on-tertiary-fixed: '#00201a'
  on-tertiary-fixed-variant: '#005144'
  background: '#001524'
  on-background: '#cbe6ff'
  surface-variant: '#1c374b'
typography:
  display-xl:
    fontFamily: Space Grotesk
    fontSize: 80px
    fontWeight: '700'
    lineHeight: '1.1'
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Space Grotesk
    fontSize: 48px
    fontWeight: '700'
    lineHeight: '1.2'
    letterSpacing: 0.02em
  headline-lg-mobile:
    fontFamily: Space Grotesk
    fontSize: 32px
    fontWeight: '700'
    lineHeight: '1.2'
  body-md:
    fontFamily: Hanken Grotesk
    fontSize: 18px
    fontWeight: '400'
    lineHeight: '1.6'
    letterSpacing: 0.01em
  body-sm:
    fontFamily: Hanken Grotesk
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.5'
  label-caps:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '500'
    lineHeight: '1'
    letterSpacing: 0.1em
  data-point:
    fontFamily: JetBrains Mono
    fontSize: 14px
    fontWeight: '700'
    lineHeight: '1'
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  unit: 4px
  gutter: 24px
  margin-desktop: 64px
  margin-mobile: 20px
  container-max: 1440px
---

## Brand & Style

This design system blends the high-precision aesthetics of aerospace telemetry with the fluid, mysterious beauty of marine conservation. It is designed to evoke a sense of urgent authority and scientific wonder—positioning the user as a mission controller for the planet's oceans.

The visual language is rooted in **Glassmorphism** and **Technical Editorial** styles. It utilizes a dark-mode-first approach to simulate the crushing depths of the midnight zone, contrasted by vibrant, bioluminescent data visualizations. The interface should feel like a high-end command deck: precise, data-rich, yet ethereal. It targets scientists, activists, and policy-makers who require "mission-critical" clarity combined with an emotionally resonant environmental narrative.

## Colors

The palette is anchored in the "Midnight Zone." The primary background utilizes `Deep Ocean Navy` for the base canvas, while `Midnight Blue` defines secondary containers and elevation layers. 

Accents are strictly bioluminescent. `Bioluminescent Cyan` and `Electric Aqua` are used for interactive elements, primary data threads, and glowing highlights. `Coral Orange` provides a high-energy contrast for CTAs and critical ecological markers. The `Muted Blue Gray` neutral is used for secondary metadata to prevent visual fatigue against the high-contrast accents. Status colors follow a "Sea State" logic: Aqua for healthy ecosystems, Amber for developing threats, and Coral Red for high-stress environmental anomalies.

## Typography

The typographic hierarchy balances impact with technical precision. 

- **Headlines:** Use `Space Grotesk`. Large display type should be set in massive uppercase with tight kerning to mimic mission patch graphics and NASA-style telemetry headers.
- **Body:** Use `Hanken Grotesk`. It offers a clean, contemporary feel with high legibility for long-form climate reports. A spacious line height is essential to maintain the "editorial" feel.
- **Technical Labels:** Use `JetBrains Mono` for all data points, coordinates, and system statuses. This monospaced font reinforces the "climate-tech" narrative and ensures tabular data aligns perfectly in complex dashboards.

## Layout & Spacing

This design system employs a **Fluid Grid** with an 8px base rhythmic unit. 

- **Desktop (1440px+):** 12-column grid, 24px gutters, 64px external margins. Layouts should utilize "asymmetric balance"—placing large data visualizations against concentrated blocks of technical text.
- **Tablet (768px - 1439px):** 8-column grid, 20px gutters. Content cards should begin to stack, but maintain side-bar navigation for quick data switching.
- **Mobile (Up to 767px):** 4-column grid, 16px gutters, 20px margins. Typography scales down significantly, and "massive" headers should wrap efficiently or use `headline-lg-mobile`.

Spacing should feel intentional and "airy" to represent the vastness of the ocean, using negative space to draw focus toward high-density data modules.

## Elevation & Depth

Depth is achieved through **Glassmorphism** rather than traditional drop shadows.

1.  **Base Layer:** The `Deep Ocean Navy` background, often featuring subtle, animated "atmospheric blurs" of Cyan and Sea Green to simulate bioluminescence.
2.  **Surface Layer:** Floating cards use a semi-transparent `Midnight Blue` (60-80% opacity) with a `Backdrop Blur` (20px-40px). 
3.  **Border Definition:** Surfaces must have a 1px solid border. Use `White` at 10% opacity for standard edges, or `Bioluminescent Cyan` at 40% opacity to indicate active or primary focus.
4.  **Glows:** Instead of shadows, use "Inner Glows" and "Outer Glows" (0px offset, high spread) in Cyan or Aqua to make high-priority data points appear self-illuminated.

## Shapes

The system uses a **Soft (1)** roundedness level to maintain a technical, engineered appearance. 

- **Standard Elements:** 4px (`0.25rem`) radius for buttons, input fields, and small tags.
- **Containers:** 8px (`0.5rem`) for cards and modal overlays.
- **Interactive Triggers:** Tab indicators and selection chips may use a "Pill" shape to distinguish them from data containers, but general UI follows a strict, geometric discipline to stay aligned with the NASA-inspired aesthetic.

## Components

- **Buttons:** Primary buttons feature a solid `Electric Aqua` fill with dark text. Secondary buttons are "Ghost" style: `1px` Cyan border, no fill, with a subtle outer glow on hover.
- **Glass Cards:** All containers must feature the frosted glass effect. Headers within cards should be separated by a `1px` muted line.
- **Telemetry Chips:** Small, monospaced tags used for displaying live metrics (e.g., "TEMP: 18.4°C"). These use a `Muted Blue Gray` background at 20% opacity.
- **Data Inputs:** Ultra-thin borders. When focused, the border color transitions to `Bioluminescent Cyan` with a matching 4px soft outer glow.
- **Status Indicators:** Small, circular "pulses." A "High Stress" state should feature a `Coral Red` dot with an animated concentric ring expanding outward to signal urgency.
- **Progress Bars:** Use a dual-gradient fill (Cyan to Aqua) against a dark, recessed track.