# 🔌 API Reference Documentation

**Base URL:** `https://api.personalfinancecoach.app/v1`  
**Authentication:** Bearer Token (JWT)  
**Content-Type:** `application/json`

---

## 🔐 Authentication

### Register New User

**Endpoint:** `POST /auth/register`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "name": "Priya Sharma",
  "consent": {
    "terms_accepted": true,
    "privacy_accepted": true,
    "marketing_emails": false
  }
}
```

**Validation Rules:**
- Email: Valid format, unique, max 255 characters
- Password: Min 8 characters, 1 uppercase, 1 number, 1 special char
- Name: Min 2 characters, max 100 characters

**Success Response (201 Created):**
```json
{
  "success": true,
  "user_id": "usr_28x9k2h1",
  "email": "user@example.com",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 3600
}
```

**Error Responses:**
```json
// 400 Bad Request - Validation Failed
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Password must contain at least one uppercase letter",
    "field": "password"
  }
}

// 409 Conflict - Email Already Exists
{
  "success": false,
  "error": {
    "code": "EMAIL_EXISTS",
    "message": "An account with this email already exists"
  }
}
```

---

### Login

**Endpoint:** `POST /auth/login`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "user_id": "usr_28x9k2h1",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 3600,
  "profile_complete": true
}
```

**Error Response (401 Unauthorized):**
```json
{
  "success": false,
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "Invalid email or password"
  }
}
```

---

## 👤 User Profile

### Get Profile

**Endpoint:** `GET /profile`  
**Auth Required:** Yes

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "user_id": "usr_28x9k2h1",
    "email": "user@example.com",
    "name": "Priya Sharma",
    "age": 28,
    "country": "India",
    "dependents": 0,
    "risk_profile": "medium",
    "financial_knowledge": "beginner",
    "created_at": "2025-12-01T10:30:00Z",
    "updated_at": "2025-12-13T07:30:00Z"
  }
}
```

---

### Create/Update Profile

**Endpoint:** `POST /profile` (Create) or `PUT /profile` (Update)  
**Auth Required:** Yes

**Request Body:**
```json
{
  "age": 28,
  "country": "India",
  "dependents": 0,
  "risk_profile": "medium",
  "financial_knowledge": "beginner"
}
```

**Field Constraints:**
- `age`: Integer, 18-100
- `country`: String, ISO country code or name
- `dependents`: Integer, 0-20
- `risk_profile`: Enum [`low`, `medium`, `high`]
- `financial_knowledge`: Enum [`beginner`, `intermediate`, `advanced`]

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Profile updated successfully",
  "data": { /* full profile */ }
}
```

---

## 📊 Financial Snapshot

### Create Snapshot

**Endpoint:** `POST /snapshot`  
**Auth Required:** Yes

**Request Body:**
```json
{
  "monthly_income": 85000,
  "monthly_expenses": 55000,
  "current_savings": 35000,
  "expense_breakdown": {
    "rent": 20000,
    "groceries": 8000,
    "utilities": 3000,
    "transport": 5000,
    "entertainment": 4000,
    "other": 15000
  }
}
```

**Validation:**
- All amounts must be >= 0
- `monthly_income` max: 100,000,000
- `monthly_expenses` should be <= `monthly_income` (warning if not)

**Success Response (201 Created):**
```json
{
  "success": true,
  "snapshot_id": "snap_91m3n7k2",
  "created_at": "2025-12-13T07:30:00Z",
  "calculated_metrics": {
    "monthly_surplus": 30000,
    "savings_rate": 0.353,
    "recommended_next_step": "Add assets and liabilities"
  }
}
```

---

### Get Latest Snapshot

**Endpoint:** `GET /snapshot/latest`  
**Auth Required:** Yes

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "snapshot_id": "snap_91m3n7k2",
    "monthly_income": 85000,
    "monthly_expenses": 55000,
    "current_savings": 35000,
    "created_at": "2025-12-13T07:30:00Z"
  }
}
```

---

## 💰 Assets Management

### Create Asset

**Endpoint:** `POST /assets`  
**Auth Required:** Yes

**Request Body:**
```json
{
  "type": "mf",
  "name": "HDFC Equity Fund",
  "current_value": 45000,
  "liquidity": "medium",
  "expected_return": 0.12
}
```

**Asset Types:** `cash`, `fd`, `mf`, `etf`, `stock`, `gold`, `crypto`, `real_estate`, `other`  
**Liquidity Levels:** `high`, `medium`, `low`

**Success Response (201 Created):**
```json
{
  "success": true,
  "asset_id": "ast_56k9m2",
  "message": "Asset added successfully"
}
```

---

### Get All Assets

**Endpoint:** `GET /assets`  
**Auth Required:** Yes

**Success Response (200 OK):**
```json
{
  "success": true,
  "total_value": 125000,
  "count": 3,
  "data": [
    {
      "asset_id": "ast_56k9m2",
      "type": "mf",
      "name": "HDFC Equity Fund",
      "current_value": 45000,
      "liquidity": "medium",
      "created_at": "2025-12-10T08:00:00Z"
    }
    // ... more assets
  ]
}
```

---

### Update Asset

**Endpoint:** `PUT /assets/{asset_id}`  
**Auth Required:** Yes

**Request Body:**
```json
{
  "current_value": 48000
}
```

---

### Delete Asset

**Endpoint:** `DELETE /assets/{asset_id}`  
**Auth Required:** Yes

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Asset deleted successfully"
}
```

---

## 💳 Liabilities Management

### Create Liability

**Endpoint:** `POST /liabilities`  
**Auth Required:** Yes

**Request Body:**
```json
{
  "type": "credit_card",
  "outstanding_amount": 75000,
  "interest_rate": 0.36,
  "tenure_months": 0,
  "minimum_payment": 2250
}
```

**Liability Types:** `credit_card`, `personal_loan`, `home_loan`, `car_loan`, `education_loan`, `other`

**Success Response (201 Created):**
```json
{
  "success": true,
  "liability_id": "lib_82m4k9",
  "priority_score": 95,
  "warning": "High interest rate detected - prioritize this debt"
}
```

---

### Get All Liabilities

**Endpoint:** `GET /liabilities`  
**Auth Required:** Yes

**Success Response (200 OK):**
```json
{
  "success": true,
  "total_outstanding": 195000,
  "count": 2,
  "high_interest_count": 1,
  "data": [
    {
      "liability_id": "lib_82m4k9",
      "type": "credit_card",
      "outstanding_amount": 75000,
      "interest_rate": 0.36,
      "priority": "CRITICAL"
    }
    // ... more liabilities
  ]
}
```

---

## 🎯 Goals Management

### Create Goal

**Endpoint:** `POST /goals`  
**Auth Required:** Yes

**Request Body:**
```json
{
  "name": "Emergency Fund",
  "target_amount": 165000,
  "target_date": "2026-06-01",
  "priority": 1,
  "category": "emergency"
}
```

**Goal Categories:** `emergency`, `short_term`, `medium_term`, `long_term`, `retirement`

**Success Response (201 Created):**
```json
{
  "success": true,
  "goal_id": "gol_73n5k2",
  "recommended_monthly_sip": 8500,
  "timeline_months": 18
}
```

---

### Get All Goals

**Endpoint:** `GET /goals`  
**Auth Required:** Yes

**Success Response (200 OK):**
```json
{
  "success": true,
  "count": 3,
  "data": [
    {
      "goal_id": "gol_73n5k2",
      "name": "Emergency Fund",
      "target_amount": 165000,
      "current_progress": 35000,
      "progress_percentage": 21.2,
      "on_track": false
    }
    // ... more goals
  ]
}
```

---

## 📋 Plan Generation

### Generate Personalized Plan

**Endpoint:** `POST /plan/generate`  
**Auth Required:** Yes

**Request Body:**
```json
{
  "force_regenerate": false,
  "risk_override": null,
  "include_explanations": true
}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "plan_id": "plan_45k9x2",
  "generated_at": "2025-12-13T07:30:00Z",
  "summary": {
    "net_worth": -115000,
    "savings_rate": 0.353,
    "emergency_months": 0.64,
    "debt_to_income": 0.085,
    "financial_health_score": 42
  },
  "buckets": {
    "emergency": {
      "current": 35000,
      "target": 165000,
      "gap": 130000,
      "monthly_allocation": 5000,
      "priority": 1,
      "status": "CRITICAL"
    },
    "debt": {
      "total_outstanding": 195000,
      "high_interest_amount": 75000,
      "monthly_allocation": 15000,
      "priority": 1,
      "estimated_payoff_months": 6
    },
    "short_term": {
      "monthly_allocation": 0,
      "status": "DEFERRED"
    },
    "long_term": {
      "current_investments": 45000,
      "monthly_allocation": 3000,
      "priority": 3
    }
  },
  "top_actions": [
    {
      "order": 1,
      "title": "Pay off Credit Card ASAP",
      "description": "Your 36% APR credit card is costing you ₹2,250/month in interest alone.",
      "impact": "Save ₹11,250 in interest over 5 months",
      "timeline": "5 months",
      "monthly_commitment": 15000,
      "explanation_id": "exp_82k1m9"
    },
    {
      "order": 2,
      "title": "Build 3-month Emergency Fund",
      "description": "You have only 0.6 months of expenses saved.",
      "impact": "Financial security buffer",
      "timeline": "26 months",
      "monthly_commitment": 5000,
      "explanation_id": "exp_91n2k7"
    },
    {
      "order": 3,
      "title": "Continue Long-term SIP",
      "description": "Keep building wealth through existing investments.",
      "impact": "Projected ₹1,20,000 in 3 years",
      "monthly_commitment": 3000,
      "explanation_id": "exp_63m8k5"
    }
  ],
  "monthly_targets": {
    "save": 5000,
    "invest": 3000,
    "debt_payoff": 15000,
    "total_commitment": 23000,
    "remaining_buffer": 7000
  },
  "projections": {
    "month_6": {
      "net_worth": -45000,
      "credit_card_cleared": true,
      "emergency_fund": 65000
    },
    "month_12": {
      "net_worth": 35000,
      "debt_remaining": 60000,
      "emergency_fund": 95000
    },
    "month_24": {
      "net_worth": 300000,
      "all_debts_cleared": true,
      "emergency_fund": 165000,
      "investments": 135000
    }
  },
  "confidence_score": 0.87,
  "rule_version": "v1.2.0"
}
```

**Error Response (400 Bad Request):**
```json
{
  "success": false,
  "error": {
    "code": "INCOMPLETE_PROFILE",
    "message": "Please complete financial snapshot before generating plan",
    "missing_fields": ["assets", "liabilities"]
  }
}
```

---

### Get Current Plan

**Endpoint:** `GET /plan/current`  
**Auth Required:** Yes

**Success Response (200 OK):**
```json
{
  "success": true,
  "plan_id": "plan_45k9x2",
  "generated_at": "2025-12-13T07:30:00Z",
  // ... same structure as generate response
}
```

---

## 📈 Progress Tracking

### Submit Monthly Progress

**Endpoint:** `POST /progress/monthly`  
**Auth Required:** Yes

**Request Body:**
```json
{
  "month": "2025-12",
  "saved_amount": 5000,
  "invested_amount": 3000,
  "debt_paid": 15000,
  "notes": "Had unexpected car repair expense",
  "unexpected_expenses": 12000
}
```

**Success Response (201 Created):**
```json
{
  "success": true,
  "progress_id": "prg_92k5m3",
  "status": "ON_TRACK",
  "analysis": {
    "savings_target_met": true,
    "investment_target_met": true,
    "debt_target_met": true,
    "overall_status": "EXCELLENT",
    "next_milestone": "Credit card payoff in 4 months"
  },
  "encouragement": "Great job! You're ahead of schedule on debt payoff. 💪"
}
```

**Possible Status Values:** `AHEAD`, `ON_TRACK`, `BEHIND`, `CRITICAL`

---

### Get Progress History

**Endpoint:** `GET /progress/history`  
**Auth Required:** Yes  
**Query Parameters:**
- `months` (optional): Number of months to retrieve (default: 12)
- `from_date` (optional): Start date (ISO 8601)
- `to_date` (optional): End date (ISO 8601)

**Example Request:**
```
GET /progress/history?months=6
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "count": 3,
  "summary": {
    "total_saved": 16000,
    "total_invested": 32000,
    "total_debt_paid": 40000,
    "months_on_track": 2,
    "months_behind": 1
  },
  "data": [
    {
      "month": "2025-12",
      "saved_amount": 5000,
      "invested_amount": 3000,
      "debt_paid": 15000,
      "status": "ON_TRACK",
      "created_at": "2025-12-31T18:00:00Z"
    }
    // ... previous months
  ],
  "trend": "IMPROVING"
}
```

---

## 🔔 Nudges & Notifications

### Get Active Nudges

**Endpoint:** `GET /nudges`  
**Auth Required:** Yes  
**Query Parameters:**
- `type` (optional): Filter by type [`encouragement`, `correction`, `reminder`, `milestone`]
- `unread_only` (optional): Boolean (default: false)

**Success Response (200 OK):**
```json
{
  "success": true,
  "count": 2,
  "data": [
    {
      "nudge_id": "ndg_73k2m9",
      "type": "correction",
      "priority": "medium",
      "title": "You missed your savings target this month",
      "message": "Don't worry! Here are two options to get back on track...",
      "action_items": [
        {
          "title": "Adjust plan",
          "action": "ADJUST_PLAN",
          "parameters": { "reduce_target": 2000 }
        },
        {
          "title": "Skip this month",
          "action": "SKIP_MONTH"
        }
      ],
      "created_at": "2025-12-13T07:00:00Z",
      "read": false
    }
  ]
}
```

---

## 🤖 AI Explanation (RAG)

### Ask Question / Get Explanation

**Endpoint:** `POST /explain`  
**Auth Required:** Yes

**Request Body:**
```json
{
  "question": "Why should I pay debt first before investing?",
  "context_type": "general",
  "recommendation_id": null
}
```

**Context Types:** `general`, `recommendation`, `bucket`, `debt_strategy`, `risk_profile`

**Success Response (200 OK):**
```json
{
  "success": true,
  "question": "Why should I pay debt first before investing?",
  "answer": "Your credit card debt at 36% APR is costing you ₹2,250 every month...",
  "sources": [
    {
      "title": "Debt Avalanche Method",
      "type": "knowledge_base",
      "confidence": 0.92,
      "excerpt": "High-interest debts above 12% should always be prioritized..."
    },
    {
      "title": "Opportunity Cost Analysis",
      "type": "financial_handbook",
      "confidence": 0.88,
      "excerpt": "The mathematical comparison between debt cost vs investment returns..."
    }
  ],
  "confidence_level": "HIGH",
  "related_questions": [
    "What is the avalanche method for debt repayment?",
    "Should I invest while paying off my home loan?"
  ],
  "response_time_ms": 1250
}
```

---

## 🔢 Common HTTP Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | Successful GET, PUT, DELETE |
| 201 | Created | Successful POST creating new resource |
| 400 | Bad Request | Invalid request format or validation failed |
| 401 | Unauthorized | Missing or invalid authentication token |
| 403 | Forbidden | Valid token but insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Resource already exists (e.g., duplicate email) |
| 422 | Unprocessable Entity | Valid format but business logic error |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server-side error |
| 503 | Service Unavailable | Temporary downtime or maintenance |

---

## 🛡️ Error Response Format

All errors follow this structure:

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "field": "field_name",
    "details": { /* optional additional context */ }
  },
  "request_id": "req_92k3m7n1"
}
```

**Common Error Codes:**
- `VALIDATION_ERROR` - Input validation failed
- `AUTHENTICATION_REQUIRED` - No auth token provided
- `INVALID_TOKEN` - Token expired or invalid
- `RESOURCE_NOT_FOUND` - Requested resource doesn't exist
- `INSUFFICIENT_DATA` - Not enough data to perform operation
- `BUSINESS_LOGIC_ERROR` - Operation violates business rules

---

## 🚀 Rate Limiting

- **Anonymous requests:** 10 requests/minute
- **Authenticated requests:** 100 requests/minute
- **Plan generation:** 5 requests/hour (computationally expensive)
- **RAG explanations:** 30 requests/hour

**Rate Limit Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1702464000
```

---

## 📝 Request Examples (cURL)

### Generate Plan
```bash
curl -X POST https://api.personalfinancecoach.app/v1/plan/generate \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "include_explanations": true
  }'
```

### Add Asset
```bash
curl -X POST https://api.personalfinancecoach.app/v1/assets \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "type": "mf",
    "name": "HDFC Equity Fund",
    "current_value": 45000,
    "liquidity": "medium"
  }'
```

---

**API Version:** v1  
**Last Updated:** 2025-12-13  
**Documentation Version:** 2.0
