# 🗄️ Database Schema & Design

Complete database design with Entity-Relationship diagrams, table schemas, and data models for the Personal Finance Coach application.

---

## Entity-Relationship Diagram

```mermaid
erDiagram
    USER ||--|| USER_PROFILE : "has"
    USER ||--o{ FINANCIAL_SNAPSHOT : "creates"
    USER ||--o{ ASSET : "owns"
    USER ||--o{ LIABILITY : "owes"
    USER ||--o{ GOAL : "defines"
    USER ||--o{ BUCKET : "manages"
    USER ||--o{ PLAN : "receives"
    USER ||--o{ MONTHLY_PROGRESS : "tracks"
    FINANCIAL_SNAPSHOT ||--o{ PLAN : "generates"
    PLAN ||--o{ RECOMMENDATION_LOG : "logs"
    PLAN ||--o{ MONTHLY_PROGRESS : "tracks"
    
    USER {
        uuid id PK
        string email UK
        string password_hash
        string name
        timestamp created_at
        timestamp last_login_at
        timestamp updated_at
    }
    
    USER_PROFILE {
        uuid user_id PK_FK
        int age
        string country
        int dependents
        enum risk_profile
        enum financial_knowledge
        timestamp created_at
        timestamp updated_at
    }
    
    FINANCIAL_SNAPSHOT {
        uuid id PK
        uuid user_id FK
        decimal monthly_income
        decimal monthly_expenses
        decimal current_savings
        jsonb expense_breakdown
        timestamp created_at
    }
    
    ASSET {
        uuid id PK
        uuid user_id FK
        enum type
        string name
        decimal current_value
        enum liquidity
        decimal expected_return
        timestamp created_at
        timestamp updated_at
    }
    
    LIABILITY {
        uuid id PK
        uuid user_id FK
        enum type
        string name
        decimal outstanding_amount
        decimal interest_rate
        int tenure_months
        decimal minimum_payment
        timestamp created_at
        timestamp updated_at
    }
    
    GOAL {
        uuid id PK
        uuid user_id FK
        string name
        decimal target_amount
        date target_date
        int priority
        enum category
        timestamp created_at
        timestamp updated_at
    }
    
    BUCKET {
        uuid id PK
        uuid user_id FK
        enum type UK
        decimal target_amount
        decimal current_amount
        enum status
        timestamp updated_at
    }
    
    PLAN {
        uuid id PK
        uuid user_id FK
        uuid snapshot_id FK
        string strategy_type
        decimal monthly_saving_target
        decimal monthly_invest_target
        jsonb top_actions
        jsonb buckets
        jsonb projections
        decimal confidence_score
        string rule_version
        timestamp created_at
    }
    
    MONTHLY_PROGRESS {
        uuid id PK
        uuid user_id FK
        uuid plan_id FK
        date month UK
        decimal saved_amount
        decimal invested_amount
        decimal debt_paid
        string notes
        enum status
        timestamp created_at
    }
    
    RECOMMENDATION_LOG {
        uuid id PK
        uuid user_id FK
        uuid plan_id FK
        string rule_version
        jsonb explanation_source_ids
        string model_version
        jsonb context_data
        timestamp created_at
    }
```

---

## Table Schemas

### 1. Users Table

**Purpose:** Authentication and basic user identity

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
```

**Sample Data:**
```json
{
  "id": "usr_28x9k2h1",
  "email": "priya.sharma@example.com",
  "name": "Priya Sharma",
  "created_at": "2025-12-01T10:30:00Z"
}
```

---

### 2. User Profiles Table

**Purpose:** Personal and financial preferences

```sql
CREATE TABLE user_profiles (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    age INTEGER CHECK (age >= 18 AND age <= 100),
    country VARCHAR(100) NOT NULL,
    dependents INTEGER DEFAULT 0 CHECK (dependents >= 0),
    risk_profile VARCHAR(20) CHECK (risk_profile IN ('low', 'medium', 'high')),
    financial_knowledge VARCHAR(20) CHECK (financial_knowledge IN ('beginner', 'intermediate', 'advanced')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Enums:**
- `risk_profile`: `low`, `medium`, `high`
- `financial_knowledge`: `beginner`, `intermediate`, `advanced`

---

### 3. Financial Snapshots Table

**Purpose:** Point-in-time financial data (versioned)

```sql
CREATE TABLE financial_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    monthly_income DECIMAL(12, 2) NOT NULL CHECK (monthly_income >= 0),
    monthly_expenses DECIMAL(12, 2) NOT NULL CHECK (monthly_expenses >= 0),
    current_savings DECIMAL(12, 2) NOT NULL CHECK (current_savings >= 0),
    expense_breakdown JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_snapshots_user ON financial_snapshots(user_id);
CREATE INDEX idx_snapshots_created ON financial_snapshots(user_id, created_at DESC);
```

**expense_breakdown JSON:**
```json
{
  "rent": 20000,
  "groceries": 8000,
  "utilities": 3000,
  "transport": 5000,
  "entertainment": 4000,
  "education": 5000,
  "healthcare": 3000,
  "other": 7000
}
```

---

### 4. Assets Table

**Purpose:** User's assets and investments

```sql
CREATE TABLE assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL CHECK (type IN ('cash', 'fd', 'mf', 'etf', 'stock', 'gold', 'crypto', 'real_estate', 'other')),
    name VARCHAR(200) NOT NULL,
    current_value DECIMAL(15, 2) NOT NULL CHECK (current_value >= 0),
    liquidity VARCHAR(20) CHECK (liquidity IN ('high', 'medium', 'low')),
    expected_return DECIMAL(5, 4) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_assets_user ON assets(user_id);
CREATE INDEX idx_assets_type ON assets(user_id, type);
```

**Asset Types:**
- `cash`: Savings, current accounts
- `fd`: Fixed deposits
- `mf`: Mutual funds
- `etf`: Exchange-traded funds
- `stock`: Individual stocks
- `gold`: Physical/digital gold
- `crypto`: Cryptocurrencies
- `real_estate`: Property
- `other`: Other assets

---

### 5. Liabilities Table

**Purpose:** User's debts and loans

```sql
CREATE TABLE liabilities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL CHECK (type IN ('credit_card', 'personal_loan', 'home_loan', 'car_loan', 'education_loan', 'other')),
    name VARCHAR(200) NOT NULL,
    outstanding_amount DECIMAL(15, 2) NOT NULL CHECK (outstanding_amount >= 0),
    interest_rate DECIMAL(5, 4) NOT NULL CHECK (interest_rate >= 0 AND interest_rate <= 1),
    tenure_months INTEGER CHECK (tenure_months >= 0),
    minimum_payment DECIMAL(12, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_liabilities_user ON liabilities(user_id);
CREATE INDEX idx_liabilities_interest ON liabilities(user_id, interest_rate DESC);
```

**Priority Calculation:**
```javascript
priority_score = (interest_rate * 100) + (outstanding_amount / 10000)
// Example: Credit card at 36% with ₹75k = 36 + 7.5 = 43.5 (HIGH)
```

---

### 6. Goals Table

**Purpose:** User's financial goals

```sql
CREATE TABLE goals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    target_amount DECIMAL(15, 2) NOT NULL CHECK (target_amount > 0),
    target_date DATE NOT NULL,
    priority INTEGER CHECK (priority >= 1 AND priority <= 5),
    category VARCHAR(50) CHECK (category IN ('emergency', 'short_term', 'medium_term', 'long_term', 'retirement')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_goals_user ON goals(user_id);
CREATE INDEX idx_goals_date ON goals(user_id, target_date);
```

**Goal Categories:**
- `emergency`: Emergency fund
- `short_term`: < 3 years (vacation, wedding, etc.)
- `medium_term`: 3-5 years (car, house down payment)
- `long_term`: 5+ years (house, child education)
- `retirement`: Retirement corpus

---

### 7. Buckets Table

**Purpose:** Money allocation buckets (framework-based organization)

```sql
CREATE TABLE buckets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL CHECK (type IN ('emergency', 'debt', 'short_term', 'long_term', 'insurance')),
    target_amount DECIMAL(15, 2) NOT NULL,
    current_amount DECIMAL(15, 2) DEFAULT 0,
    status VARCHAR(20) CHECK (status IN ('critical', 'active', 'on_track', 'completed', 'deferred')),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(user_id, type)
);

CREATE INDEX idx_buckets_user ON buckets(user_id);
```

**Bucket Types:**
- `emergency`: Emergency fund (3-6 months expenses)
- `debt`: Debt payoff bucket
- `short_term`: Goals < 3 years
- `long_term`: Goals > 5 years
- `insurance`: Insurance premiums

---

### 8. Plans Table

**Purpose:** Generated financial plans with actionable recommendations

```sql
CREATE TABLE plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    snapshot_id UUID REFERENCES financial_snapshots(id),
    strategy_type VARCHAR(100),
    monthly_saving_target DECIMAL(12, 2),
    monthly_invest_target DECIMAL(12, 2),
    top_actions JSONB NOT NULL,
    buckets JSONB NOT NULL,
    projections JSONB,
    confidence_score DECIMAL(3, 2) CHECK (confidence_score >= 0 AND confidence_score <= 1),
    rule_version VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_plans_user ON plans(user_id, created_at DESC);
```

**top_actions JSON:**
```json
[
  {
    "order": 1,
    "title": "Pay off Credit Card ASAP",
    "description": "Your 36% APR credit card is costing you ₹2,250/month",
    "impact": "Save ₹11,250 in interest",
    "timeline": "5 months",
    "monthly_commitment": 15000
  }
]
```

**buckets JSON:**
```json
{
  "emergency": {
    "current": 35000,
    "target": 165000,
    "gap": 130000,
    "monthly_allocation": 5000,
    "priority": 1
  }
}
```

---

### 9. Monthly Progress Table

**Purpose:** Self-reported user progress tracking

```sql
CREATE TABLE monthly_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    plan_id UUID REFERENCES plans(id),
    month DATE NOT NULL,
    saved_amount DECIMAL(12, 2) DEFAULT 0,
    invested_amount DECIMAL(12, 2) DEFAULT 0,
    debt_paid DECIMAL(12, 2) DEFAULT 0,
    notes TEXT,
    status VARCHAR(20) CHECK (status IN ('ahead', 'on_track', 'behind', 'critical')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(user_id, month)
);

CREATE INDEX idx_progress_user ON monthly_progress(user_id, month DESC);
```

---

### 10. Recommendation Logs Table

**Purpose:** Audit trail for AI explanations and compliance

```sql
CREATE TABLE recommendation_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    plan_id UUID REFERENCES plans(id),
    rule_version VARCHAR(20) NOT NULL,
    explanation_source_ids JSONB,
    model_version VARCHAR(50),
    context_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_rec_logs_user ON recommendation_logs(user_id, created_at DESC);
```

---

## Drizzle ORM Schema (TypeScript)

```typescript
// src/db/schema.ts
import { pgTable, uuid, varchar, text, decimal, integer, timestamp, jsonb, date, unique } from 'drizzle-orm/pg-core';

// Users
export const users = pgTable('users', {
  id: uuid('id').primaryKey().defaultRandom(),
  email: varchar('email', { length: 255 }).notNull().unique(),
  passwordHash: text('password_hash').notNull(),
  name: varchar('name', { length: 100 }).notNull(),
  createdAt: timestamp('created_at').defaultNow().notNull(),
  lastLoginAt: timestamp('last_login_at'),
  updatedAt: timestamp('updated_at').defaultNow().notNull(),
});

// User Profiles
export const userProfiles = pgTable('user_profiles', {
  userId: uuid('user_id').primaryKey().references(() => users.id, { onDelete: 'cascade' }),
  age: integer('age'),
  country: varchar('country', { length: 100 }).notNull(),
  dependents: integer('dependents').default(0),
  riskProfile: varchar('risk_profile', { length: 20 }),
  financialKnowledge: varchar('financial_knowledge', { length: 20 }),
  createdAt: timestamp('created_at').defaultNow().notNull(),
  updatedAt: timestamp('updated_at').defaultNow().notNull(),
});

// Financial Snapshots
export const financialSnapshots = pgTable('financial_snapshots', {
  id: uuid('id').primaryKey().defaultRandom(),
  userId: uuid('user_id').notNull().references(() => users.id, { onDelete: 'cascade' }),
  monthlyIncome: decimal('monthly_income', { precision: 12, scale: 2 }).notNull(),
  monthlyExpenses: decimal('monthly_expenses', { precision: 12, scale: 2 }).notNull(),
  currentSavings: decimal('current_savings', { precision: 12, scale: 2 }).notNull(),
  expenseBreakdown: jsonb('expense_breakdown'),
  createdAt: timestamp('created_at').defaultNow().notNull(),
});

// Assets
export const assets = pgTable('assets', {
  id: uuid('id').primaryKey().defaultRandom(),
  userId: uuid('user_id').notNull().references(() => users.id, { onDelete: 'cascade' }),
  type: varchar('type', { length: 50 }).notNull(),
  name: varchar('name', { length: 200 }).notNull(),
  currentValue: decimal('current_value', { precision: 15, scale: 2 }).notNull(),
  liquidity: varchar('liquidity', { length: 20 }),
  expectedReturn: decimal('expected_return', { precision: 5, scale: 4 }).default('0'),
  createdAt: timestamp('created_at').defaultNow().notNull(),
  updatedAt: timestamp('updated_at').defaultNow().notNull(),
});

// Liabilities
export const liabilities = pgTable('liabilities', {
  id: uuid('id').primaryKey().defaultRandom(),
  userId: uuid('user_id').notNull().references(() => users.id, { onDelete: 'cascade' }),
  type: varchar('type', { length: 50 }).notNull(),
  name: varchar('name', { length: 200 }).notNull(),
  outstandingAmount: decimal('outstanding_amount', { precision: 15, scale: 2 }).notNull(),
  interestRate: decimal('interest_rate', { precision: 5, scale: 4 }).notNull(),
  tenureMonths: integer('tenure_months'),
  minimumPayment: decimal('minimum_payment', { precision: 12, scale: 2 }),
  createdAt: timestamp('created_at').defaultNow().notNull(),
  updatedAt: timestamp('updated_at').defaultNow().notNull(),
});

// Goals
export const goals = pgTable('goals', {
  id: uuid('id').primaryKey().defaultRandom(),
  userId: uuid('user_id').notNull().references(() => users.id, { onDelete: 'cascade' }),
  name: varchar('name', { length: 200 }).notNull(),
  targetAmount: decimal('target_amount', { precision: 15, scale: 2 }).notNull(),
  targetDate: date('target_date').notNull(),
  priority: integer('priority'),
  category: varchar('category', { length: 50 }),
  createdAt: timestamp('created_at').defaultNow().notNull(),
  updatedAt: timestamp('updated_at').defaultNow().notNull(),
});

// Buckets
export const buckets = pgTable('buckets', {
  id: uuid('id').primaryKey().defaultRandom(),
  userId: uuid('user_id').notNull().references(() => users.id, { onDelete: 'cascade' }),
  type: varchar('type', { length: 50 }).notNull(),
  targetAmount: decimal('target_amount', { precision: 15, scale: 2 }).notNull(),
  currentAmount: decimal('current_amount', { precision: 15, scale: 2 }).default('0'),
  status: varchar('status', { length: 20 }),
  updatedAt: timestamp('updated_at').defaultNow().notNull(),
}, (table) => ({
  uniqueUserType: unique().on(table.userId, table.type),
}));

// Plans
export const plans = pgTable('plans', {
  id: uuid('id').primaryKey().defaultRandom(),
  userId: uuid('user_id').notNull().references(() => users.id, { onDelete: 'cascade' }),
  snapshotId: uuid('snapshot_id').references(() => financialSnapshots.id),
  strategyType: varchar('strategy_type', { length: 100 }),
  monthlySavingTarget: decimal('monthly_saving_target', { precision: 12, scale: 2 }),
  monthlyInvestTarget: decimal('monthly_invest_target', { precision: 12, scale: 2 }),
  topActions: jsonb('top_actions').notNull(),
  buckets: jsonb('buckets').notNull(),
  projections: jsonb('projections'),
  confidenceScore: decimal('confidence_score', { precision: 3, scale: 2 }),
  ruleVersion: varchar('rule_version', { length: 20 }).notNull(),
  createdAt: timestamp('created_at').defaultNow().notNull(),
});

// Monthly Progress
export const monthlyProgress = pgTable('monthly_progress', {
  id: uuid('id').primaryKey().defaultRandom(),
  userId: uuid('user_id').notNull().references(() => users.id, { onDelete: 'cascade' }),
  planId: uuid('plan_id').references(() => plans.id),
  month: date('month').notNull(),
  savedAmount: decimal('saved_amount', { precision: 12, scale: 2 }).default('0'),
  investedAmount: decimal('invested_amount', { precision: 12, scale: 2 }).default('0'),
  debtPaid: decimal('debt_paid', { precision: 12, scale: 2 }).default('0'),
  notes: text('notes'),
  status: varchar('status', { length: 20 }),
  createdAt: timestamp('created_at').defaultNow().notNull(),
}, (table) => ({
  uniqueUserMonth: unique().on(table.userId, table.month),
}));

// Recommendation Logs
export const recommendationLogs = pgTable('recommendation_logs', {
  id: uuid('id').primaryKey().defaultRandom(),
  userId: uuid('user_id').notNull().references(() => users.id, { onDelete: 'cascade' }),
  planId: uuid('plan_id').references(() => plans.id),
  ruleVersion: varchar('rule_version', { length: 20 }).notNull(),
  explanationSourceIds: jsonb('explanation_source_ids'),
  modelVersion: varchar('model_version', { length: 50 }),
  contextData: jsonb('context_data'),
  createdAt: timestamp('created_at').defaultNow().notNull(),
});
```

---

## Sample Complete User Dataset

```json
{
  "user": {
    "id": "usr_123",
    "email": "priya@example.com",
    "name": "Priya Sharma"
  },
  "profile": {
    "age": 28,
    "country": "India",
    "dependents": 0,
    "risk_profile": "medium",
    "financial_knowledge": "beginner"
  },
  "snapshot": {
    "monthly_income": 85000,
    "monthly_expenses": 55000,
    "current_savings": 35000
  },
  "assets": [
    {
      "type": "cash",
      "name": "Savings Account",
      "current_value": 35000,
      "liquidity": "high"
    },
    {
      "type": "mf",
      "name": "HDFC Equity Fund",
      "current_value": 45000,
      "liquidity": "medium",
      "expected_return": 0.12
    }
  ],
  "liabilities": [
    {
      "type": "credit_card",
      "name": "HDFC Credit Card",
      "outstanding_amount": 75000,
      "interest_rate": 0.36
    },
    {
      "type": "personal_loan",
      "name": "Personal Loan",
      "outstanding_amount": 120000,
      "interest_rate": 0.14,
      "tenure_months": 24
    }
  ],
  "calculated_metrics": {
    "net_worth": -115000,
    "savings_rate": 0.353,
    "emergency_months": 0.64,
    "debt_to_income": 0.085
  }
}
```

---

**Last Updated:** 2025-12-13  
**Version:** 3.0 (Consolidated)  
**Database:** PostgreSQL with Drizzle ORM
