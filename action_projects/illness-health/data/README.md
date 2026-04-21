# Illness → Health — Data Directory

Contains medical knowledge databases in JSON format.

## Files

- `conditions.json` — medical conditions (symptoms, severity, treatment, sources)
- `medications.json` — drug information (dose, contraindications, alternatives)
- `aid_organizations.json` — clinics, hospitals, hotlines by region

## Data Sources

Conditions and medications initially sourced from:
- WHO Essential Medicines List
- CDC Guidelines (Common Cold, Influenza)
- WHO COVID-19 Clinical Management
- American Diabetes Association

## Expanding the Database

To add a new condition:
```json
{
  "id": "unique_id",
  "name": "English Name",
  "name_ar": "الاسم العربي",
  "symptoms": ["symptom1", "symptom2"],
  "severity": "mild|moderate|severe|critical",
  "contagious": true/false,
  "typical_duration_days": 7,
  "treatment_guidelines": ["step1", "step2"],
  "recommended_medications": ["med_id_1", "med_id_2"],
  "when_to_see_doctor": ["indication1", "indication2"],
  "source": "Guideline Name Year",
  "source_url": "https://..."
}
```

Always cite trusted medical sources. No personal opinions.

## Privacy

Raw patient data NEVER stored here. Only reference data.

🕌 Developed under Islamic ethics: preserve life, no harm, no data exploitation.
