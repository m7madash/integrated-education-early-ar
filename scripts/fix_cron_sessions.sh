#!/bin/bash
# Fix cron sessionTarget for all mission jobs (change from main to isolated)

MISSION_IDS=(
  "d4cb02dd-1e78-4fca-9aa6-351ea42d3f84" # poverty-dignity
  "ba9207e1-c6d3-4c8a-9524-9d1d56963930" # dhikr-morning
  "0d4ad1b9-9565-4922-aaa6-d1a11bb6e856" # war-peace
  "eff44d2c-090c-4c31-862c-6874c55c5096" # shirk-tawhid
  "364af229-9f63-405c-8cf6-9f5125aa6199" # pollution-cleanliness
  "2eafc3de-87be-49d6-8586-3db549fad2c9" # disease-health
  "95fa3334-9f91-4fb4-b9a0-1304e8fefa69" # slavery-freedom
  "c7f8b9e2-1a3d-4f6e-9b8c-2d4e5f6a7b8c" # corruption-reform
  "a2d80f54-2a9c-4529-9595-bca33ce7961e" # extremism-moderation
  "44979dac-72d6-4411-8fe6-ad2077bfd0c1" # ignorance-knowledge
  "20f7ac63-3d26-417a-952a-e67aea5f80cf" # dhikr-evening
  "quran-study-1777964046981"            # quran-study (named id)
  "wise-disagreement-1778010728547"      # wise-disagreement
  "868f5442-6b2b-4675-be00-231c82f83746" # anti_extortion_weekly
  "37562876-2b7a-4502-8048-d3d0f89d4c6d" # modesty_mode_weekly
)

for id in "${MISSION_IDS[@]}"; do
  echo "🔧 Fixing $id..."
  openclaw cron edit "$id" --session isolated 2>&1 | head -3
done

echo "✅ Batch fix complete"
