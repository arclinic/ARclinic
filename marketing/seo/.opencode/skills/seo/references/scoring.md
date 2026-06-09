# SEO Audit Scoring Methodology

## Weight Categories

```
Final Score = Technical(30%) + Content(30%) + Schema(20%) + GEO(20%)
```

## Grade Thresholds

| Score | Grade | Meaning |
|-------|-------|---------|
| 90-100 | A | Excellent, minor polish only |
| 80-89 | B+ | Good foundation, fix warnings |
| 70-79 | B | Average, notable improvements needed |
| 60-69 | C | Below average, significant issues |
| 40-59 | D | Poor, major overhaul needed |
| 0-39 | F | Critical, site has fundamental problems |

## Finding Severity Levels

- **critical** (-10 to -20 points): Blocks ranking or AI citation
- **warning** (-3 to -7 points): Reduces effectiveness
- **info** (0 points): Improvement opportunity

## Every Finding Must Include

1. **Issue**: what's wrong
2. **Fix**: specific actionable fix
3. **Indicator**: how to verify improvement (metric or check)

## Example Falsifiable Finding

```json
{
  "severity": "critical",
  "check": "no_https",
  "issue": "Site not using HTTPS",
  "fix": "Install Let's Encrypt SSL certificate",
  "indicator": "Browser shows lock icon; no mixed-content warnings in console"
}
```

"How would we know the fix failed?" = falsifiability check.
