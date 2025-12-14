# 🎨 UI / UX & Design System

## Design Philosophy
- Simple
- Calm
- Trustworthy
- Finance without fear

Inspired by:
- Mint
- Notion
- Calm
- Google Material simplicity

---

## Core UI Principles
- One action per screen
- Plain language (no finance jargon)
- Visual buckets instead of tables
- Positive reinforcement

---

## UI Design Mockups (Desktop Web App)

### 1. Landing Page (Public Home)
*High-conversion SaaS landing page focusing on trust and value.*
![Landing Page](ui/11_landing_page.png)
![Landing Page Features](ui/11b_landing_features.png)
![Landing Page Footer](ui/11c_landing_footer.png)

### 2. Login Screen
*Clean, split-screen design with brand aesthetics and distinct login form.*
![Login Screen](ui/01_login.png)

### 3. Forgot Password
*Simple recovery flow.*
![Forgot Password](ui/12_forgot_password.png)

### 4. Email Verification
*Confirm email address before proceeding.*
![Email Verification](ui/15_email_verification.png)

### 5. Dashboard (Populated)
*Information-rich sidebar layout with clear buckets and financial health visualization.*
![Dashboard](ui/02_dashboard.png)

### 6. Dashboard (Empty State)
*First-time user experience guiding to onboarding.*
![Empty Dashboard](ui/16_dashboard_empty.png)

### 7. Financial Health Analysis
*Detailed breakdown of financial health metrics and recommendations.*
![Analysis Detail](ui/18_analysis_detail.png)

### 8. Onboarding (Risk Profile)
*Step-by-step form with clear progress indication and accessible inputs.*
![Onboarding](ui/03_onboarding.png)

### 9. Action Plan
*Detailed view of priority actions and monthly financial allocation.*
![Action Plan](ui/04_action_plan.png)

### 10. Financial Snapshot (Input)
*Clean form for entering monthly financial data with real-time health insights.*
![Financial Snapshot](ui/05_financial_snapshot.png)

### 11. Assets & Liabilities
*Split-view interface for managing net worth components.*
![Assets & Liabilities](ui/06_assets_liabilities.png)

### 12. Goal Setting
*Card-based interface for defining financial goals.*
![Goal Setting](ui/07_goals_input.png)

### 13. Investment Comparison
*Educational tool to explore and compare investment options.*
![Investment Comparison](ui/17_investment_compare.png)

### 14. Monthly Check-in
*Interactive progress tracking form with visual feedback.*
![Monthly Check-in](ui/08_monthly_checkin.png)

### 15. AI Explanation (RAG)
*Contextual AI assistance explaining financial decisions.*
![RAG Explanation](ui/09_rag_explanation.png)

### 16. Settings & Profile
*Comprehensive settings for user preferences and data management.*
![Settings](ui/10_settings_profile.png)

### 17. 404 Error Page
*Friendly error state with clear navigation.*
![404 Error](ui/13_404_error.png)

### 18. Privacy Policy
*Clear, readable legal documentation layout.*
![Privacy Policy](ui/14_privacy_policy.png)

---

## Key Screens

### 1. Home / Dashboard
- Progress bar
- Current net worth
- "You are on track" message

### 2. Profile & Financial Snapshot
- Card-based inputs
- Optional advanced fields
- Save & continue anytime

### 3. Analysis Screen
- What's working
- What needs fixing
- Priority warnings

### 4. Bucket View
- Emergency
- Debt
- Short-term goals
- Long-term wealth

Each bucket shows:
- Current amount
- Target
- Next action

### 5. Plan Screen
- Step-by-step actions
- Monthly targets
- Simple charts

### 6. Tracking & Nudges
- Monthly check-in
- "Did you invest this month?"
- Encouraging messages

---

## Design System

### Colors
- **Primary**: Calm Blue (#4A90E2)
- **Success**: Soft Green (#7ED321)
- **Warning**: Amber (#F5A623)
- **Error**: Muted Red (#D0021B)
- **Critical**: Red-Orange (#FF6B6B)
- **Background**: Light Gray (#F8F9FA)
- **Card**: White (#FFFFFF)

### Typography
- **Headings**: Inter / SF Pro Display (Bold)
- **Body**: Inter / SF Pro Text (Regular)
- **Numbers**: SF Mono / Roboto Mono (for clarity)

### Components
- **Cards**: Rounded corners (12px), shadow (0 2px 8px rgba(0,0,0,0.1))
- **Progress bars**: Height 8px, rounded
- **Sliders**: Material Design style
- **Chips**: Pills with background colors (Low / Medium / High risk)
- **Buttons**: 
  - Primary: Blue, rounded (8px)
  - Secondary: Outlined
  - Danger: Red

### Spacing
- Base unit: 8px
- Small: 8px
- Medium: 16px
- Large: 24px
- XL: 32px

### Animations
- Micro-interactions: 200ms ease
- Page transitions: 300ms ease-in-out
- Hover effects: 150ms
- Loading states: Skeleton screens

---

## Interaction Patterns

### Loading States
- Skeleton screens for content
- Spinner for actions
- Progress indicators for multi-step

### Empty States
- Friendly illustrations
- Clear call-to-action
- Helpful guidance text

### Error States
- Non-aggressive red
- Clear error message
- Suggested fix
- Retry option

### Success States
- Celebration animations (confetti)
- Encouraging messages
- Progress visualization

---

## Accessibility
- WCAG 2.1 AA compliance
- Color contrast ratio > 4.5:1
- Keyboard navigation support
- Screen reader friendly
- Focus indicators
- Alt text for all images

---

## Responsive Design
- Mobile-first approach
- Breakpoints:
  - Mobile: 320px - 767px
  - Tablet: 768px - 1023px
  - Desktop: 1024px+
- Touch-friendly targets (min 44x44px)
- Swipe gestures for mobile

---

## UX Rule
If a user needs explanation → show tooltip  
If still confused → show "Why this?" (RAG explanation)

---

**Last Updated:** 2025-12-13  
**Design Version:** 2.0  
**Mockups:** 6 core screens generated
