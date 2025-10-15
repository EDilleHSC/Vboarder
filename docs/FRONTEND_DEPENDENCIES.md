# VBoarder Frontend Dependencies & Setup

**Date:** October 14, 2025
**Location:** `vboarder_frontend/nextjs_space`

---

## 📦 Required Dependencies

The upgraded chat UI requires the following npm packages:

### Core Dependencies (Should Already Be Installed)

- `react` - Core React library
- `next` - Next.js framework
- `typescript` - TypeScript support
- `tailwindcss` - Utility-first CSS

### UI Component Dependencies

- `framer-motion` - Animation library
- `react-markdown` - Markdown rendering
- `remark-gfm` - GitHub Flavored Markdown support
- `lucide-react` - Icon library

### shadcn/ui Components

The chat UI uses these shadcn components (should already be installed):

- `button`
- `card`
- `input`
- `textarea`
- `badge`
- `scroll-area`
- `separator`
- `toggle`
- `tabs`
- `avatar`
- `select`

---

## 🚀 Installation Steps

### Step 1: Navigate to Frontend Directory

```bash
cd /mnt/d/ai/projects/vboarder/vboarder_frontend/nextjs_space
```

### Step 2: Check Existing Dependencies

```bash
# List all dependencies
npm list --depth=0

# Check specific packages
npm list framer-motion
npm list react-markdown
npm list remark-gfm
```

### Step 3: Install Missing Dependencies

```bash
# Install all required packages
npm install framer-motion react-markdown remark-gfm

# Or install individually:
npm install framer-motion
npm install react-markdown
npm install remark-gfm
```

### Step 4: Verify Installation

```bash
# Check package.json
cat package.json | grep -E "framer-motion|react-markdown|remark-gfm"

# Should show:
# "framer-motion": "^11.x.x",
# "react-markdown": "^9.x.x",
# "remark-gfm": "^4.x.x",
```

---

## 🎨 UI Component Status

### Already Installed (via shadcn/ui)

If you've been using the VBoarder frontend, these should already exist:

```
components/ui/button.tsx
components/ui/card.tsx
components/ui/input.tsx
components/ui/textarea.tsx
components/ui/badge.tsx
components/ui/select.tsx
```

### May Need to Install

These shadcn components might not be installed yet:

```bash
# Check if components exist
ls components/ui/scroll-area.tsx
ls components/ui/separator.tsx
ls components/ui/toggle.tsx
ls components/ui/tabs.tsx
ls components/ui/avatar.tsx
```

### Install Missing shadcn Components

```bash
# If using shadcn CLI:
npx shadcn@latest add scroll-area
npx shadcn@latest add separator
npx shadcn@latest add toggle
npx shadcn@latest add tabs
npx shadcn@latest add avatar
```

---

## 🔧 Troubleshooting

### Problem: "Cannot find module 'framer-motion'"

**Solution:**

```bash
npm install framer-motion
```

### Problem: "Cannot find module 'react-markdown'"

**Solution:**

```bash
npm install react-markdown remark-gfm
```

### Problem: "Module not found: Can't resolve '@/components/ui/scroll-area'"

**Solution:**

```bash
npx shadcn@latest add scroll-area
# Or manually create the component (see shadcn docs)
```

### Problem: npm install fails with "EACCES"

**Solution:**

```bash
# Fix permissions (Linux/WSL)
sudo chown -R $USER:$USER /mnt/d/ai/projects/vboarder/vboarder_frontend/nextjs_space/node_modules

# Or try with --legacy-peer-deps
npm install --legacy-peer-deps
```

### Problem: TypeScript errors in chat/page.tsx

**Symptoms:**

- "Property 'inline' does not exist on type..."
- "Type 'any' is not assignable..."

**Solution:**
These are expected if you're using strict TypeScript. The component includes `any` types for ReactMarkdown component props. To fix:

1. Add proper types from react-markdown
2. Or adjust tsconfig.json temporarily:

```json
{
  "compilerOptions": {
    "strict": false
  }
}
```

---

## 📋 Complete Package List

### package.json Dependencies

Your `package.json` should include:

```json
{
  "dependencies": {
    "next": "14.2.33",
    "react": "^18",
    "react-dom": "^18",
    "typescript": "^5",
    "framer-motion": "^11.0.0",
    "react-markdown": "^9.0.0",
    "remark-gfm": "^4.0.0",
    "lucide-react": "latest",
    "@radix-ui/react-avatar": "^1.0.0",
    "@radix-ui/react-scroll-area": "^1.0.0",
    "@radix-ui/react-separator": "^1.0.0",
    "@radix-ui/react-toggle": "^1.0.0",
    "@radix-ui/react-tabs": "^1.0.0",
    "tailwindcss": "^3.3.0"
  }
}
```

---

## 🚀 Launch Sequence

### 1. Install Dependencies

```bash
cd /mnt/d/ai/projects/vboarder/vboarder_frontend/nextjs_space
npm install
```

### 2. Verify Environment

```bash
# Check .env.local exists
cat .env.local
# Should contain: NEXT_PUBLIC_API_BASE=http://127.0.0.1:3738
```

### 3. Start Development Server

```bash
npm run dev
```

**Expected Output:**

```
▲ Next.js 14.2.33
- Local:        http://localhost:3000
- Ready in 2.1s
```

### 4. Open Chat UI

```
http://localhost:3000/chat
```

---

## ✅ Pre-Launch Checklist

- [ ] `cd` to `vboarder_frontend/nextjs_space`
- [ ] Run `npm list framer-motion` - should show version
- [ ] Run `npm list react-markdown` - should show version
- [ ] Run `npm list remark-gfm` - should show version
- [ ] Check `.env.local` has `NEXT_PUBLIC_API_BASE=http://127.0.0.1:3738`
- [ ] Run `npm run dev` - should start without errors
- [ ] Open `http://localhost:3000/chat` - should load UI
- [ ] Backend running on port 3738
- [ ] Can select agent from dropdown
- [ ] Can type and send message
- [ ] Message appears in chat
- [ ] Agent response appears

---

## 🎯 Quick Install Command

For a fresh install or reset:

```bash
cd /mnt/d/ai/projects/vboarder/vboarder_frontend/nextjs_space

# Install all dependencies at once
npm install framer-motion react-markdown remark-gfm

# Install missing shadcn components (if needed)
npx shadcn@latest add scroll-area separator toggle tabs avatar

# Start dev server
npm run dev
```

Then open: http://localhost:3000/chat

---

## 📚 Component Documentation

### Framer Motion

Used for smooth animations and transitions

- Docs: https://www.framer.com/motion/
- Used in: Page transitions, message animations

### React Markdown

Renders markdown in agent responses

- Docs: https://github.com/remarkjs/react-markdown
- Used in: Message bubbles, code blocks

### remark-gfm

GitHub Flavored Markdown support

- Docs: https://github.com/remarkjs/remark-gfm
- Used in: Tables, strikethrough, task lists

### Lucide React

Beautiful icon library

- Docs: https://lucide.dev/
- Used in: Bot, User, Send, Trash, Sparkles icons

---

## 🐛 Common Errors & Fixes

### Error: "Module not found: Can't resolve 'framer-motion'"

**Fix:**

```bash
npm install framer-motion
```

### Error: "Cannot find module 'react-markdown'"

**Fix:**

```bash
npm install react-markdown remark-gfm
```

### Error: "Component 'ScrollArea' not found"

**Fix:**

```bash
npx shadcn@latest add scroll-area
```

### Error: npm install hangs or times out

**Fix:**

```bash
# Clear npm cache
npm cache clean --force

# Try again
npm install

# Or use yarn
yarn add framer-motion react-markdown remark-gfm
```

---

**Document Version:** 1.0
**Last Updated:** October 14, 2025
**Status:** Ready for Installation
