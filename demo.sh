ARG=$1

if [[ $ARG == "--help" ]]; then
  echo "Usage: $0 [OPTION]"
  echo "1) Pathfinding: Milestone one"
  echo "2) Pathfinding: Milestone two"
  echo "3) Pathfinding: Milestone two (debug)"
  echo "4) Collision avoidance: Milestone three"
  echo "5) Collision avoidance: Crash"
  echo "6) Cruise: Learner driver"
  echo "7) Cruise: Stop and go"

  exit 1
fi

ARG=$((ARG))

declare -A DEMOS
DEMOS[1]="python ai_test.py --scenario MilestoneOne --seed 3307178576457248122"
DEMOS[2]="python ai_test.py --scenario MilestoneTwo --seed 2838885953118142194"
DEMOS[3]="python ai_test.py --scenario MilestoneTwo --seed 2838885953118142194 --debug"
DEMOS[4]="python ai_test.py --scenario MilestoneThree --seed 3032819752621599457"
DEMOS[5]="python ai_test.py --scenario Crash --seed 2774128912161005954"
DEMOS[6]="python ai_test.py --scenario LearnerDriver --seed 8568594000893089934"
DEMOS[7]="python ai_test.py --scenario StopAndGo --seed 4435168397950181503"

if [[ $ARG -gt 0 && $ARG -lt 8 ]]; then
  eval ${DEMOS[$ARG]}
else
  echo "Invalid option: $ARG"
  echo "Try '$0 --help' for more information."
fi
