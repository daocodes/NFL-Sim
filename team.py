import random


class Team:
    def __init__(self, name, conference, division, rating, stadium_rating):
        self.name = name
        self.conference = conference
        self.division = division
        self.rating = rating
        self.stadium_rating = stadium_rating
        self.schedule = {}  # week: (opponent, home/away)
        self.wins = 0
        self.losses = 0
        self.playoffs = False

    def __str__(self):
        return f"{self.name} ({self.conference} {self.division})"


def create_teams():
    teams = [
        # AFC East
        Team("Buffalo Bills", "AFC", "East", 75, 65),
        Team("Miami Dolphins", "AFC", "East", 68, 55),
        Team("New England Patriots", "AFC", "East", 45, 60),
        Team("New York Jets", "AFC", "East", 58, 70),
        # AFC North
        Team("Cincinnati Bengals", "AFC", "North", 72, 62),
        Team("Baltimore Ravens", "AFC", "North", 80, 68),
        Team("Pittsburgh Steelers", "AFC", "North", 63, 75),
        Team("Cleveland Browns", "AFC", "North", 60, 58),
        # AFC South
        Team("Jacksonville Jaguars", "AFC", "South", 55, 45),
        Team("Tennessee Titans", "AFC", "South", 50, 50),
        Team("Indianapolis Colts", "AFC", "South", 53, 48),
        Team("Houston Texans", "AFC", "South", 67, 52),
        # AFC West
        Team("Kansas City Chiefs", "AFC", "West", 95, 80),
        Team("Los Angeles Chargers", "AFC", "West", 57, 40),
        Team("Las Vegas Raiders", "AFC", "West", 52, 68),
        Team("Denver Broncos", "AFC", "West", 48, 72),
        # NFC East
        Team("Philadelphia Eagles", "NFC", "East", 85, 78),
        Team("Dallas Cowboys", "NFC", "East", 82, 77),
        Team("New York Giants", "NFC", "East", 42, 65),
        Team("Washington Commanders", "NFC", "East", 40, 55),
        # NFC North
        Team("Detroit Lions", "NFC", "North", 73, 70),
        Team("Green Bay Packers", "NFC", "North", 68, 78),
        Team("Minnesota Vikings", "NFC", "North", 60, 72),
        Team("Chicago Bears", "NFC", "North", 50, 60),
        # NFC South
        Team("Tampa Bay Buccaneers", "NFC", "South", 54, 58),
        Team("New Orleans Saints", "NFC", "South", 62, 75),
        Team("Carolina Panthers", "NFC", "South", 35, 50),
        Team("Atlanta Falcons", "NFC", "South", 45, 54),
        # NFC West
        Team("San Francisco 49ers", "NFC", "West", 94, 76),
        Team("Seattle Seahawks", "NFC", "West", 65, 98),  # Super tough stadium
        Team("Los Angeles Rams", "NFC", "West", 58, 66),
        Team("Arizona Cardinals", "NFC", "West", 40, 50),
    ]
    return teams


def group_by_division(teams):
    divisions = {}
    for team in teams:
        key = (team.conference, team.division)
        if key not in divisions:
            divisions[key] = []
        divisions[key].append(team)
    return divisions


def assign_games_safely(team1, team2, divisions):
    """Helper function to safely assign games without duplicates"""
    # Get available weeks where neither team is already scheduled
    available_weeks = [
        w for w in range(1, 19) if w not in team1.schedule and w not in team2.schedule
    ]

    if available_weeks:
        week = random.choice(available_weeks)
        if random.choice([True, False]):
            team1.schedule[week] = (team2.name, "home")
            team2.schedule[week] = (team1.name, "away")
        else:
            team1.schedule[week] = (team2.name, "away")
            team2.schedule[week] = (team1.name, "home")
        return True
    return False


def assign_division_games(divisions):
    for division_teams in divisions.values():
        for i, team1 in enumerate(division_teams):
            for j in range(i + 1, len(division_teams)):
                team2 = division_teams[j]
                # Assign two games (home and away)
                assign_games_safely(team1, team2, divisions)
                assign_games_safely(team1, team2, divisions)


def assign_intraconference_games(divisions):
    conferences = ["AFC", "NFC"]
    for conference in conferences:
        conf_divisions = [d for d in divisions.keys() if d[0] == conference]
        for i, (conf, div1) in enumerate(conf_divisions):
            (conf, div2) = conf_divisions[(i + 1) % len(conf_divisions)]
            for team1 in divisions[(conf, div1)]:
                for team2 in divisions[(conf, div2)]:
                    assign_games_safely(team1, team2, divisions)


def assign_interconference_games(divisions):
    afc_divs = [d[1] for d in divisions.keys() if d[0] == "AFC"]
    nfc_divs = [d[1] for d in divisions.keys() if d[0] == "NFC"]

    for afc_div, nfc_div in zip(afc_divs, nfc_divs):
        for team1 in divisions[("AFC", afc_div)]:
            for team2 in divisions[("NFC", nfc_div)]:
                assign_games_safely(team1, team2, divisions)


def assign_bye_weeks(teams):
    for team in teams:
        available_weeks = [
            w
            for w in range(4, 15)  # Byes typically weeks 4-14
            if w not in team.schedule
        ]
        if not available_weeks:
            available_weeks = [w for w in range(1, 19) if w not in team.schedule]
        if available_weeks:
            week = random.choice(available_weeks)
            team.schedule[week] = ("BYE", "")


def validate_schedule(teams):
    """Check for scheduling conflicts"""
    valid = True
    for team in teams:
        weekly_counts = {}
        for week in team.schedule:
            weekly_counts[week] = weekly_counts.get(week, 0) + 1
            if weekly_counts[week] > 1:
                print(f"ERROR: {team.name} has multiple games in week {week}")
                valid = False
    return valid


def fix_duplicate_games(teams):
    """Clean up duplicate matchups"""
    team_map = {t.name: t for t in teams}

    for week in range(1, 19):
        scheduled_pairs = set()

        for team in teams:
            if week in team.schedule:
                opp, loc = team.schedule[week]
                if opp == "BYE":
                    continue

                pair = frozenset({team.name, opp})
                if pair in scheduled_pairs:
                    # Remove duplicate
                    del team.schedule[week]
                    del team_map[opp].schedule[week]
                else:
                    scheduled_pairs.add(pair)


def fill_remaining_games(teams):

    # First assign bye weeks to teams that need them
    teams_needing_bye = [
        t for t in teams if "BYE" not in [opp for opp, _ in t.schedule.values()]
    ]
    for team in teams_needing_bye:
        available_weeks = [w for w in range(1, 19) if w not in team.schedule]
        if available_weeks:
            week = random.choice(available_weeks)
            team.schedule[week] = ("BYE", "")

    # Now ensure proper pairing for remaining games
    for week in range(1, 19):
        # Get teams not playing this week (excluding byes)
        available_teams = [
            t for t in teams if week not in t.schedule or t.schedule[week][0] == "BYE"
        ]

        # Remove teams with byes this week
        available_teams = [
            t
            for t in available_teams
            if week not in t.schedule or t.schedule[week][0] != "BYE"
        ]

        # Ensure even number of available teams
        if len(available_teams) % 2 != 0:
            # If odd number, find a team that could move their bye
            for t in available_teams:
                if "BYE" in [opp for opp, _ in t.schedule.values()]:
                    bye_week = [
                        w for w, (opp, _) in t.schedule.items() if opp == "BYE"
                    ][0]
                    t.schedule.pop(bye_week)
                    available_teams.append(t)
                    break

        # Pair up teams for this week
        random.shuffle(available_teams)
        for i in range(0, len(available_teams), 2):
            if i + 1 >= len(available_teams):
                break
            team1 = available_teams[i]
            team2 = available_teams[i + 1]

            if random.choice([True, False]):
                team1.schedule[week] = (team2.name, "home")
                team2.schedule[week] = (team1.name, "away")
            else:
                team1.schedule[week] = (team2.name, "away")
                team2.schedule[week] = (team1.name, "home")


def get_weekly_matchups(teams):
    weekly_matchups = {week: [] for week in range(1, 19)}

    for team in teams:
        for week, (opponent, loc) in team.schedule.items():
            if opponent != "BYE" and loc == "home":
                weekly_matchups[week].append((team.name, opponent))

    return weekly_matchups


def playGame(team1, team2):
    # Determine win probability based solely on team ratings
    if team1 == team2:
        pass
    total_rating = team1.rating + team2.rating
    team1_prob = team1.rating / total_rating

    if random.random() < team1_prob:
        winner, loser = team1, team2
    else:
        winner, loser = team2, team1

    # Update win/loss records and rating
    winner.wins += 1
    winner.rating += 3
    loser.rating += 3  # Rating boost for winner
    loser.losses += 1

    print(f"{winner.name} beats {loser.name}")
    return winner


def loopGames(weekly_matchups, teams):
    # Iterate through each week
    for week, matchups in weekly_matchups.items():
        print(f"Week {week} Matchups:")

        # Iterate through the matchups for this week
        for matchup in matchups:
            team1_name, team2_name = matchup

            # Find the teams by name
            team1 = next(team for team in teams if team.name == team1_name)
            team2 = next(team for team in teams if team.name == team2_name)

            # Simulate the game
            playGame(team1, team2)

        print("-" * 30)

        # After all games for the week, print the record for each team
        print(f"After Week {week} Results:")
        for team in teams:
            print(
                f"{team.name} - Wins: {team.wins}, Losses: {team.losses}, Rating: {team.rating}"
            )
        print("-" * 30)


def setPlayoffs(teams):
    # Sort teams by wins (descending)
    for i in range(1, len(teams)):
        key = teams[i]
        j = i - 1
        while j >= 0 and key.wins > teams[j].wins:
            teams[j + 1] = teams[j]
            j -= 1
        teams[j + 1] = key

    afcPlayoffs = []
    nfcPlayoffs = []

    for team in teams:
        if team.conference == "AFC" and len(afcPlayoffs) < 7:
            afcPlayoffs.append(team)
        elif team.conference == "NFC" and len(nfcPlayoffs) < 7:
            nfcPlayoffs.append(team)

        # Stop once both are filled
        if len(afcPlayoffs) == 7 and len(nfcPlayoffs) == 7:
            break

    return afcPlayoffs, nfcPlayoffs


def printPlayoffBracket(afcPlayoffs, nfcPlayoffs):
    print("-" * 60)
    print("                      WILD CARD ROUND")
    print("-" * 60)
    print("NFC:")
    print("First Round Bye:", nfcPlayoffs[0])

    print(nfcPlayoffs[1], "vs.", nfcPlayoffs[6])
    nfcWinner27 = playGame(nfcPlayoffs[1], nfcPlayoffs[6])
    print(nfcPlayoffs[2], "vs.", nfcPlayoffs[5])
    nfcWinner36 = playGame(nfcPlayoffs[2], nfcPlayoffs[5])
    print(nfcPlayoffs[3], "vs.", nfcPlayoffs[4])
    nfcWinner54 = playGame(nfcPlayoffs[3], nfcPlayoffs[4])
    print("AFC:")
    print("First Round Bye:", afcPlayoffs[0])
    print(afcPlayoffs[1], "vs.", afcPlayoffs[6])
    afcWinner27 = playGame(afcPlayoffs[1], afcPlayoffs[6])
    print(afcPlayoffs[2], "vs.", afcPlayoffs[5])
    afcWinner36 = playGame(afcPlayoffs[2], afcPlayoffs[5])
    print(afcPlayoffs[3], "vs.", afcPlayoffs[4])
    afcWinner54 = playGame(afcPlayoffs[3], afcPlayoffs[4])
    input("Type anything to simulate to the next round")
    print("-" * 60)
    print("                      Divisional Round")
    print("-" * 60)
    print(nfcPlayoffs[0], "vs.", nfcWinner54)
    nfcchamp1 = playGame(nfcPlayoffs[0], nfcWinner54)
    print(nfcWinner36, "vs.", nfcWinner27)
    nfcchamp2 = playGame(nfcWinner36, nfcWinner27)
    print(afcPlayoffs[0], "vs.", afcWinner54)
    afcchamp1 = playGame(afcPlayoffs[0], afcWinner54)
    print(afcWinner36, "vs.", afcWinner27)
    afcchamp2 = playGame(afcWinner36, afcWinner27)
    input("Type anything to simulate to the next round")
    print("-" * 60)
    print("                      Championship Round")
    print("-" * 60)
    print(nfcchamp1, "vs.", nfcchamp2)
    nfcchamp = playGame(nfcchamp1, nfcchamp2)
    print(afcchamp1, "vs.", afcchamp2)
    afcchamp = playGame(afcchamp1, afcchamp2)
    input("Type anything to simulate to the next round")
    print("-" * 60)
    print("                      SUPER BOWL!!!!!!!")
    print("-" * 60)
    print(nfcchamp, "vs.", afcchamp)
    win = playGame(nfcchamp, afcchamp)
    print("THE", win, "HAVE WON THE SUPER BOWL!!!!!!!!!!")


def main():
    teams = create_teams()
    divisions = group_by_division(teams)

    # Assign games in proper order
    assign_division_games(divisions)  # 6 games
    assign_intraconference_games(divisions)  # 4 games
    assign_interconference_games(divisions)  # 4 games

    # Validate before proceeding
    if not validate_schedule(teams):
        print("Scheduling conflicts detected! Regenerating...")
        return main()  # Try again if conflicts found

    assign_bye_weeks(teams)  # 1 bye week
    fill_remaining_games(teams)  # 2 games

    # Get weekly matchups
    weekly_matchups = get_weekly_matchups(teams)

    # Final validation and loop through games
    loopGames(weekly_matchups, teams)
    afcPlayoffs, nfcPlayoffs = setPlayoffs(teams)

    printPlayoffBracket(afcPlayoffs, nfcPlayoffs)


if __name__ == "__main__":
    main()
