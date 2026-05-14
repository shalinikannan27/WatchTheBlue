import os

def fix_file(path, replacements):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    for old, new in replacements:
        content = content.replace(old, new)
        
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

# 1. backend/main.py
fix_file('backend/main.py', [
    ('datetime.utcnow()', 'datetime.now(timezone.utc)'),
    ('from datetime import datetime', 'from datetime import datetime, timezone'),
    ('max_prob = r["risk_probability"]', 'max_prob = float(r["risk_probability"])'),
    ('if r["risk_probability"] > max_prob:', 'if float(r["risk_probability"]) > max_prob:')
])

# 2. backend/cmems_fetch.py
fix_file('backend/cmems_fetch.py', [
    ('datetime.utcnow()', 'datetime.now(timezone.utc)'),
    ('from datetime import datetime', 'from datetime import datetime, timezone')
])

# 3. backend/drift/drift_model.py
fix_file('backend/drift/drift_model.py', [
    ('datetime.utcnow()', 'datetime.now(timezone.utc)'),
    ('from datetime import datetime, timedelta', 'from datetime import datetime, timedelta, timezone')
])

# 4. backend/ml_inference.py
fix_file('backend/ml_inference.py', [
    ('float(row.get(name, 0.0))', 'row.get(name, 0.0)'),
    ('float(est.predict(x_row)[0])', 'est.predict(x_row)[0]'),
    ('float(importances[idx])', 'importances[idx]'),
    ('int(month)', 'month'),
    ('int(row.get("month", 1))', 'row.get("month", 1)')
])

print("Fixed backend files")
