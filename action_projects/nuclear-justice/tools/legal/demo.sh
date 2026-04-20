#!/bin/bash
# Demo for Legal Qaeda (Tool 2 — Nuclear Justice)
# Runs ICJ case generator, ICC indictment builder, and sanctions generator

cd /root/.openclaw/workspace/action_projects/nuclear-justice/tools/legal

echo "=========================================="
echo "LEGAL QAEDA — DEMO"
echo "Tool 2 of PROJECT OMAR"
echo "=========================================="
echo ""

echo "[1] Running ICJ case generator..."
python3 legal_qaeda_cli.py --tool icj \
  --applicant "Islamic Republic of Iran" \
  --respondent "State X" \
  --facts /root/.openclaw/workspace/action_projects/nuclear-justice/tools/legal/docs/sample_facts.json \
  --output demo_icj_case.md 2>&1 || echo "   (facts JSON missing — will create next)"
  
# Create sample facts JSON if not exists
if [ ! -f docs/sample_facts.json ]; then
  cat > docs/sample_facts.json << 'JSON'
[
  {"date":"2025-03-15","description":"Test enrichment to 90% U-235 at Facility A","evidence":"Satellite imagery Annex A"},
  {"date":"2025-04-01","description":"Public threat to use nuclear weapons against neighbor states","evidence":"State TV transcript Annex B"}
]
JSON
  echo "   Created docs/sample_facts.json"
fi

echo ""
echo "[2] Running ICC indictment generator..."
python3 legal_qaeda_cli.py --tool icc \
  --suspect "General X" \
  --title "Head of Strategic Forces" \
  --position "Commander, Nuclear Missile Command" \
  --nationality "State X" \
  --output demo_icc_indictment.md

echo ""
echo "[3] Running sanctions generator..."
# Create sample persons CSV
cat > /tmp/persons.csv << CSV
name,title,organization,country,risk_score,sanction_type
Dr. Ahmad Vahidi,Minister of Defense,Ministry of Defense,State X,9,both
General Y,Head of Nuclear Command,Strategic Forces Command,State X,10,both
Dr. Z,Chief Scientist,Nuclear Research Center,State X,7,asset_freeze
CSV

# Create sample orgs CSV
cat > /tmp/orgs.csv << CSV
name,type,country,risk_score,justification
Atomic Energy Organization of State X,state_enterprise,State X,8,Controls all nuclear material
Bank X,bank,State X,6,Facilitates financial transactions for prohibited program
CSV

python3 legal_qaeda_cli.py --tool sanctions \
  --persons /tmp/persons.csv \
  --organizations /tmp/orgs.csv \
  --evidence "Satellite imagery + procurement records + official decrees" \
  --prefix demo_sanctions

echo ""
echo "=========================================="
echo "✅ Legal Qaeda demo completed."
echo "Outputs:"
echo "  - demo_icj_case.md"
echo "  - demo_icc_indictment.md"
echo "  - demo_sanctions.json + _persons.csv + _orgs.csv"
echo "=========================================="
