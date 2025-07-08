# Design System - SEO Grove Inspired

Source: Comprehensive analysis of seogrove.ai design patterns and visual language

## Design System Principles

✅ Create a theme that can be applied to the rest of the website easily
✅ Don't hardcode fixes or variables but instead create a reusable system 
✅ Make it mobile friendly from the beginning
✅ Based on seogrove.ai CSS styles and design patterns

## Overview

This design system is inspired by the modern, tech-forward aesthetic of seogrove.ai, emphasizing clean interfaces, intelligent interactions, and a professional SEO tool appearance suitable for the PHP agentic framework.

## Color Palette

### Primary Colors
```css
:root {
  --grove-green: #22c55e;        /* Primary brand color */
  --grove-pink: #ef2b70;         /* Accent color for highlights */
  --grove-dark: #1e293b;         /* Primary text color */
  --grove-secondary: #64748b;    /* Secondary text color */
}
```

### Neutral Colors
```css
:root {
  --gray-50: #f8f9fa;           /* Light background */
  --gray-100: #e2e8f0;          /* Subtle borders */
  --gray-200: #cbd5e1;          /* Disabled elements */
  --gray-300: #94a3b8;          /* Placeholder text */
  --gray-400: #64748b;          /* Supporting text */
  --gray-500: #475569;          /* Body text */
  --gray-600: #334155;          /* Headings */
  --gray-700: #1e293b;          /* Dark text */
  --gray-800: #0f172a;          /* High contrast text */
  --gray-900: #020617;          /* Maximum contrast */
  --white: #ffffff;             /* Pure white */
}
```

### Semantic Colors
```css
:root {
  --success: #22c55e;           /* Success states */
  --warning: #f59e0b;           /* Warning states */
  --error: #ef4444;             /* Error states */
  --info: #3b82f6;              /* Information states */
}
```

## Typography

### Font Family
```css
:root {
  --font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  --font-mono: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace;
}
```

### Font Sizes
```css
:root {
  --text-xs: 0.625rem;     /* 10px */
  --text-sm: 0.75rem;      /* 12px */
  --text-base: 0.875rem;   /* 14px - Base size */
  --text-lg: 1rem;         /* 16px */
  --text-xl: 1.125rem;     /* 18px */
  --text-2xl: 1.25rem;     /* 20px */
  --text-3xl: 1.5rem;      /* 24px */
  --text-4xl: 2rem;        /* 32px */
  --text-5xl: 2.5rem;      /* 40px */
}
```

### Font Weights
```css
:root {
  --font-normal: 400;
  --font-medium: 500;
  --font-semibold: 600;
  --font-bold: 700;
  --font-extrabold: 800;
}
```

### Typography Classes
```css
.heading-1 {
  font-size: var(--text-5xl);
  font-weight: var(--font-extrabold);
  line-height: 1.2;
  color: var(--gray-700);
  letter-spacing: -0.025em;
}

.heading-2 {
  font-size: var(--text-4xl);
  font-weight: var(--font-bold);
  line-height: 1.3;
  color: var(--gray-700);
}

.heading-3 {
  font-size: var(--text-3xl);
  font-weight: var(--font-semibold);
  line-height: 1.4;
  color: var(--gray-600);
}

.body-text {
  font-size: var(--text-base);
  font-weight: var(--font-normal);
  line-height: 1.6;
  color: var(--gray-500);
}

.caption {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  line-height: 1.5;
  color: var(--gray-400);
}

.label {
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  line-height: 1.4;
  color: var(--gray-600);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
```

## Spacing System

### Spacing Scale
```css
:root {
  --space-1: 0.25rem;     /* 4px */
  --space-2: 0.5rem;      /* 8px */
  --space-3: 0.75rem;     /* 12px */
  --space-4: 1rem;        /* 16px */
  --space-5: 1.25rem;     /* 20px */
  --space-6: 1.5rem;      /* 24px */
  --space-8: 2rem;        /* 32px */
  --space-10: 2.5rem;     /* 40px */
  --space-12: 3rem;       /* 48px */
  --space-16: 4rem;       /* 64px */
  --space-20: 5rem;       /* 80px */
  --space-24: 6rem;       /* 96px */
}
```

## Border Radius

```css
:root {
  --radius-sm: 0.25rem;    /* 4px */
  --radius: 0.375rem;      /* 6px */
  --radius-md: 0.5rem;     /* 8px */
  --radius-lg: 0.75rem;    /* 12px */
  --radius-xl: 1rem;       /* 16px */
  --radius-full: 9999px;   /* Full round */
}
```

## Shadows

```css
:root {
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  --shadow-inner: inset 0 2px 4px 0 rgba(0, 0, 0, 0.06);
}
```

## Button Components

### Primary Button
```css
.btn-primary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-3) var(--space-6);
  background: linear-gradient(135deg, var(--grove-green), #16a34a);
  color: var(--white);
  border: none;
  border-radius: var(--radius-md);
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: var(--shadow-sm);
}

.btn-primary:hover {
  background: linear-gradient(135deg, #16a34a, #15803d);
  box-shadow: var(--shadow-md);
  transform: translateY(-1px);
}

.btn-primary:active {
  transform: translateY(0);
  box-shadow: var(--shadow-sm);
}
```

### Secondary Button
```css
.btn-secondary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-3) var(--space-6);
  background: var(--white);
  color: var(--gray-600);
  border: 1px solid var(--gray-200);
  border-radius: var(--radius-md);
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-secondary:hover {
  background: var(--gray-50);
  border-color: var(--gray-300);
  color: var(--gray-700);
}
```

## Card Components

### Basic Card
```css
.card {
  background: var(--white);
  border: 1px solid var(--gray-100);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  box-shadow: var(--shadow-sm);
  transition: all 0.2s ease;
}

.card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}
```

### Feature Card
```css
.feature-card {
  background: var(--white);
  border: 1px solid var(--gray-100);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  text-align: center;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.feature-card:hover {
  box-shadow: var(--shadow-lg);
  transform: translateY(-4px);
  border-color: var(--grove-green);
}

.feature-card:hover::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--grove-green), var(--grove-pink));
}
```

## Form Components

### Input Fields
```css
.input {
  width: 100%;
  padding: var(--space-3) var(--space-4);
  background: var(--white);
  border: 1px solid var(--gray-200);
  border-radius: var(--radius-md);
  font-size: var(--text-base);
  color: var(--gray-700);
  transition: all 0.2s ease;
}

.input:focus {
  outline: none;
  border-color: var(--grove-green);
  box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.1);
}
```

### Toggle Switch
```css
.toggle {
  position: relative;
  display: inline-block;
  width: 3rem;
  height: 1.5rem;
}

.toggle-slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: var(--gray-200);
  transition: 0.3s;
  border-radius: var(--radius-full);
}

.toggle input:checked + .toggle-slider {
  background-color: var(--grove-green);
}
```

## Layout Components

### Container
```css
.container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--space-6);
}
```

### Grid System
```css
.grid {
  display: grid;
  gap: var(--space-6);
}

.grid-cols-1 { grid-template-columns: repeat(1, 1fr); }
.grid-cols-2 { grid-template-columns: repeat(2, 1fr); }
.grid-cols-3 { grid-template-columns: repeat(3, 1fr); }

@media (max-width: 768px) {
  .grid-cols-2,
  .grid-cols-3 {
    grid-template-columns: 1fr;
  }
}
```

## Responsive Design

### Breakpoints
```css
:root {
  --breakpoint-sm: 640px;
  --breakpoint-md: 768px;
  --breakpoint-lg: 1024px;
  --breakpoint-xl: 1280px;
}
```

### Mobile-First Approach
```css
/* Mobile First - Base styles are for mobile */
.container {
  padding: 0 var(--space-4);
}

/* Tablet and up */
@media (min-width: 768px) {
  .container {
    padding: 0 var(--space-6);
  }
}

/* Desktop and up */
@media (min-width: 1024px) {
  .container {
    padding: 0 var(--space-8);
  }
}
```

## Animation and Interactions

### Hover Effects
```css
.hover-lift {
  transition: transform 0.2s ease;
}

.hover-lift:hover {
  transform: translateY(-2px);
}
```

### Loading Animations
```css
.loading-spinner {
  width: 2rem;
  height: 2rem;
  border: 2px solid var(--gray-200);
  border-top: 2px solid var(--grove-green);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
```

## Usage Guidelines

### Implementation Priority
1. **Color Palette**: Implement the green-focused color system first
2. **Typography**: Establish clear hierarchy with the defined font scales
3. **Button Components**: Create consistent interactive elements
4. **Card Components**: Build modular content containers
5. **Form Components**: Ensure accessible and user-friendly inputs
6. **Layout System**: Implement responsive grid and flexbox utilities

### Component Naming Convention
- Use BEM methodology: `.block__element--modifier`
- Keep class names descriptive and semantic
- Use utility classes for common patterns

### Accessibility Considerations
- Ensure color contrast ratios meet WCAG AA standards
- Provide focus indicators for keyboard navigation
- Use semantic HTML elements