# Thesis Project Workflow - Visual Explanation

## 🏗️ System Architecture (Big Picture)

```
┌─────────────────────────────────────────────────────────────┐
│                    YOUR DAILY WORKFLOW                       │
└─────────────────────────────────────────────────────────────┘

                    ┌──────────────┐
                    │   GitHub     │  ← Single Source of Truth
                    │  Repository  │     (Code + Context Files)
                    └──────┬───────┘
                           │
                           │ git push/pull
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
   ┌─────────┐      ┌──────────┐      ┌──────────┐
   │ Notion  │◄────►│   YOU    │◄────►│  Local   │
   │Database │      │(Computer)│      │  Files   │
   └────┬────┘      └──────────┘      └────┬─────┘
        │                                    │
        │                                    │
        └────────────┬───────────────────────┘
                     │
           ┌─────────┴─────────┐
           │                   │
           ▼                   ▼
    ┌─────────────┐    ┌─────────────┐
    │ Claude Chat │    │ Claude Code │
    │  (Browser)  │    │  (Terminal) │
    └─────────────┘    └─────────────┘
```

---

## 📅 DAILY WORKFLOW (တစ်နေ့ တာ workflow)

### 🌅 MORNING (မနက်ခင်း - ၅ မိနစ်)

```
Step 1: Check Current Status
┌──────────────────────────────────────────┐
│  YOU: Open Terminal                      │
│  ↓                                       │
│  cd ~/thesis-implementation              │
│  ↓                                       │
│  cat CURRENT_STATUS.md                   │
│  ↓                                       │
│  "ငါ မနေ့က ဘာလုပ်ထားလဲ? ဒီနေ့ ဘာဆက်လုပ်မလဲ?"  │
└──────────────────────────────────────────┘

Step 2: Update Today's Plan
┌──────────────────────────────────────────┐
│  vim CURRENT_STATUS.md                   │
│  ↓                                       │
│  Update:                                 │
│  - ✅ Yesterday: Completed MOEAD basics  │
│  - 🚧 Today: Weight vector generation    │
│  - 📋 Next: Testing on ZDT1             │
│  ↓                                       │
│  Save & Exit                             │
└──────────────────────────────────────────┘

Step 3: Sync to GitHub
┌──────────────────────────────────────────┐
│  git add CURRENT_STATUS.md               │
│  ↓                                       │
│  git commit -m "Daily plan 2026-04-21"   │
│  ↓                                       │
│  git push                                │
│  ↓                                       │
│  "GitHub မှာ latest status ရှိပြီ!"        │
└──────────────────────────────────────────┘

Step 4: Update Notion (Optional - 2 မိနစ်)
┌──────────────────────────────────────────┐
│  Open Notion "Current Status" page       │
│  ↓                                       │
│  Copy today's plan from terminal         │
│  ↓                                       │
│  Paste & format nicely                   │
│  ↓                                       │
│  "Notion က human-readable ဖြစ်သွားပြီ"      │
└──────────────────────────────────────────┘
```

---

### 💻 DEVELOPMENT TIME (Coding - Claude Code သုံးတယ်)

```
┌───────────────────────────────────────────────────────────┐
│                  CLAUDE CODE WORKFLOW                      │
└───────────────────────────────────────────────────────────┘

YOU: Need to write code
  ↓
Open Terminal
  ↓
┌─────────────────────────────────────────────┐
│ $ thesis-code "MOEAD weight vectors ရေးပေး" │  ← Your alias
└─────────────────────────────────────────────┘
  ↓
  ↓ (Claude Code loads context)
  ↓
┌──────────────────────────────────────────┐
│ Claude Code ကို auto-load လုပ်တယ်:        │
│                                          │
│ 1. PROJECT_CONTEXT.md                    │
│    → ငါ့ project structure ကို သိတယ်     │
│    → ဘယ် files တွေ ရှိလဲ သိတယ်           │
│                                          │
│ 2. CURRENT_STATUS.md                     │
│    → ဒီနေ့ ဘာလုပ်နေလဲ သိတယ်              │
│    → ဘယ် phase မှာ ရောက်နေလဲ သိတယ်       │
│    → ဘာ issue တွေ ရှိလဲ သိတယ်            │
└──────────────────────────────────────────┘
  ↓
Claude Code generates code
  ↓
┌──────────────────────────────────────────┐
│ # Generated: moead.py                    │
│                                          │
│ def generate_weight_vectors(n, m):       │
│     """                                  │
│     Based on your project context,       │
│     using Das and Dennis method...       │
│     """                                  │
│     # ... code ...                       │
└──────────────────────────────────────────┘
  ↓
YOU: Copy code → Save to file
  ↓
Test locally
  ↓
Works? → Commit to GitHub
```

**Claude Code က session ပိတ်လိုက်ရင်?**
```
No problem!
  ↓
Next time သုံးတဲ့အခါ:
  ↓
$ thesis-code "continue ဆက်လုပ်မယ်"
  ↓
Claude Code က ပြန်ပြီး:
- PROJECT_CONTEXT.md ကို ဖတ်တယ် → structure သိပြီ
- CURRENT_STATUS.md ကို ဖတ်တယ် → ဘယ်မှာ ရပ်ထားလဲ သိပြီ
  ↓
"ဘာဆက်လုပ်မလဲ?" ← Ready to continue!
```

---

### 💭 PLANNING TIME (Strategy - Claude Chat သုံးတယ်)

```
┌────────────────────────────────────────────────────────┐
│                  CLAUDE CHAT WORKFLOW                   │
└────────────────────────────────────────────────────────┘

YOU: Need to plan/discuss strategy
  ↓
Open Browser → claude.ai
  ↓
┌─────────────────────────────────────────┐
│ Notion MCP connected? ✅                │
│   ↓                                     │
│   Say: "Read my Notion Project Context" │
│   ↓                                     │
│   Claude Chat auto-loads:               │
│   - Project overview                    │
│   - Current status                      │
│   - Recent decisions                    │
│   - Knowledge base                      │
└─────────────────────────────────────────┘
  ↓
YOU: "ငါ့ MOEAD algorithm က NSGA-II နဲ့ ဘယ်လို compare လုပ်သင့်လဲ?"
  ↓
Claude Chat: [Reads context from Notion]
  ↓
"သင့် project မှာ MOEAD က Month 9 မှာ implement လုပ်နေတယ်...
 NSGA-II က ပြီးသွားပြီ...
 Compare လုပ်ဖို့ ZDT benchmarks သုံးဖို့ decide လုပ်ထားပြီးသား...
 ဒါဆို ဒီလို approach သုံးရမယ်..."
  ↓
YOU: Takes notes / Makes decisions
  ↓
Update decision in Notion
```

**Claude Chat က ဘာကြောင့် context သိလဲ?**
```
Notion MCP connection ကြောင့်:
  ↓
Notion "Project Context" page
  ↓
Auto-synced from GitHub PROJECT_CONTEXT.md
  ↓
OR manually updated by you
  ↓
Claude Chat reads via Notion API
  ↓
Always has latest context!
```

---

### 🌙 EVENING (ညနေခင်း - ၅ မိနစ်)

```
Step 1: Review Today's Work
┌──────────────────────────────────────────┐
│  Check files changed:                    │
│  $ git status                            │
│  ↓                                       │
│  modified: src/algorithms/moead.py       │
│  modified: tests/test_moead.py           │
│  ↓                                       │
│  "ဒီနေ့ ဒါတွေ လုပ်ခဲ့တယ်"                  │
└──────────────────────────────────────────┘

Step 2: Commit Changes
┌──────────────────────────────────────────┐
│  git add .                               │
│  ↓                                       │
│  git commit -m "Implement MOEAD weight   │
│                 vector generation"       │
│  ↓                                       │
│  git push                                │
└──────────────────────────────────────────┘

Step 3: Update Status
┌──────────────────────────────────────────┐
│  vim CURRENT_STATUS.md                   │
│  ↓                                       │
│  Update:                                 │
│  ✅ Completed Today:                     │
│     - MOEAD weight vectors (done!)       │
│  🚧 In Progress:                         │
│     - Testing needed                     │
│  📋 Tomorrow:                            │
│     - Run ZDT1 benchmark                 │
│  ↓                                       │
│  git add CURRENT_STATUS.md               │
│  git commit -m "EOD update 2026-04-21"   │
│  git push                                │
└──────────────────────────────────────────┘

Step 4: Quick Notion Update
┌──────────────────────────────────────────┐
│  Open Notion → "Daily Log" page          │
│  ↓                                       │
│  "2026-04-21:                            │
│   ✅ MOEAD weight vectors complete       │
│   💡 Learned: Das-Dennis method works    │
│   🔜 Tomorrow: ZDT1 testing"             │
└──────────────────────────────────────────┘
```

---

## 🔄 THE SYNC CYCLE (ဘယ်လို sync ဖြစ်လဲ)

```
┌────────────────────────────────────────────────────────────┐
│                    INFORMATION FLOW                         │
└────────────────────────────────────────────────────────────┘

   YOU WRITE CODE          YOU UPDATE STATUS      YOU PLAN STRATEGY
         │                        │                       │
         ▼                        ▼                       ▼
   ┌──────────┐            ┌──────────┐           ┌──────────┐
   │  Local   │───push────►│  GitHub  │◄──sync───│  Notion  │
   │  Files   │            │(Truth)   │           │(Planning)│
   └──────────┘            └────┬─────┘           └────┬─────┘
         ▲                      │                       │
         │                      │                       │
         │                      ▼                       ▼
         │              ┌──────────────┐        ┌──────────────┐
         │              │PROJECT_      │        │Notion Pages: │
         │              │CONTEXT.md    │        │- Overview    │
         │              │              │        │- Status      │
         │              │CURRENT_      │        │- Decisions   │
         │              │STATUS.md     │        │- Knowledge   │
         │              └──────┬───────┘        └──────┬───────┘
         │                     │                       │
         │                     │                       │
         │                     ▼                       ▼
         │              ┌──────────────┐        ┌──────────────┐
         └──────────────│ Claude Code  │        │ Claude Chat  │
    Generates code      │  (Terminal)  │        │  (Browser)   │
                        └──────────────┘        └──────────────┘
                              │                       │
                              └───────────┬───────────┘
                                          │
                                  Both have context!
                                  Both know project!
```

---

## 📊 EXAMPLE: Real Day Scenario

### မနက် 9:00 AM

```
┌──────────────────────────────────────┐
│ YOU:                                 │
│ "ဒီနေ့ MOEAD algorithm ဆက်ရေးမယ်"      │
└──────────────────────────────────────┘
         ↓
┌──────────────────────────────────────┐
│ UPDATE: CURRENT_STATUS.md            │
│                                      │
│ 🚧 Today: MOEAD weight vectors       │
│ 📁 File: src/algorithms/moead.py     │
└──────────────────────────────────────┘
         ↓
┌──────────────────────────────────────┐
│ COMMIT TO GITHUB                     │
│ "Daily plan - starting MOEAD"        │
└──────────────────────────────────────┘
```

### 10:00 AM - Coding

```
┌──────────────────────────────────────┐
│ TERMINAL:                            │
│ $ thesis-code "MOEAD weight vectors  │
│   generate လုပ်မယ် Das-Dennis method" │
└──────────────────────────────────────┘
         ↓
         (Claude Code loads context from files)
         ↓
┌──────────────────────────────────────┐
│ CLAUDE CODE RESPONSE:                │
│ "သင့် project structure အရ...         │
│  moead.py ထဲမှာ ဒီလို ရေးရမယ်..."      │
│  [Code generated]                    │
└──────────────────────────────────────┘
         ↓
┌──────────────────────────────────────┐
│ YOU: Copy → Save → Test              │
└──────────────────────────────────────┘
```

### 2:00 PM - Planning

```
┌──────────────────────────────────────┐
│ BROWSER: claude.ai                   │
│ "MOEAD က NSGA-II ထက် ပိုကောင်းမလား?   │
│  Benchmark အတွက် ဘာသုံးသင့်လဲ?"         │
└──────────────────────────────────────┘
         ↓
         (Claude Chat reads from Notion)
         ↓
┌──────────────────────────────────────┐
│ CLAUDE CHAT RESPONSE:                │
│ "သင့် Notion status အရ MOEAD က O(N)   │
│  ဖြစ်တော့ large population မှာ        │
│  ပိုမြန်မယ်... ZDT suite သုံးပြီး       │
│  compare လုပ်ဖို့ decide ထားပြီးသား..." │
└──────────────────────────────────────┘
         ↓
┌──────────────────────────────────────┐
│ YOU: Update decision in Notion       │
│ "✅ Decision: Use ZDT1-6 for tests"  │
└──────────────────────────────────────┘
```

### ညနေ 6:00 PM

```
┌──────────────────────────────────────┐
│ COMMIT WORK:                         │
│ $ git add .                          │
│ $ git commit -m "MOEAD: Add weight   │
│   vector generation (Das-Dennis)"    │
│ $ git push                           │
└──────────────────────────────────────┘
         ↓
┌──────────────────────────────────────┐
│ UPDATE STATUS:                       │
│ ✅ Today: MOEAD weight vectors done  │
│ 🔜 Tomorrow: Testing on ZDT1         │
│                                      │
│ Commit + Push                        │
└──────────────────────────────────────┘
         ↓
┌──────────────────────────────────────┐
│ NOTION QUICK NOTE:                   │
│ "2026-04-21: ✅ MOEAD progress good"  │
└──────────────────────────────────────┘
```

---

## 🎯 KEY BENEFITS (အကျိုးကျေးဇူးတွေ)

```
✅ Claude Code က session ပိတ်လည်း
   → thesis-code ခေါ်ရုံနဲ့ context ပြန်ရပြီ

✅ Claude Chat က conversation အသစ်ဖွင့်လည်း
   → Notion ကနေ context ပြန်ရပြီ

✅ သင် computer ပြောင်းလည်း
   → GitHub clone ရုံပဲ၊ context files ပါလာပြီ

✅ Advisor ကို share လုပ်ချင်လည်း
   → GitHub repo link ပို့ရုံပဲ

✅ ၃ လ ကြာပြီး ပြန်ကြည့်လည်း
   → CURRENT_STATUS.md ဖတ်ရုံနဲ့ သိပြီ
```

---

## 💪 PRO TIPS

```
Tip 1: Morning routine (< 5 min)
- Open CURRENT_STATUS.md
- Update today's focus
- Commit + Push
- Done!

Tip 2: Coding time
- Always use: thesis-code
- Never re-explain context
- Work faster!

Tip 3: Evening routine (< 5 min)
- Commit all changes
- Update CURRENT_STATUS.md
- Quick Notion note
- Done!

Tip 4: Weekly review
- Sunday evening
- Read CURRENT_STATUS.md history
- Plan next week in Notion
- Update PROJECT_CONTEXT.md if needed
```

---

**ရှင်းသွားပြီလား? ဒီ workflow သဘောကျလား?** 🚀
