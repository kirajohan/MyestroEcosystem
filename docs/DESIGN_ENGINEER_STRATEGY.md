# 🎨 DESIGN ENGINEER STRATEGY — UI/UX & Components

**Role:** Senior Frontend Designer  
**Scope:** Broadcast UI, Inbox UI, Settings UI, Logs Dashboard, CSS improvements  
**Duration:** 8 hours design + implementation  
**Output:** Production-ready React components with Tailwind CSS

---

## 1. COMPONENT INVENTORY

### Current State Analysis

```
✅ COMPLETED COMPONENTS
├─ UserTable (admin/components/users/UserTable.tsx)
├─ StatsCard (admin/components/dashboard/StatsCard.tsx)
├─ ActivityChart (admin/components/dashboard/ActivityChart.tsx)
├─ Badge, Button, Input, Dialog (admin/components/ui/)
└─ AuthGuard, Sidebar, Header (admin/components/layout/)

❌ MISSING COMPONENTS (TO BUILD)
├─ BroadcastCreate (create new broadcast)
├─ BroadcastHistory (list past broadcasts)
├─ BroadcastPreview (preview before send)
├─ InboxList (list of admin messages)
├─ InboxThread (view specific conversation)
├─ InboxCompose (reply to user)
├─ LogsViewer (searchable logs)
├─ SettingsPanel (global toggles)
└─ NotificationAlert (toast/snackbar)
```

### Design System (Maestro Brand)

```
📐 SPACING
├─ xs: 4px    (0.25rem)
├─ sm: 8px    (0.5rem)
├─ md: 16px   (1rem)
├─ lg: 24px   (1.5rem)
├─ xl: 32px   (2rem)
└─ 2xl: 48px  (3rem)

🎨 COLOR PALETTE
├─ Primary (Trust + Learning)
│  ├─ Blue-500: #3B82F6 (Main action)
│  ├─ Blue-600: #2563EB (Hover/active)
│  └─ Blue-50:  #EFF6FF (Background)
├─ Success (Progress)
│  ├─ Green-500: #10B981 (Complete, positive)
│  ├─ Green-600: #059669 (Hover)
│  └─ Green-50:  #ECFDF5 (Background)
├─ Alert (Warning)
│  ├─ Orange-500: #F97316 (Warning)
│  ├─ Orange-600: #EA580C (Hover)
│  └─ Orange-50:  #FFF7ED (Background)
├─ Danger (Error)
│  ├─ Red-500:   #EF4444 (Error)
│  ├─ Red-600:   #DC2626 (Hover)
│  └─ Red-50:    #FEF2F2 (Background)
├─ Neutral (Text + Backgrounds)
│  ├─ Gray-900:  #111827 (Text)
│  ├─ Gray-700:  #374151 (Text secondary)
│  ├─ Gray-500:  #6B7280 (Text tertiary)
│  ├─ Gray-300:  #D1D5DB (Borders)
│  ├─ Gray-100:  #F3F4F6 (Backgrounds)
│  └─ Gray-50:   #F9FAFB (Light backgrounds)
└─ White: #FFFFFF (Surfaces)

📝 TYPOGRAPHY
├─ Font Family: -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif
├─ Headings:
│  ├─ H1: 32px, 700, 1.2 line-height
│  ├─ H2: 28px, 700, 1.3 line-height
│  ├─ H3: 24px, 600, 1.4 line-height
│  └─ H4: 20px, 600, 1.5 line-height
├─ Body:
│  ├─ Large: 16px, 400, 1.5 line-height
│  ├─ Regular: 14px, 400, 1.6 line-height
│  └─ Small: 12px, 400, 1.6 line-height
└─ Code: monospace, 12px, 1.4 line-height

🔲 SHADOWS
├─ sm:  0 1px 2px 0 rgba(0, 0, 0, 0.05)
├─ md:  0 4px 6px -1px rgba(0, 0, 0, 0.1)
├─ lg:  0 10px 15px -3px rgba(0, 0, 0, 0.1)
├─ xl:  0 20px 25px -5px rgba(0, 0, 0, 0.1)
└─ 2xl: 0 25px 50px -12px rgba(0, 0, 0, 0.1)

🎯 BORDER RADIUS
├─ sm: 0.375rem (6px)
├─ md: 0.5rem   (8px)
├─ lg: 0.75rem  (12px)
└─ xl: 1rem     (16px)
```

---

## 2. COMPONENT DESIGNS

### 2.1 BROADCAST COMPONENTS

#### BroadcastCreate

**Purpose:** Admin creates new broadcast message

**Features:**
- ✅ Message text editor (rich text with HTML support)
- ✅ Audience targeting (all users, by CEFR level, by registration status)
- ✅ Media upload (image, video, document)
- ✅ Preview before send
- ✅ Schedule (immediate or later)
- ✅ Save as draft

**Layout:**

```
┌──────────────────────────────────────────────────────────┐
│  📢 Broadcast Message                                    │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  📝 Message Content                                      │
│  ┌──────────────────────────────────────────────────┐   │
│  │ Write your message here...                       │   │
│  │ Supports <b>HTML</b>, <i>italic</i>, links, etc.│   │
│  │                                                  │   │
│  │                                                  │   │
│  └──────────────────────────────────────────────────┘   │
│                                                           │
│  🎬 Media (optional)                                    │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌──────────┐   │
│  │ 📸 Image│  │ 🎥 Video│  │ 📄 Docs │  │ + Upload │   │
│  └─────────┘  └─────────┘  └─────────┘  └──────────┘   │
│                                                           │
│  👥 Target Audience                                     │
│  ┌─ All Users (25,342)                                 │
│  ├─ By Level: [A1] [A2] [B1] [B2] [C1] [C2]           │
│  ├─ By Status: [Active] [Inactive] [New]              │
│  └─ Manual List: [upload CSV]                          │
│                                                           │
│  ⏰ Schedule                                            │
│  ┌─ Send Now  ○ Schedule Later                         │
│  │            [Date picker] [Time picker]              │
│                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ 👁️ Preview  │  │ 💾 Draft     │  │ ✅ Send Now  │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

**Tailwind Classes:**

```tsx
<div className="p-6 bg-white rounded-lg shadow-md">
  <h2 className="text-2xl font-bold text-gray-900 mb-6">📢 Broadcast Message</h2>
  
  {/* Message Editor */}
  <div className="mb-8">
    <label className="block text-sm font-semibold text-gray-700 mb-2">
      📝 Message Content
    </label>
    <textarea
      className="w-full p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
      rows={6}
      placeholder="Write your message here... Supports HTML, links, emoji"
    />
  </div>

  {/* Media Upload */}
  <div className="mb-8">
    <label className="block text-sm font-semibold text-gray-700 mb-3">
      🎬 Media (optional)
    </label>
    <div className="grid grid-cols-4 gap-4">
      <button className="p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition">
        📸 Image
      </button>
      <button className="p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition">
        🎥 Video
      </button>
      <button className="p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition">
        📄 Document
      </button>
      <button className="p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition">
        ➕ Upload
      </button>
    </div>
  </div>

  {/* Target Audience */}
  <div className="mb-8">
    <label className="block text-sm font-semibold text-gray-700 mb-3">
      👥 Target Audience
    </label>
    <div className="space-y-4 bg-gray-50 p-4 rounded-lg">
      <div className="flex items-center">
        <input type="radio" id="all" name="audience" defaultChecked />
        <label htmlFor="all" className="ml-2">All Users (25,342)</label>
      </div>
      <div className="flex items-center">
        <input type="radio" id="level" name="audience" />
        <label htmlFor="level" className="ml-2">By CEFR Level:</label>
      </div>
      <div className="flex gap-2 ml-6 flex-wrap">
        {['A1', 'A2', 'B1', 'B2', 'C1', 'C2'].map(level => (
          <button key={level} className="px-3 py-1 border border-gray-300 rounded hover:bg-blue-500 hover:text-white transition">
            {level}
          </button>
        ))}
      </div>
    </div>
  </div>

  {/* Buttons */}
  <div className="flex gap-3 pt-6 border-t border-gray-200">
    <button className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition">
      👁️ Preview
    </button>
    <button className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition">
      💾 Save as Draft
    </button>
    <button className="ml-auto px-6 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition">
      ✅ Send Now
    </button>
  </div>
</div>
```

#### BroadcastHistory

**Purpose:** View past broadcasts, delivery status, statistics

**Features:**
- ✅ List all broadcasts with filters (date, status, audience size)
- ✅ Show delivery stats (sent, failed, pending)
- ✅ View individual broadcast details
- ✅ Resend or delete broadcasts

**Layout:**

```
┌──────────────────────────────────────────────────────────┐
│ 📊 Broadcast History                                     │
├──────────────────────────────────────────────────────────┤
│ 🔍 [Search...] | Status: [All ▼] | Date: [Last 30 days ▼]
├──────────────────────────────────────────────────────────┤
│                                                           │
│ Date       │ Message                │ Audience │ Status  │
│ ───────────┼────────────────────────┼──────────┼─────────│
│ Jan 15     │ "Learn English Today"  │ 1,234    │ ✅ Sent  │
│ Jan 14     │ "Holiday Offer: 20%"   │ 5,678    │ ✅ Sent  │
│ Jan 13     │ "Quiz Results"         │ 234      │ ⏳ Pend. │
│ Jan 12     │ "New Feature Alert"    │ 9,876    │ ⚠️ Fail  │
│ ───────────┼────────────────────────┼──────────┼─────────│
│                                                           │
│ [Pagination: 1 2 3 ... 45]                               │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

---

### 2.2 INBOX COMPONENTS

#### InboxList

**Purpose:** Admin inbox — view all user messages

**Split Layout:**
- Top half: Conversations list
- Bottom half: User list (for sending unsolicited messages)

**Features:**
- ✅ Search conversations
- ✅ Filter by status (unread, archived, resolved)
- ✅ Sort by date or priority
- ✅ Quick reply with templates
- ✅ Archive/delete conversations

**Layout:**

```
┌─────────────────────────────────────────────────────────────┐
│  📬 Inbox                                 [Settings] [Help]  │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  MESSAGES TAB (Top Half)                                     │
│  ────────────────────────────────────────────────────────   │
│  🔍 [Search conversations...] | Status: [All ▼] | [Filters] │
│  ├─────────────────────────────────────────────────────────┤
│  │                                                           │
│  │ 🔴 User: Ahmed (@ahmed_uz)              Jan 15, 14:32   │
│  │    "Hi, I have a question about..."                      │
│  │    [Unread: 3]                                           │
│  │                                                           │
│  │ ○  User: Fatima (@fatima_ru)            Jan 14, 09:15   │
│  │    "Thank you for the lesson!"                           │
│  │    [Unread: 0] ✓ Replied                                 │
│  │                                                           │
│  │ ○  User: Shashnur (@shasha_en)          Jan 13, 22:40   │
│  │    "Can I get a refund?"                                 │
│  │    [Unread: 0] ⚠️  Critical                             │
│  │                                                           │
│  │ [Load more...]                                           │
│  │                                                           │
│  └─────────────────────────────────────────────────────────┘
│
│  USERS TAB (Bottom Half)                                     │
│  ────────────────────────────────────────────────────────   │
│  🔍 [Search users...] | Active: [All ▼] | Level: [All ▼]   │
│  ├─────────────────────────────────────────────────────────┤
│  │                                                           │
│  │ 👤 Ahmed (@ahmed_uz)              Level: B1  ✅ Active  │
│  │    Last seen: Jan 15, 10:22                              │
│  │    [Send message]                                        │
│  │                                                           │
│  │ 👤 Fatima (@fatima_ru)            Level: A2  ✅ Active  │
│  │    Last seen: Jan 14, 15:45                              │
│  │    [Send message]                                        │
│  │                                                           │
│  └─────────────────────────────────────────────────────────┘
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

#### InboxThread

**Purpose:** Read and reply to specific user message

**Features:**
- ✅ View full conversation history (all messages from user)
- ✅ Reply with HTML formatting
- ✅ Use quick-reply templates
- ✅ Attach media/documents
- ✅ Mark as resolved/archived

**Layout:**

```
┌────────────────────────────────────────────────────────────┐
│  ← Back to Inbox  │  👤 Ahmed (@ahmed_uz)  │  Level: B1   │
├────────────────────────────────────────────────────────────┤
│                                                              │
│  📅 Jan 15, 14:32                                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Hi, I have a question about lesson 5. I don't        │  │
│  │ understand the grammar. Can you explain?             │  │
│  │                                                      │  │
│  │ - Ahmed                                              │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  📅 Jan 15, 15:00 (ADMIN REPLY)                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Hi Ahmed,                                             │  │
│  │                                                      │  │
│  │ Great question! In lesson 5, we cover the           │  │
│  │ <b>past continuous</b>. You use "was" + verb(-ing) │  │
│  │                                                      │  │
│  │ Example: I <b>was studying</b> when you called.     │  │
│  │                                                      │  │
│  │ Try the practice exercises and let me know!         │  │
│  │                                                      │  │
│  │ - Admin                                              │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ═════════════════════════════════════════════════════════ │
│                                                              │
│  ✉️ YOUR REPLY                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ <b>Bold</b> <i>Italic</i> [Link] | 📎 Attach       │  │
│  ├──────────────────────────────────────────────────────┤  │
│  │                                                      │  │
│  │ Type your response...                                │  │
│  │                                                      │  │
│  │                                                      │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌─ Quick Replies ▼  ┐                                     │
│  │ • "Thanks for the question!"                           │
│  │ • "Can you provide more details?"                      │
│  │ • "I'll look into this for you"                        │
│  └────────────────────┘                                     │
│                                                              │
│  [Draft]  [Resolve] [Archive]  ➡️ [Send Reply]            │
│                                                              │
└────────────────────────────────────────────────────────────┘
```

---

### 2.3 LOGS DASHBOARD

**Purpose:** View structured logs, search, filter

**Features:**
- ✅ Real-time log stream
- ✅ Search by keyword, user_id, event type
- ✅ Filter by service (bot, backend, admin)
- ✅ Filter by level (ERROR, WARN, INFO, DEBUG)
- ✅ Export logs to CSV
- ✅ Set up alerts for errors

**Layout:**

```
┌────────────────────────────────────────────────────────────┐
│  📋 Logs Viewer                        [🔄 Auto-refresh]  │
├────────────────────────────────────────────────────────────┤
│                                                              │
│  🔍 Search: [keywords...] | Service: [All ▼] | Level: [All ▼]
│                                                              │
│  Date/Time        │ Service │ Level  │ Message             │
│  ──────────────────┼─────────┼────────┼─────────────────────│
│  Jan 15 14:32:10 │ bot     │ 🟢 INF │ User message sent  │
│  Jan 15 14:31:55 │ backend │ 🟢 INF │ User created       │
│  Jan 15 14:31:20 │ bot     │ 🟠 WRN │ Slow response (3s) │
│  Jan 15 14:30:45 │ backend │ 🔴 ERR │ DB connection lost │
│  Jan 15 14:30:10 │ admin   │ 🟢 INF │ Broadcast sent     │
│  ──────────────────┼─────────┼────────┼─────────────────────│
│                                                              │
│  [Export CSV]  [Set Alert]  [< Previous] [Next >]           │
│                                                              │
│  Showing 1-50 of 2,341 logs                                 │
│                                                              │
└────────────────────────────────────────────────────────────┘
```

---

### 2.4 SETTINGS PANEL

**Purpose:** Global bot toggles

**Features:**
- ✅ GLOBAL BOT on/off (freeze all bot functionality except for admins)
- ✅ AI GLOBAL on/off (disable AI responses, show fallback)
- ✅ Broadcast queue stats
- ✅ Database stats
- ✅ Maintenance mode

**Layout:**

```
┌────────────────────────────────────────────────────────────┐
│  ⚙️ Settings                                                │
├────────────────────────────────────────────────────────────┤
│                                                              │
│  🤖 BOT SETTINGS                                            │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ Global Bot Status: [OFF/ON Toggle]                   │  │
│  │ When OFF: Users get "Sorry, bot is under maintenance"│  │
│  │           Admins can still use all features          │  │
│  │                                                      │  │
│  │ Last toggled: Jan 15, 14:20 by Admin                │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                              │
│  🧠 AI SETTINGS                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ Global AI Status: [OFF/ON Toggle]                    │  │
│  │ When OFF: AI features disabled, fallback message     │  │
│  │ Model: gpt-4o-mini (OpenRouter)                      │  │
│  │ Cost: $0.03/1K tokens                                │  │
│  │                                                      │  │
│  │ Last toggled: Jan 14, 10:00 by Admin                │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                              │
│  📊 SYSTEM STATS                                            │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ Active Users: 12,345                                 │  │
│  │ Messages Today: 45,678                               │  │
│  │ Broadcast Queue: 123 pending                         │  │
│  │ Database Size: 2.3 GB                                │  │
│  │ Redis Memory: 512 MB                                 │  │
│  │ Uptime: 14 days                                      │  │
│  │                                                      │  │
│  │ Last health check: Jan 15, 14:25 ✅ All OK          │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                              │
└────────────────────────────────────────────────────────────┘
```

---

## 3. IMPLEMENTATION CHECKLIST

### Phase 1: BroadcastCreate Component (2 hours)
- [ ] Create `admin/components/broadcast/BroadcastCreate.tsx`
- [ ] HTML editor (textarea with formatting hints)
- [ ] Audience targeting (multi-select)
- [ ] Media upload (drag-drop or button)
- [ ] Preview modal
- [ ] Save draft to localStorage
- [ ] Send button (calls API)
- [ ] Success/error toast notifications

### Phase 2: BroadcastHistory Component (1.5 hours)
- [ ] Create `admin/components/broadcast/BroadcastHistory.tsx`
- [ ] Data table (broadcast list)
- [ ] Search + filters
- [ ] Resend/delete buttons
- [ ] Pagination
- [ ] Stats cards (sent, failed, pending)

### Phase 3: InboxList + InboxThread (3 hours)
- [ ] Create `admin/components/inbox/InboxList.tsx` (messages tab)
- [ ] Create `admin/components/inbox/UsersList.tsx` (users tab)
- [ ] Create `admin/components/inbox/InboxThread.tsx` (detail view)
- [ ] Create `admin/components/inbox/InboxCompose.tsx` (reply form)
- [ ] HTML formatting buttons
- [ ] Quick reply templates
- [ ] Archive/resolve buttons
- [ ] Conversation history display

### Phase 4: LogsViewer Component (2 hours)
- [ ] Create `admin/components/logs/LogsViewer.tsx`
- [ ] Real-time log stream (WebSocket or polling)
- [ ] Search input
- [ ] Filter dropdowns (service, level, date range)
- [ ] Export button (CSV)
- [ ] Syntax highlighting for log entries
- [ ] Auto-scroll to bottom

### Phase 5: SettingsPanel Component (1 hour)
- [ ] Create `admin/components/settings/SettingsPanel.tsx`
- [ ] Toggle switches for Global Bot, Global AI
- [ ] System stats cards
- [ ] Health check status
- [ ] Last action audit trail

### Phase 6: Tailwind CSS Improvements (1.5 hours)
- [ ] Audit current CSS in all components
- [ ] Replace custom CSS with Tailwind utilities
- [ ] Ensure consistent spacing (4px grid)
- [ ] Add dark mode support (if needed)
- [ ] Test responsive design (mobile, tablet, desktop)
- [ ] Improve color contrast (WCAG AA)

---

## 4. RESPONSIVE BREAKPOINTS

```tailwind
Mobile First Approach:
- sm: 640px   (tablets)
- md: 768px   (small laptops)
- lg: 1024px  (desktops)
- xl: 1280px  (large desktops)
- 2xl: 1536px (very large displays)

Example:
<div className="w-full md:w-1/2 lg:w-1/3">
  Full width on mobile, half on tablet, third on desktop
</div>
```

---

## 5. ACCESSIBILITY REQUIREMENTS

- ✅ Color contrast ≥ 4.5:1 for text
- ✅ ARIA labels on all interactive elements
- ✅ Keyboard navigation (Tab, Enter, Escape)
- ✅ Focus visible on all buttons
- ✅ Semantic HTML (button, input, label)
- ✅ Form labels associated with inputs
- ✅ Alt text on all images
- ✅ Error messages linked to form fields

---

## 6. ANIMATION GUIDELINES

- **Durations:** 150ms (micro), 300ms (standard), 500ms (complex)
- **Easing:** ease-in-out (natural), ease-out (popover), ease-in (exit)
- **Reduce Motion:** Respect `prefers-reduced-motion` media query

```tsx
// Example: Fade in animation
<div className="animate-fadeIn">Content</div>

// Custom animation in tailwind.config.js:
animation: {
  fadeIn: 'fadeIn 300ms ease-out',
  slideIn: 'slideIn 300ms ease-out',
}
```

---

## 7. SUCCESS METRICS

- ✅ All components pass WCAG AA accessibility audit
- ✅ Components work on mobile (375px), tablet (768px), desktop (1024px+)
- ✅ Color palette matches Maestro brand
- ✅ Tailwind utilities used consistently (no custom CSS)
- ✅ Animations smooth at 60fps
- ✅ Components documented in Storybook (optional)
- ✅ Load time < 3 seconds
- ✅ Bundle size < 200KB (all components)

