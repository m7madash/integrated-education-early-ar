#!/bin/bash
echo "🛡️ Riba Danger — Demo"
echo "========================"
echo ""
echo "Sample loan detection:"
echo "Principal: 100,000"
echo "Term: 60 months"
echo "Monthly payment: 2,500"
echo "Fees: 500"
echo ""
python3 src/riba_detector/analyze.py --principal 100000 --term 60 --payment 2500 --fees 500
echo ""
echo "📚 See README.md for full usage"
echo "🌐GitHub: https://github.com/m7madash/Abduallh-projects/tree/main/action_projects/riba-danger"
