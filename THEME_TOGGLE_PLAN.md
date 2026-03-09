# Light/Dark Mode Toggle — Implementation Plan

## Audit Findings

### CSS Architecture — GOOD NEWS
Colors are already defined as CSS custom properties on `:root` in `variables.css`.
The architecture is clean: only 8 core color variables need light-mode overrides.

**Core color variables (dark defaults):**
| Variable | Dark value | Role |
|---|---|---|
| `--color-bg` | `#0a0e13` | Page background |
| `--color-surface` | `#111820` | Card/panel surface |
| `--color-border` | `#1e2d3d` | Borders |
| `--color-text` | `#e8edf2` | Body text |
| `--color-text-muted` | `#8899aa` | Secondary text |
| `--color-accent` | `#00bcd4` | Cyan brand accent |
| `--color-accent-dim` | `rgba(0,188,212,0.10)` | Tinted accent fills |
| `--color-bg-elevated` | `#1a1f2e` | Sidebar, elevated surfaces |

**Legacy aliases** (`--color-bg-primary`, `--color-text-primary`, etc.) resolve via `var()` to the above — they do NOT need overrides.

**Two edge cases with hardcoded values:**
1. `auth.css` (login page, inline `<style>`) has its own `:root` block — needs its own `[data-theme="light"]` override block added to that same `<style>` tag.
2. `navigation.css` — `.site-header` background uses a raw `rgba(10, 14, 19, 0.88)` literal (not a variable). Needs one targeted override.

**Semantic/status colors** (`--color-accent-secondary` green, `--color-accent-tertiary` gold, `--color-accent-warning` orange, `--color-accent-critical` red) are intentional signal colors — leave them unchanged in light mode; they carry meaning.

**Shadow variables** use `rgba(0,0,0,…)` — these naturally lighten in light mode because `--color-bg` changes. No override needed, but may want slightly reduced opacity overrides for visual weight.

---

## Files to Change

| File | What changes |
|---|---|
| `app/static/css/core/variables.css` | Add `[data-theme="light"] :root { … }` block (or `html[data-theme="light"]`) |
| `app/static/css/layout/navigation.css` | Override the one hardcoded `rgba(10, 14, 19, 0.88)` on `.site-header` |
| `app/templates/base.html` | (1) Add `data-theme` attr to `<html>`, (2) add toggle to sidebar footer, (3) expand `<script>` block |
| `app/templates/auth/login.html` | Add `data-theme` attr to `<html>` + add light-mode block to inline `<style>` |
| `app/static/js/app.js` | (currently empty) — Not used; theme JS goes inline in base.html |

No new files. No new dependencies. No layout/typography/spacing changes.

---

## Step-by-Step Implementation

### Step 1 — Light theme CSS block in `variables.css`

Add immediately after the existing `:root { … }` block:

```css
html[data-theme="light"] {
  --color-bg:          #f0f2f5;
  --color-surface:     #ffffff;
  --color-border:      #d0d8e4;
  --color-text:        #1a1f2e;
  --color-text-muted:  #5a6a7a;
  --color-accent:      #0097a7;          /* deepened for contrast on light */
  --color-accent-dim:  rgba(0, 151, 167, 0.10);
  --color-bg-elevated: #e8ecf0;

  /* Legacy standalone vars (not aliases) */
  --color-border-hover:   #a0afc0;
  --color-text-tertiary:  #4a5568;
  --color-text-dim:       #718096;

  /* Softer shadows on light background */
  --shadow-sm:   0 1px 2px rgba(0, 0, 0, 0.10);
  --shadow-md:   0 2px 8px rgba(0, 0, 0, 0.15);
  --shadow-glow: 0 0 20px rgba(0, 151, 167, 0.12);
}
```

**Palette rationale:**
- Background: `#f0f2f5` (warm off-white, not glaring pure white)
- Surface: `#ffffff` (cards/panels pop against bg)
- Text: `#1a1f2e` (the dark bg color — same hue family, strong contrast)
- Accent: `#0097a7` (cyan slightly deepened — same hue, passes WCAG AA on `#f0f2f5`)

### Step 2 — Fix the one hardcoded color in `navigation.css`

The `.site-header` background `rgba(10, 14, 19, 0.88)` is essentially `--color-bg` at 88% opacity. Add:

```css
html[data-theme="light"] .site-header {
  background-color: rgba(240, 242, 245, 0.92);   /* --color-bg light value */
}
```

This goes at the bottom of `navigation.css`.

### Step 3 — Light mode block in `auth/login.html` inline `<style>`

The login page has its own `:root` inside an inline `<style>`. Add the same override block there (trimmed to only the 7 vars it actually uses). Also add `data-theme` to the `<html>` tag and the same theme-init script.

### Step 4 — Toggle markup in `base.html`

Inside `.nav-sidebar-footer`, above the username link:

```html
<div class="theme-toggle-row">
  <span class="theme-toggle-label">Light mode</span>
  <button
    id="theme-toggle"
    class="theme-toggle-btn"
    role="switch"
    aria-checked="false"
    aria-label="Toggle light mode"
  >
    <span class="theme-toggle-track">
      <span class="theme-toggle-thumb"></span>
    </span>
  </button>
</div>
```

CSS for the toggle goes at the bottom of `navigation.css` (same file — no new file needed).

### Step 5 — JavaScript (inline in `base.html`)

Logic, added to the existing `<script>` block:

```javascript
// Theme initialisation — runs before paint to prevent flash
(function() {
  const saved = localStorage.getItem('theme');
  if (saved === 'light') {
    document.documentElement.setAttribute('data-theme', 'light');
  }
})();

// Toggle handler (runs after DOM ready — safe because it only touches the button)
document.addEventListener('DOMContentLoaded', function () {
  const btn = document.getElementById('theme-toggle');
  if (!btn) return;

  function syncToggle() {
    const isLight = document.documentElement.getAttribute('data-theme') === 'light';
    btn.setAttribute('aria-checked', String(isLight));
  }

  syncToggle();

  btn.addEventListener('click', function () {
    const isLight = document.documentElement.getAttribute('data-theme') === 'light';
    if (isLight) {
      document.documentElement.removeAttribute('data-theme');
      localStorage.setItem('theme', 'dark');
    } else {
      document.documentElement.setAttribute('data-theme', 'light');
      localStorage.setItem('theme', 'light');
    }
    syncToggle();
  });
});
```

The IIFE at the top runs synchronously — before the browser paints — eliminating any flash.

### Step 6 — Login page parity

- `<html>` gets `data-theme` attribute.
- Same IIFE theme-init script added before `</body>`.
- Light-mode override block added to the inline `<style>`.

---

## Flash-of-Wrong-Theme Prevention

The IIFE (`(function(){ … })()`) runs synchronously during HTML parsing, before any CSS is applied or any frame is painted. This is the standard, reliable technique — no extra attributes or server-side work required.

---

## What Is NOT Changed

- No layout properties
- No spacing or typography
- No font sizes, weights, or line-heights
- No semantic/status accent colors (green, gold, orange, red)
- No `cie-syntax.css` syntax highlight colors (these are fine as-is)
- No new CSS frameworks or dependencies
- No server-side code

---

## Verification Checklist

- [ ] Toggle persists across page reload (localStorage read in IIFE)
- [ ] Toggle persists across navigation (base.html IIFE fires on every page)
- [ ] Login page respects saved preference
- [ ] No layout shifts or unstyled flashes on load
- [ ] Dark mode is default when no preference stored
- [ ] Both themes render legibly
