$ARG = $args[0]

if ($ARG -eq "--help") {
  Write-Host "Usage: $PSCommandPath [OPTION]"
  Write-Host "1) Pathfinding: Milestone one"
  Write-Host "2) Pathfinding: Milestone two"
  Write-Host "3) Pathfinding: Milestone two (debug)"
  Write-Host "4) Collision avoidance: Milestone three"
  Write-Host "5) Collision avoidance: Crash"
  Write-Host "6) Cruise: Learner driver"
  Write-Host "7) Cruise: Stop and go"

  exit 1
}

$ARG = [int]$ARG

$DEMOS = @{
    1 = "python ai_test.py --scenario MilestoneOne --seed 3307178576457248122"
    2 = "python ai_test.py --scenario MilestoneTwo --seed 2838885953118142194"
    3 = "python ai_test.py --scenario MilestoneTwo --seed 2838885953118142194 --debug"
    4 = "python ai_test.py --scenario MilestoneThree --seed 3032819752621599457"
    5 = "python ai_test.py --scenario Crash --seed 2774128912161005954"
    6 = "python ai_test.py --scenario LearnerDriver --seed 8568594000893089934"
    7 = "python ai_test.py --scenario StopAndGo --seed 4435168397950181503"
}

if ($ARG -gt 0 -and $ARG -lt 8) {
  Invoke-Expression $DEMOS[$ARG]
} else {
  Write-Host "Invalid option: $ARG"
  Write-Host "Try '$PSCommandPath --help' for more information."
}
