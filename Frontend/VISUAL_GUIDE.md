# 🎨 Visual Flow & Screenshots Guide

## Page Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     SPLASH SCREEN                            │
│                      (page.tsx)                              │
│                                                              │
│              🛡️  [Animated Shield Logo]                      │
│                  with orbiting sparkles                      │
│                                                              │
│              Multi-Agent                                     │
│         Fake-News Detection Platform                         │
│                                                              │
│    An interactive dashboard for explainable results         │
│                                                              │
│              ●  ●  ●  (loading dots)                         │
│                                                              │
│              Auto-redirect after 3.5s ────────┐             │
└───────────────────────────────────────────────│─────────────┘
                                                │
                                                ▼
┌─────────────────────────────────────────────────────────────┐
│                      DASHBOARD                               │
│                 (dashboard/page.tsx)                         │
│                                                              │
│         Fake News Detector                                   │
│  Upload, analyze, and get instant AI-powered verdicts       │
│                                                              │
│  ┌─────────────────────────────────────────────────┐       │
│  │         INPUT SECTION (Initial State)            │       │
│  │                                                   │       │
│  │              ⊕  [Upload Button]                  │       │
│  │            (Circle with + icon)                  │       │
│  │                                                   │       │
│  │      ───────────────  or  ───────────────        │       │
│  │                                                   │       │
│  │     ┌──────────────────────────────────┐        │       │
│  │     │ Enter news link or text...       │        │       │
│  │     │                                  │        │       │
│  │     └──────────────────────────────────┘        │       │
│  │                                                   │       │
│  │           ✨ [ Detect ] (Glowing)               │       │
│  │                                                   │       │
│  └─────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────┘
                          │
                          │ Click Detect
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                  LOADING STATE                               │
│                                                              │
│              ╭─────────────╮                                │
│              │    ◐ ◑ ◒    │  (Rotating rings)             │
│              │             │                                 │
│              │ Analyzing...│                                │
│              ╰─────────────╯                                │
│                                                              │
│          ▬▬▬▬▬▬▬▬▬▬  (Progress bar)                        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                          │
                          │ After 3s
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                  RESULTS DISPLAY                             │
│                                                              │
│  ┌──────────────────┐    ┌──────────────────┐             │
│  │                   │    │                   │             │
│  │  ⚠️  FAKE        │    │     ⭕ 87%       │             │
│  │                   │    │   Confidence      │             │
│  │  Detection Verdict│    │                   │             │
│  │                   │    │  High Confidence  │             │
│  └──────────────────┘    └──────────────────┘             │
│                                                              │
│  ┌──────────────────────────────────────────────┐          │
│  │  🔑 Key Signals                               │          │
│  │                                                │          │
│  │  [Unverified source] [Sensational language]   │          │
│  │  [Missing citations] [Factually inaccurate]   │          │
│  │  [Poor grammar]                                │          │
│  └──────────────────────────────────────────────┘          │
│                                                              │
│  ┌──────────────────────────────────────────────┐          │
│  │  🌐 External Evidence (3)         [▼]        │          │
│  │  ┌────────────────────────────────────────┐  │ ←Click   │
│  │  │ 🐦 Expert debunks similar claim       │  │   to     │
│  │  │ Fact-checkers have thoroughly...      │  │  expand  │
│  │  │ [contradicting] → View source         │  │          │
│  │  └────────────────────────────────────────┘  │          │
│  │  ... (more evidence when expanded)            │          │
│  └──────────────────────────────────────────────┘          │
│                                                              │
│  ┌──────────────────────────────────────────────┐          │
│  │  Was this result helpful?                     │          │
│  │    👍 Yes          👎 No                      │          │
│  └──────────────────────────────────────────────┘          │
│                                                              │
│              ← New Detection                                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Component Layouts

### UploadButton
```
     ┌─────────────────┐
     │                 │
     │                 │
     │    ⬆️ Upload    │  ← Circular button
     │                 │    with neon glow
     │                 │
     └─────────────────┘
       128px × 128px
```

### InputBox
```
┌────────────────────────────────────────┐
│ Enter news link or text...             │  ← Glassmorphism
│                                        │    effect
│                                        │
└────────────────────────────────────────┘
  ▓▓▓▓▓▓▓▓▓▓▓▓▓  ← Animated gradient
                    (appears on focus)
```

### DetectButton
```
╔══════════════════════════════════╗
║     ✨ Detect                     ║  ← Gradient background
╚══════════════════════════════════╝    with glow pulse
  (Purple → Pink → Cyan gradient)
```

### ResultCard (Fake)
```
┌────────────────────────────────────┐
│  ⚠️                                │  ← Red theme
│                                    │
│  FAKE                              │
│                                    │
│  Detection Verdict                 │
└────────────────────────────────────┘
  Red glow and borders
```

### ResultCard (Real)
```
┌────────────────────────────────────┐
│  ✓                                 │  ← Green theme
│                                    │
│  REAL                              │
│                                    │
│  Detection Verdict                 │
└────────────────────────────────────┘
  Green glow and borders
```

### ConfidenceCircle
```
       ╭────────────╮
      ╱              ╲
     │                │
     │      87%       │  ← Animated fill
     │   Confidence   │    Color-coded
      ╲              ╱
       ╰────────────╯
    (Circular progress)
```

### EvidencePanel (Collapsed)
```
┌──────────────────────────────────────┐
│ 🔑 Key Signals                        │
│                                       │
│ [Signal 1] [Signal 2] [Signal 3]     │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│ 🌐 External Evidence (3)      [▼]    │  ← Click to expand
└──────────────────────────────────────┘
```

### EvidencePanel (Expanded)
```
┌──────────────────────────────────────┐
│ 🌐 External Evidence (3)      [▲]    │  ← Click to collapse
│                                       │
│  ┌────────────────────────────────┐  │
│  │ 🐦 Twitter Post Title          │  │
│  │ Snippet of the evidence...     │  │
│  │ [contradicting] → View source  │  │
│  └────────────────────────────────┘  │
│                                       │
│  ┌────────────────────────────────┐  │
│  │ 💬 Reddit Discussion           │  │
│  │ Community members have...      │  │
│  │ [supporting] → View source     │  │
│  └────────────────────────────────┘  │
│                                       │
│  ... (more evidence)                  │
└──────────────────────────────────────┘
```

## Color Indicators

### Verdict Colors
- 🔴 **Fake**: Red theme (`#ef4444`)
- 🟢 **Real**: Green theme (`#10b981`)
- 🟡 **Uncertain**: Yellow theme (`#f59e0b`)

### Evidence Types
- 🔴 **Contradicting**: Red border/background
- 🟢 **Supporting**: Green border/background

### Confidence Levels
- 🟢 **High (70-100%)**: Green
- 🟡 **Medium (40-69%)**: Yellow
- 🔴 **Low (0-39%)**: Red

## Animation Effects

### Entrance Animations
- **Fade in**: 0.5s
- **Scale up**: 0.5s with spring
- **Slide up**: 0.6-0.8s

### Hover Effects
- **Scale**: 1.05× (buttons)
- **Glow increase**: Border brightness +20%
- **Color shift**: Transition 0.3s

### Loading Animations
- **Rotating rings**: 1-2s per rotation
- **Pulsing glow**: 2s cycle
- **Scanning beam**: 2s vertical sweep

## Responsive Behavior

### Mobile (< 768px)
- Single column layout
- Reduced text sizes
- Smaller upload button
- Stacked result cards

### Tablet (768px - 1024px)
- Two-column results grid
- Medium text sizes
- Full-size components

### Desktop (> 1024px)
- Maximum width containers
- Optimized spacing
- All animations enabled
- Full neon effects

## Interactive States

### UploadButton
- **Default**: Purple border
- **Hover**: Neon purple glow
- **Drag over**: Neon cyan glow + scale

### InputBox
- **Default**: Subtle border
- **Focus**: Neon blue border + gradient line
- **Filled**: Persistent focus styling

### DetectButton
- **Default**: Gradient + glow pulse
- **Hover**: Scale 1.05 + shadow increase
- **Disabled**: 50% opacity, no hover
- **Loading**: Animated gradient sweep

### Evidence Cards
- **Default**: Subtle glow
- **Hover**: Increased border opacity
- **Expanded**: Full content visible

---

## Development Preview

**Server running at**: http://localhost:3000

**Pages**:
1. `/` - Splash screen (auto-redirects)
2. `/dashboard` - Main detection interface

**Key Files**:
- `src/app/page.tsx` - Splash
- `src/app/dashboard/page.tsx` - Dashboard
- `src/components/*.tsx` - All UI components
- `src/app/globals.css` - Theme & animations

---

Enjoy the futuristic fake news detection experience! 🚀✨
