# Broken Features Audit

**Status**: 17 broken interactive features  
**Impact**: No user workflows can be completed

---

## UI Elements That Appear But Don't Work

### Buttons (8 Broken)

1. **"➕ New Engagement"** (Engagements page)
   - Visual: ✅ Displays
   - Click: ❌ No handler
   - Expected: Open create modal
   - Actual: Nothing happens
   - Impact: HIGH (primary action)

2. **"🚀 Launch Scan"** (Scans page)
   - Visual: ✅ Displays
   - Click: ❌ No handler
   - Expected: Open scan creation modal
   - Actual: Nothing happens
   - Impact: HIGH (primary action)

3. **"📤 Upload Evidence"** (Evidence page)
   - Visual: ✅ Displays
   - Click: ❌ No handler
   - Expected: File upload dialog
   - Actual: Nothing happens
   - Impact: HIGH (primary action)

4. **"📝 Generate Report"** (Reports page)
   - Visual: ✅ Displays
   - Click: ❌ No handler
   - Expected: Report generation form
   - Actual: Nothing happens
   - Impact: HIGH (primary action)

5. **"Download (PDF)"** (Reports page)
   - Visual: ✅ Displays
   - Click: ❌ No handler
   - Expected: PDF download
   - Actual: Nothing happens
   - Impact: MEDIUM (secondary action)

6. **"Export (MD)"** (Reports page)
   - Visual: ✅ Displays
   - Click: ❌ No handler
   - Expected: Markdown export
   - Actual: Nothing happens
   - Impact: MEDIUM (secondary action)

7. **"💾 Save Settings"** (Settings page)
   - Visual: ✅ Displays
   - Click: ❌ No handler
   - Expected: Save user preferences
   - Actual: Nothing happens
   - Impact: MEDIUM (form submission)

8. **"↓ Send Message"** (AI Copilot)
   - Visual: ✅ Displays
   - Click: ✅ WORKS (hardcoded responses)
   - Expected: Send to real AI
   - Actual: Returns hardcoded response
   - Impact: DEMO (acceptable)

### Input Fields (3 Broken)

9. **Search Engagements** (Engagements page)
   - Visual: ✅ Displays
   - Type: ✅ Input works
   - Filter: ❌ No filtering
   - Expected: Filter list by name/client
   - Actual: Text entered but not used
   - Impact: MEDIUM

10. **Search Evidence** (Evidence page)
    - Visual: ✅ Displays
    - Type: ✅ Input works
    - Filter: ❌ No filtering
    - Expected: Filter evidence by name
    - Actual: Text entered but not used
    - Impact: MEDIUM

11. **Search Findings** (Findings page)
    - Visual: ✅ Displays
    - Type: ✅ Input works
    - Filter: ❌ No filtering
    - Expected: Filter findings by title
    - Actual: Text entered but not used
    - Impact: MEDIUM

### Select/Dropdown Filters (3 Broken)

12. **Status Filter** (Scans page)
    - Visual: ✅ Displays
    - Change: ✅ Value changes
    - Filter: ❌ No filtering applied
    - Expected: Filter scans by status
    - Actual: Selection has no effect
    - Impact: MEDIUM

13. **Severity Filter** (Findings page)
    - Visual: ✅ Displays
    - Change: ✅ Value changes
    - Filter: ❌ No filtering applied
    - Expected: Filter findings by severity
    - Actual: Selection has no effect
    - Impact: MEDIUM

14. **Criticality Filter** (Assets page)
    - Visual: ✅ Displays
    - Change: ✅ Value changes
    - Filter: ❌ No filtering applied
    - Expected: Filter assets by criticality
    - Actual: Selection has no effect
    - Impact: MEDIUM

### Links (2 Broken)

15. **"View all activity →"** (Dashboard)
    - Visual: ✅ Displays
    - Click: ❌ Route doesn't exist (/activity)
    - Expected: Navigate to activity page
    - Actual: 404 error
    - Impact: MEDIUM (broken link)

16. **"View all findings →"** (Dashboard)
    - Visual: ✅ Displays
    - Click: ✅ WORKS (navigates to /findings)
    - Expected: Navigate to findings page
    - Actual: Works correctly
    - Impact: OK

### Table Interactions (1 Broken)

17. **Scan Table Rows** (Dashboard, Scans page)
    - Visual: ✅ Rows display
    - Hover: ✅ Shows cursor
    - Click: ❌ No row click handler
    - Expected: Navigate to scan details
    - Actual: Nothing happens
    - Impact: MEDIUM

---

## Form Fields Without Validation

### Settings Page Form (4 Fields)
```
1. API URL
   - Validation: ❌ None
   - Save: ❌ Doesn't persist
   - Expected: Validate URL format, save to localStorage

2. Theme selector
   - Validation: ❌ None
   - Apply: ❌ Doesn't change theme
   - Expected: Apply theme immediately

3. Notifications checkbox
   - Validation: ❌ None
   - Apply: ❌ Doesn't enable/disable notifications
   - Expected: Save preference

4. Auto-refresh checkbox
   - Validation: ❌ None
   - Apply: ❌ Doesn't auto-refresh data
   - Expected: Refresh data on interval
```

---

## Missing User Feedback

### No Loading States
- Buttons don't show loading spinner
- Pages don't show skeleton loader
- No progress indicator on long operations
- No disabled state while "loading"

### No Error Messages
- Form errors not displayed
- API errors not shown
- Failed actions have no feedback
- No error boundary

### No Success Feedback
- No toast notifications
- No success messages
- No confirmation dialogs
- No feedback after actions

### No Empty States
- No empty state when no data
- No "No engagements" message
- No "No findings" message
- No helper text for new users

---

## Missing Modal Components

### Should Exist But Don't

1. **Create Engagement Modal**
   - Fields: name, client, description, dates, type
   - Actions: Create, Cancel
   - Validation: Required fields
   - Status: ❌ NOT IMPLEMENTED

2. **Create Scan Modal**
   - Fields: name, plugin, target, priority
   - Actions: Launch, Cancel
   - Validation: Required fields
   - Status: ❌ NOT IMPLEMENTED

3. **Upload Evidence Modal**
   - Fields: file upload, related finding
   - Actions: Upload, Cancel
   - Validation: File type
   - Status: ❌ NOT IMPLEMENTED

4. **Generate Report Modal**
   - Fields: report type, sections
   - Actions: Generate, Cancel
   - Validation: At least one section
   - Status: ❌ NOT IMPLEMENTED

5. **Create Finding Modal**
   - Fields: title, severity, description, asset
   - Actions: Create, Cancel
   - Validation: Required fields
   - Status: ❌ NOT IMPLEMENTED

---

## Missing Detail Pages

1. **/engagements/{id}**
   - Should show: Full engagement details, assets, scans, findings
   - Status: ❌ NOT IMPLEMENTED

2. **/scans/{id}**
   - Should show: Scan details, jobs, progress, logs
   - Status: ❌ NOT IMPLEMENTED

3. **/findings/{id}**
   - Should show: Finding details, evidence, remediation, history
   - Status: ❌ NOT IMPLEMENTED

4. **/evidence/{id}**
   - Should show: Evidence details, preview, related findings
   - Status: ❌ NOT IMPLEMENTED

---

## API Integration (0% Complete)

### All Pages Use Mock Data
- Dashboard: ❌ Doesn't call api.get('/engagements')
- Engagements: ❌ Doesn't call api.get('/engagements')
- Assets: ❌ Doesn't call api.get('/assets')
- Scans: ❌ Doesn't call api.get('/scans')
- Findings: ❌ Doesn't call api.get('/findings')
- Evidence: ❌ Doesn't call api.get('/evidence')
- Reports: ❌ Custom, no API call
- Settings: ❌ Doesn't call api.put('/settings')

### useEffect Missing Everywhere
- No data fetching on page load
- No error handling
- No loading state
- No cache management

---

## Summary

**Total Broken Features**: 17  
**Broken Buttons**: 7 (critical)  
**Broken Filters**: 6  
**Broken Links**: 1  
**Broken Interactions**: 1  
**Missing User Feedback**: 4 categories  

**Impact**: User cannot perform any workflows  
**Demo Risk**: HIGH - cannot show functionality  

---

**Prepared by**: Principal QA Engineer
