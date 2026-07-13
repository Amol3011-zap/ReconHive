# Missing Components Inventory

**Status**: 14 critical components not implemented  
**Impact**: Prevents all interactive workflows

---

## MISSING UI COMPONENTS

### 1. Modal/Dialog Component ⚠️ CRITICAL
**Location**: Should be in `/components`  
**Used By**:
- Create Engagement
- Create Scan
- Create Finding
- Upload Evidence
- Generate Report
- Confirm actions

**Status**: ❌ NOT IMPLEMENTED  
**Impact**: HIGH - blocks all create/edit operations

---

### 2. Form Component ⚠️ CRITICAL
**Location**: Should be in `/components`  
**Used By**:
- Settings page
- Create engagement form
- Create scan form
- Upload evidence form
- Generate report form

**Status**: ❌ NOT IMPLEMENTED  
**Impact**: HIGH - blocks all data entry

---

### 3. Loading Spinner / Skeleton Loader ⚠️ CRITICAL
**Location**: Should be in `/components`  
**Used By**:
- All pages during data fetch
- All buttons during submission
- File uploads
- Report generation

**Status**: ❌ NOT IMPLEMENTED  
**Impact**: HIGH - no user feedback during loading

---

### 4. Error Boundary Component ⚠️ CRITICAL
**Location**: Should wrap entire app
**Purpose**: Catch and display errors gracefully

**Status**: ❌ NOT IMPLEMENTED  
**Impact**: MEDIUM - app crashes on error

---

### 5. Toast/Notification Component ⚠️ CRITICAL
**Location**: Should be in `/components`  
**Used By**:
- Success messages after actions
- Error messages
- Information alerts
- Warnings

**Status**: ❌ NOT IMPLEMENTED  
**Impact**: MEDIUM - no feedback on actions

---

### 6. Confirm Dialog Component
**Location**: Should be in `/components`  
**Used By**:
- Delete engagement
- Delete finding
- Cancel scan
- Archive report

**Status**: ❌ NOT IMPLEMENTED  
**Impact**: MEDIUM - risky actions without confirmation

---

### 7. Drawer / Slide Panel Component
**Location**: Should be in `/components`  
**Used By**:
- Finding details drawer
- Scan details drawer
- Evidence preview drawer

**Status**: ❌ NOT IMPLEMENTED  
**Impact**: MEDIUM - no detail views

---

### 8. File Upload Component
**Location**: Should be in `/components`  
**Used By**:
- Upload evidence
- Import assets (CSV/TXT)

**Status**: ❌ NOT IMPLEMENTED  
**Impact**: HIGH - no file upload capability

---

### 9. Empty State Component
**Location**: Should be in `/components`  
**Used By**:
- Empty engagement list
- Empty asset list
- Empty findings list
- Empty evidence list
- Empty scan list

**Status**: ❌ NOT IMPLEMENTED  
**Impact**: LOW - nice to have, doesn't break functionality

---

### 10. Pagination Component
**Location**: Should be in `/components`  
**Used By**:
- All tables for large datasets
- Asset list
- Finding list
- Evidence list

**Status**: ❌ NOT IMPLEMENTED  
**Impact**: MEDIUM - doesn't scale

---

### 11. Badge / Tag Component
**Location**: Should be in `/components`  
**Used By**:
- Asset tags
- Finding severity badges
- Status badges
- Report section indicators

**Status**: ❌ Partially implemented  
**Current**: Inline JSX with tailwind classes  
**Need**: Reusable component

---

### 12. Breadcrumb Component
**Location**: Should be in `/components`  
**Used By**:
- Detail pages navigation
- Back navigation

**Status**: ❌ NOT IMPLEMENTED  
**Impact**: LOW - but improves UX

---

### 13. Search Box Component (with debouncing)
**Location**: Should be in `/components`  
**Used By**:
- Engagements search
- Evidence search
- Findings search
- Global search

**Status**: ❌ Partially implemented  
**Current**: Plain HTML input  
**Missing**: Debounce, filtering logic

---

### 14. Date/Time Picker Component
**Location**: Should be in `/components`  
**Used By**:
- Engagement date ranges
- Date filters
- Report date selection

**Status**: ❌ NOT IMPLEMENTED  
**Impact**: MEDIUM - currently using text input

---

## MISSING UTILITY COMPONENTS

### 1. Protected Route Wrapper
**Location**: Should be in `/components` or `/lib`  
**Purpose**: Wrap routes to check authentication  
**Status**: ❌ NOT IMPLEMENTED  
**Impact**: HIGH - no route protection

---

### 2. Data Fetching Hook (useData)
**Location**: Should be in `/hooks`  
**Purpose**: Centralized data fetching with loading/error states  
**Status**: ❌ NOT IMPLEMENTED  
**Impact**: HIGH - no way to fetch real data

---

### 3. Form Hook (useForm)
**Location**: Should be in `/hooks`  
**Purpose**: Handle form state, validation, submission  
**Status**: ❌ NOT IMPLEMENTED  
**Impact**: HIGH - no form handling

---

### 4. API Client Hook (useApi)
**Location**: Should be in `/hooks`  
**Purpose**: Wrapper around api.ts with loading state  
**Status**: ❌ NOT IMPLEMENTED  
**Impact**: HIGH - no unified API access

---

### 5. Auth Hook (useAuth)
**Location**: Should be in `/hooks`  
**Purpose**: Manage authentication state  
**Status**: ❌ NOT IMPLEMENTED  
**Impact**: HIGH - no auth management

---

## MISSING PAGES

### 1. Activity Page (/activity)
**Referenced By**: Dashboard "View all activity →"  
**Status**: ❌ NOT IMPLEMENTED  
**Impact**: MEDIUM - broken link

---

### 2. Plugins Page (/plugins)
**Purpose**: Manage plugins, view configuration  
**Status**: ❌ NOT IMPLEMENTED  
**Impact**: HIGH - needed for full app

---

### 3. Schedules Page (/schedules)
**Purpose**: Create/manage scan schedules  
**Status**: ❌ NOT IMPLEMENTED  
**Impact**: HIGH - needed for automation

---

### 4. Engagement Detail Page (/engagements/{id})
**Purpose**: View engagement details, assets, scans  
**Status**: ❌ NOT IMPLEMENTED  
**Impact**: MEDIUM - needed for navigation

---

### 5. Scan Detail Page (/scans/{id})
**Purpose**: View scan progress, jobs, logs  
**Status**: ❌ NOT IMPLEMENTED  
**Impact**: MEDIUM - needed for navigation

---

### 6. Finding Detail Page (/findings/{id})
**Purpose**: View finding details, evidence, remediation  
**Status**: ❌ NOT IMPLEMENTED  
**Impact**: MEDIUM - needed for navigation

---

### 7. Evidence Detail Page (/evidence/{id})
**Purpose**: Preview evidence, download, view metadata  
**Status**: ❌ NOT IMPLEMENTED  
**Impact**: LOW - can view list instead

---

## MISSING SERVICES/UTILITIES

### 1. Authentication Service
**Functions Needed**:
- login(email, password)
- logout()
- getCurrentUser()
- refreshToken()
- isAuthenticated()

**Status**: ❌ NOT IMPLEMENTED  
**Impact**: HIGH

---

### 2. API Service (Proper Implementation)
**Current**: api.ts exists but unused  
**Missing**:
- Interceptors for auth
- Error handling
- Request/response transformation
- Retry logic

**Status**: ⚠️ PARTIAL  
**Impact**: HIGH

---

### 3. Cache Service
**Functions Needed**:
- Cache data fetches
- Invalidate cache on mutations
- Preload common queries

**Status**: ❌ NOT IMPLEMENTED  
**Impact**: MEDIUM

---

### 4. Error Handling Service
**Functions Needed**:
- Normalize API errors
- Display user-friendly messages
- Log errors for debugging

**Status**: ❌ NOT IMPLEMENTED  
**Impact**: MEDIUM

---

### 5. Validation Service
**Functions Needed**:
- Email validation
- URL validation
- CIDR validation
- Required field checking

**Status**: ❌ NOT IMPLEMENTED  
**Impact**: MEDIUM

---

## MISSING STATE MANAGEMENT

**Current State**: Uses useState on individual pages  
**Missing**:
- ❌ Context API for shared state
- ❌ Redux or Zustand for complex state
- ❌ Global auth state
- ❌ Global app state
- ❌ Caching strategy

**Impact**: HIGH - state scattered across pages

---

## SUMMARY

**Total Missing Components**: 14+ critical  
**By Severity**:
- CRITICAL: 5 (Modal, Form, Spinner, Error Boundary, Toast)
- HIGH: 6 (File upload, Routes, Forms, API, Auth, State)
- MEDIUM: 6 (Drawer, Pagination, Confirm, Search, Date picker, Detail pages)
- LOW: 3 (Empty state, Breadcrumb, Activity page)

**Overall Impact**: Frontend is 70% UI skeleton, 30% functionality

---

**Prepared by**: Principal QA Engineer
