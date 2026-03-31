# Schwab Futures Integration - Testing Checklist

## Pre-Testing Setup

- [ ] Python environment active
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] Schwab developer account created
- [ ] API app registered on developer.schwab.com
- [ ] App Key and App Secret obtained
- [ ] Schwab account has futures trading enabled

## Installation Tests

### 1. Library Installation
- [ ] Run: `pip install schwab-py`
- [ ] Verify: `python -c "import schwab; print('OK')"`
- [ ] Expected: Output shows "OK"

### 2. Setup Script
- [ ] Run: `powershell -ExecutionPolicy Bypass -File setup_schwab.ps1`
- [ ] Verify: Script completes without errors
- [ ] Expected: Instructions displayed

## Application Tests

### 3. First Launch
- [ ] Run: `python Trading.py`
- [ ] Verify: Application starts without errors
- [ ] Verify: Dependency check shows schwab-py status
- [ ] Expected: Main menu displays options 1-23

### 4. Initial Configuration (Option 18)
- [ ] Select: Option 18 (Preflight Setup)
- [ ] Step through: Polygon.io setup (optional)
- [ ] Step through: Telegram setup (optional)
- [ ] Step through: Schwab futures setup
- [ ] Answer "yes" to enable Schwab futures
- [ ] Enter: Valid App Key
- [ ] Enter: Valid App Secret
- [ ] Expected: Browser opens for OAuth

### 5. OAuth Authentication
- [ ] Browser: Schwab login page appears
- [ ] Login: With Schwab credentials
- [ ] Authorize: Allow app access
- [ ] Expected: Redirect to localhost:8182
- [ ] Expected: Terminal shows "Successfully authenticated"
- [ ] Verify: `config/schwab_tokens.json` created
- [ ] Verify: `.env` contains SCHWAB_APP_KEY and SCHWAB_APP_SECRET
- [ ] Verify: `config/config.json` has `schwab_futures_enabled: true`

### 6. Header Display
- [ ] Return to main menu
- [ ] Verify: Header shows "🚀 Schwab Futures Trading: ENABLED"
- [ ] Verify: Welcome banner displays (first time only)
- [ ] Expected: Green banner with options 22 & 23 highlighted

## Dashboard Tests (Option 22)

### 7. View Dashboard
- [ ] Select: Option 22 (Schwab Futures Dashboard)
- [ ] Verify: Account Information table displays
- [ ] Check: Account Type shown
- [ ] Check: Cash Balance shown
- [ ] Check: Buying Power shown
- [ ] Check: Total Equity shown
- [ ] Check: Available Funds shown

### 8. Position Display
- [ ] If positions exist: Position table displays
- [ ] Verify: Symbol, Quantity, Avg Price shown
- [ ] Verify: Market Value shown
- [ ] Verify: P&L shown with colors (green/red)
- [ ] If no positions: "No open positions" message

### 9. Market Quotes
- [ ] Verify: Market Quotes table displays
- [ ] Check: /ES quote shown
- [ ] Check: /NQ quote shown
- [ ] Check: /YM quote shown
- [ ] Check: /CL quote shown
- [ ] Check: /GC quote shown
- [ ] Verify: Last price, Change, Bid, Ask, Volume all populated

### 10. Dashboard Navigation
- [ ] Select: 1 (Refresh Dashboard)
- [ ] Verify: Dashboard reloads with updated data
- [ ] Select: 2 (Place Order)
- [ ] Verify: Redirects to order placement screen
- [ ] Select: 3 (Back to Main Menu)
- [ ] Verify: Returns to main menu

## Order Placement Tests (Option 23)

### 11. Order Screen Display
- [ ] Select: Option 23 (Place Futures Order)
- [ ] Verify: Contract selection menu displays
- [ ] Verify: 8 popular contracts listed
- [ ] Verify: Option 9 for custom symbol

### 12. Market Order - Buy (PAPER TEST ONLY)
⚠️ **WARNING: This will execute a real trade! Use smallest quantity**

- [ ] Select: Contract (e.g., /ES)
- [ ] Verify: Current market quote displays
- [ ] Select: 1 (BUY - Long)
- [ ] Enter: Quantity = 1
- [ ] Select: 1 (MARKET order)
- [ ] Verify: Confirmation screen shows all details
- [ ] Verify: Symbol, Side, Quantity, Type correct
- [ ] Cancel order: Answer "No" to confirmation
- [ ] Expected: "Order cancelled" message

### 13. Limit Order - Sell
⚠️ **WARNING: This will execute a real trade! Use smallest quantity**

- [ ] Select: Contract (e.g., /NQ)
- [ ] Verify: Current quote displays
- [ ] Select: 2 (SELL - Short)
- [ ] Enter: Quantity = 1
- [ ] Select: 2 (LIMIT order)
- [ ] Enter: Limit price (far from market to avoid fill)
- [ ] Verify: Confirmation shows limit price
- [ ] Cancel order: Answer "No"
- [ ] Expected: "Order cancelled"

### 14. Custom Symbol
- [ ] Select: 9 (Custom symbol)
- [ ] Enter: /SI (Silver)
- [ ] Verify: Quote fetched successfully
- [ ] Cancel order before placing

### 15. Order Validation
- [ ] Try: Invalid symbol (e.g., "TEST")
- [ ] Expected: Error message or no quote
- [ ] Try: Empty quantity
- [ ] Expected: Prompt to enter valid number

## Integration Tests

### 16. Analyze Futures (Option 1)
- [ ] Select: Option 1 (Analyze Stock/Crypto)
- [ ] Enter: /ES
- [ ] Verify: Data fetched from yfinance
- [ ] Verify: Technical indicators calculated
- [ ] Verify: AI analysis runs
- [ ] Expected: Full analysis report for /ES

### 17. Multi-Timeframe Futures (Option 9)
- [ ] Select: Option 9 (Multi-Timeframe)
- [ ] Enter: /NQ
- [ ] Verify: Analysis across multiple timeframes
- [ ] Expected: Timeframe comparison table

### 18. Market Scanner with Futures
- [ ] Select: Option 2 (Market Scanner)
- [ ] Add: futures universe or individual futures
- [ ] Verify: Scanner processes futures symbols
- [ ] Expected: Results include futures (if in universe)

## Error Handling Tests

### 19. Missing Authentication
- [ ] Delete: `config/schwab_tokens.json`
- [ ] Select: Option 22 or 23
- [ ] Expected: "Not authenticated" error
- [ ] Expected: Prompt to run Option 18

### 20. Invalid Credentials
- [ ] Edit: .env with invalid App Key
- [ ] Run: Option 18 authentication
- [ ] Expected: Authentication fails gracefully
- [ ] Expected: Error message shown

### 21. Network Error Simulation
- [ ] Disconnect: Internet connection
- [ ] Select: Option 22
- [ ] Expected: Network error caught
- [ ] Expected: User-friendly error message
- [ ] Reconnect: Internet

### 22. Rate Limit Handling
- [ ] Rapidly: Call get_futures_quotes many times
- [ ] Expected: Rate limit error caught (if exceeded)
- [ ] Expected: Graceful degradation

## Documentation Tests

### 23. File Existence
- [ ] Verify: `SCHWAB_FUTURES_GUIDE.md` exists
- [ ] Verify: `SCHWAB_QUICKREF.md` exists
- [ ] Verify: `SCHWAB_IMPLEMENTATION.md` exists
- [ ] Verify: `SCHWAB_ARCHITECTURE.md` exists
- [ ] Verify: `SCHWAB_README.md` exists
- [ ] Verify: `setup_schwab.ps1` exists

### 24. Documentation Accuracy
- [ ] Open: SCHWAB_FUTURES_GUIDE.md
- [ ] Verify: Setup instructions match actual flow
- [ ] Verify: All links work
- [ ] Verify: Screenshots/diagrams accurate (if any)

### 25. Code Documentation
- [ ] Check: SchwabFuturesTrader class has docstrings
- [ ] Check: All methods have docstrings
- [ ] Check: Complex logic has comments
- [ ] Run: `python -m pydoc Trading` (should work)

## Security Tests

### 26. Credential Storage
- [ ] Check: .env file not in git (verify .gitignore)
- [ ] Check: schwab_tokens.json not in git
- [ ] Check: API Secret not logged in plaintext
- [ ] Check: Tokens stored in secure location

### 27. Input Validation
- [ ] Try: SQL injection in symbol field
- [ ] Try: Very large quantity (1000000)
- [ ] Try: Negative quantity
- [ ] Expected: All handled safely

## Performance Tests

### 28. Dashboard Load Time
- [ ] Measure: Time to load Option 22
- [ ] Expected: < 3 seconds
- [ ] Verify: Progress indicators shown (if slow)

### 29. Quote Refresh
- [ ] In dashboard: Press 1 to refresh multiple times
- [ ] Verify: No memory leaks
- [ ] Verify: Performance doesn't degrade

## Logging Tests

### 30. Log File Creation
- [ ] Check: `logs/finalai_YYYYMMDD.log` exists
- [ ] Verify: Schwab API calls logged
- [ ] Verify: Errors logged with stack traces
- [ ] Verify: No sensitive data in logs

### 31. Error Logging
- [ ] Trigger: Authentication error
- [ ] Check: Error logged to file
- [ ] Verify: Log level appropriate (ERROR)
- [ ] Verify: Timestamp present

## Cleanup Tests

### 32. Configuration Persistence
- [ ] Close: Application
- [ ] Restart: Application
- [ ] Verify: Schwab still enabled
- [ ] Verify: Auto-login works (tokens valid)

### 33. Disable Feature
- [ ] Edit: config.json, set `schwab_futures_enabled: false`
- [ ] Restart: Application
- [ ] Select: Option 22
- [ ] Expected: "Not enabled" message
- [ ] Re-enable: via Option 18

## Edge Cases

### 34. Token Expiration
- [ ] Wait: For token to expire (or manually expire)
- [ ] Use: Dashboard or place order
- [ ] Expected: Auto-refresh triggers
- [ ] Expected: Operation completes successfully

### 35. Concurrent Sessions
- [ ] Open: Two terminals with FinalAI
- [ ] Both: Use Schwab features simultaneously
- [ ] Expected: Both work independently
- [ ] Expected: Token refresh handled

### 36. Market Closed
- [ ] Test: During market closed hours
- [ ] Verify: Quotes still returned (last close)
- [ ] Verify: Order placement works (queued for open)

## Final Verification

### 37. Complete User Journey
- [ ] Fresh install on new machine/VM
- [ ] Follow: SCHWAB_FUTURES_GUIDE.md step-by-step
- [ ] Complete: Full setup to first trade
- [ ] Time: Total setup time < 15 minutes
- [ ] Expected: Successful end-to-end flow

### 38. Code Quality
- [ ] No syntax errors
- [ ] No import errors
- [ ] No undefined variables
- [ ] All functions return expected types
- [ ] Exception handling in all API calls

### 39. User Experience
- [ ] UI is intuitive
- [ ] Error messages are helpful
- [ ] Success feedback is clear
- [ ] Loading states indicated
- [ ] Colors/formatting enhances readability

## Test Results Summary

**Date**: _______________
**Tester**: _______________
**Version**: FinalAI Quantum v7.0

| Category | Tests Passed | Tests Failed | Notes |
|----------|--------------|--------------|-------|
| Installation | ___ / 2 | | |
| Configuration | ___ / 3 | | |
| Dashboard | ___ / 4 | | |
| Orders | ___ / 6 | | |
| Integration | ___ / 3 | | |
| Error Handling | ___ / 4 | | |
| Documentation | ___ / 3 | | |
| Security | ___ / 2 | | |
| Performance | ___ / 2 | | |
| Logging | ___ / 2 | | |
| Cleanup | ___ / 2 | | |
| Edge Cases | ___ / 3 | | |
| Final Verification | ___ / 3 | | |
| **TOTAL** | **___ / 39** | | |

## Issues Found

1. _______________________________________________
2. _______________________________________________
3. _______________________________________________

## Sign-Off

- [ ] All critical tests passed
- [ ] Documentation is accurate
- [ ] No security vulnerabilities found
- [ ] Ready for production use

**Approved by**: _______________
**Date**: _______________

---

## Notes

- ⚠️ Tests marked with "PAPER TEST ONLY" should use minimal quantities
- 🔴 Never test real orders without understanding consequences
- 💡 Keep a test log for future reference
- 📝 Update this checklist if new features added
