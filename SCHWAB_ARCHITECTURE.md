# Schwab Futures Integration Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         FinalAI Quantum v7.0                        │
│                    Elite Trading System + Futures                   │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   │
        ┌──────────────────────────┼──────────────────────────┐
        │                          │                          │
        ▼                          ▼                          ▼
┌───────────────┐          ┌───────────────┐         ┌───────────────┐
│  Option 1-21  │          │   Option 22   │         │   Option 23   │
│ Existing      │          │   Futures     │         │  Place Futures│
│ Features      │          │   Dashboard   │         │    Order      │
└───────────────┘          └───────────────┘         └───────────────┘
        │                          │                          │
        │                          └────────────┬─────────────┘
        │                                       │
        │                                       ▼
        │                          ┌─────────────────────────┐
        │                          │ SchwabFuturesTrader     │
        │                          │  Class                  │
        │                          ├─────────────────────────┤
        │                          │ • authenticate()        │
        │                          │ • get_quotes()          │
        │                          │ • place_order()         │
        │                          │ • get_positions()       │
        │                          │ • get_account_info()    │
        │                          └─────────────────────────┘
        │                                       │
        │                                       │
        │                                       ▼
        │                          ┌─────────────────────────┐
        │                          │    schwab-py Library    │
        │                          │  (Official API Client)  │
        │                          └─────────────────────────┘
        │                                       │
        │                                       │
        └───────────────────────────────────────┴─────────────┐
                                                               │
                                                               ▼
                                                  ┌────────────────────┐
                                                  │  Charles Schwab    │
                                                  │  API Endpoints     │
                                                  ├────────────────────┤
                                                  │ • Authentication   │
                                                  │ • Market Data      │
                                                  │ • Trading          │
                                                  │ • Account Info     │
                                                  └────────────────────┘
                                                               │
                                                               ▼
                                                  ┌────────────────────┐
                                                  │  Schwab Account    │
                                                  │  (Live Trading)    │
                                                  └────────────────────┘
```

## Component Flow

### Setup Flow (Option 18)
```
User Input → ConfigurationManager.run_preflight()
    ↓
SchwabFuturesTrader.setup_credentials()
    ↓
User enters App Key & Secret
    ↓
SchwabFuturesTrader.authenticate()
    ↓
Browser OAuth flow
    ↓
Tokens saved to config/schwab_tokens.json
    ↓
Configuration saved to config.json & .env
```

### Dashboard Flow (Option 22)
```
User selects Option 22
    ↓
_show_schwab_futures_dashboard()
    ↓
SchwabFuturesTrader initialized
    ↓
Parallel API calls:
    • get_account_info()
    • get_positions()
    • get_futures_quotes(['/ES', '/NQ', '/CL', ...])
    ↓
Rich tables displayed:
    • Account Information
    • Current Positions (with real-time P&L)
    • Market Quotes
    ↓
User can refresh or place order
```

### Order Flow (Option 23)
```
User selects Option 23
    ↓
_place_schwab_futures_order()
    ↓
Display available contracts
    ↓
User selects: Symbol, Side, Quantity, Type
    ↓
Get real-time quote for confirmation
    ↓
User confirms order
    ↓
SchwabFuturesTrader.place_futures_order()
    ↓
schwab-py builds order object
    ↓
API call to Schwab
    ↓
Order executed
    ↓
Display confirmation with Order ID
```

## Data Flow

### Market Data
```
SchwabFuturesTrader.get_futures_quotes(['/ES', '/NQ'])
    ↓
schwab.client.get_quotes(['/ES', '/NQ'])
    ↓
Schwab API: GET /marketdata/v1/quotes
    ↓
JSON response with bid/ask/last/volume
    ↓
Parsed into dictionary
    ↓
Displayed in rich table
```

### Order Execution
```
place_futures_order(symbol='/ES', quantity=1, side='BUY', type='MARKET')
    ↓
Get account hash from API
    ↓
Build order using schwab.orders.futures
    ↓
schwab.client.place_order(account_hash, order)
    ↓
Schwab API: POST /trader/v1/accounts/{accountHash}/orders
    ↓
HTTP 201 Created
    ↓
Extract Order ID from response headers
    ↓
Return success confirmation
```

## Authentication Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    First-Time Setup                         │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │ User enters App Key    │
              │ and App Secret         │
              └────────────────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │ schwab.auth.easy_client│
              │ opens browser          │
              └────────────────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │ User logs into Schwab  │
              │ via web interface      │
              └────────────────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │ OAuth redirect to      │
              │ https://localhost:8182 │
              └────────────────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │ schwab-py captures     │
              │ authorization code     │
              └────────────────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │ Exchange code for      │
              │ access + refresh token │
              └────────────────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │ Save tokens to:        │
              │ config/schwab_tokens   │
              │        .json           │
              └────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                   Subsequent Sessions                       │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │ Load tokens from file  │
              └────────────────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │ Check token expiry     │
              └────────────────────────┘
                           │
                ┌──────────┴──────────┐
                │                     │
                ▼                     ▼
      ┌─────────────────┐   ┌─────────────────┐
      │ Token expired   │   │ Token valid     │
      └─────────────────┘   └─────────────────┘
                │                     │
                ▼                     │
      ┌─────────────────┐             │
      │ Auto-refresh    │             │
      │ using refresh   │             │
      │ token           │             │
      └─────────────────┘             │
                │                     │
                └──────────┬──────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │ API call with valid    │
              │ access token           │
              └────────────────────────┘
```

## Error Handling Flow

```
API Call Initiated
    │
    ├─→ [Success] → Return data
    │
    ├─→ [401 Unauthorized]
    │       ↓
    │   Attempt token refresh
    │       ↓
    │   Retry API call
    │
    ├─→ [Rate Limited]
    │       ↓
    │   Log warning
    │       ↓
    │   Return error to user
    │
    ├─→ [Network Error]
    │       ↓
    │   Log error
    │       ↓
    │   Display user-friendly message
    │
    └─→ [Other Error]
            ↓
        Log to file
            ↓
        Display error details
```

## Configuration Storage

```
Project Root
│
├── .env
│   ├── SCHWAB_APP_KEY="..."
│   ├── SCHWAB_APP_SECRET="..."
│   └── SCHWAB_CALLBACK_URL="https://localhost:8182"
│
├── config/
│   ├── config.json
│   │   ├── "schwab_futures_enabled": true
│   │   ├── "schwab_app_key": "..."
│   │   └── "schwab_callback_url": "..."
│   │
│   └── schwab_tokens.json  (auto-generated)
│       ├── "access_token": "..."
│       ├── "refresh_token": "..."
│       ├── "expires_at": timestamp
│       └── "scope": [...]
│
└── logs/
    └── finalai_YYYYMMDD.log
        └── Contains all API call logs
```

## Security Model

```
Credential Storage
    │
    ├── App Secret
    │   ├── Stored in .env (not in code)
    │   ├── Git ignored
    │   └── User-level environment variable option
    │
    ├── Access Token
    │   ├── Short-lived (30 minutes)
    │   ├── Auto-refresh mechanism
    │   └── Stored in schwab_tokens.json
    │
    └── Refresh Token
        ├── Long-lived (7 days)
        ├── Used to get new access tokens
        └── Requires re-auth after expiry

OAuth Flow
    │
    ├── Browser-based (not password collection)
    ├── User authenticates with Schwab directly
    └── App never sees user password
```

---

This architecture ensures:
✅ Secure credential management
✅ Smooth user experience
✅ Automatic token refresh
✅ Comprehensive error handling
✅ Clean separation of concerns
