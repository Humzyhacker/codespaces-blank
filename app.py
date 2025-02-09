from flask import Flask, render_template, request, jsonify, redirect, url_for
import requests
from bs4 import BeautifulSoup
import numpy as np
from scipy.stats import poisson
import threading

app = Flask(__name__)

# List of URLs for multiple matches
urls = [
    "https://www.superior.tips/predictions/february-6-25/wellington-phoenix-vs-brisbane-roar-betting-tips",
    "https://www.superior.tips/predictions/february-6-25/valencia-vs-barcelona-betting-tips",
    "https://www.superior.tips/predictions/february-7-25/rayo-vallecano-vs-valladolid-betting-tips",
    "https://www.superior.tips/predictions/february-7-25/bayern-munchen-vs-werder-bremen-betting-tips",
    "https://www.superior.tips/predictions/february-7-25/como-vs-juventus-betting-tips",
    "https://www.superior.tips/predictions/february-7-25/nantes-vs-stade-brestois-29-betting-tips",
    "https://www.superior.tips/predictions/february-7-25/paris-saint-germain-vs-monaco-betting-tips",
    "https://www.superior.tips/predictions/february-7-25/fc-porto-vs-sporting-cp-betting-tips",
    "https://www.superior.tips/predictions/february-7-25/cibao-vs-guadalajara-chivas-betting-tips",
    "https://www.superior.tips/predictions/february-7-25/cavalry-fc-vs-unam-pumas-betting-tips",
    "https://www.superior.tips/predictions/february-7-25/mansfield-town-vs-northampton-betting-tips",
    "https://www.superior.tips/predictions/february-7-25/albacete-vs-zaragoza-betting-tips",
    "https://www.superior.tips/predictions/february-7-25/spvgg-greuther-furth-vs-ssv-jahn-regensburg-betting-tips",
    "https://www.superior.tips/predictions/february-7-25/brescia-vs-salernitana-betting-tips",
    "https://www.superior.tips/predictions/february-7-25/grenoble-vs-red-star-fc-93-betting-tips",
    "https://www.superior.tips/predictions/february-7-25/paris-fc-vs-pau-betting-tips",
    "https://www.superior.tips/predictions/february-7-25/rodez-vs-bastia-betting-tips",
    "https://www.superior.tips/predictions/february-7-25/banfield-vs-belgrano-cordoba-betting-tips",
    "https://www.superior.tips/predictions/february-7-25/central-cordoba-de-santiago-vs-newells-old-boys-betting-tips",
    "https://www.superior.tips/predictions/february-7-25/huracan-vs-tigre-betting-tips",
    "https://www.superior.tips/predictions/february-7-25/samsunspor-vs-hatayspor-betting-tips",
    "https://www.superior.tips/predictions/february-7-25/kv-mechelen-vs-gent-betting-tips",
    "https://www.superior.tips/predictions/february-7-25/adelaide-united-vs-melbourne-city-betting-tips",
    "https://www.superior.tips/predictions/february-7-25/perth-glory-vs-central-coast-mariners-betting-tips",
    "https://www.superior.tips/predictions/february-7-25/fc-botosani-vs-dinamo-bucuresti-betting-tips",
    "https://www.superior.tips/predictions/february-7-25/cerro-largo-vs-progreso-betting-tips",
    "https://www.superior.tips/predictions/february-7-25/bangkok-united-vs-rayong-fc-betting-tips",
    "https://www.superior.tips/predictions/february-7-25/stal-mielec-vs-jagiellonia-betting-tips",
    "https://www.superior.tips/predictions/february-7-25/pogon-szczecin-vs-gornik-zabrze-betting-tips",
    "https://www.superior.tips/predictions/february-7-25/mtk-budapest-vs-debreceni-vsc-betting-tips",
    "https://www.superior.tips/predictions/february-7-25/lommel-united-vs-club-brugge-ii-betting-tips",
    "https://www.superior.tips/predictions/february-7-25/tekstilac-odzaci-vs-cukaricki-betting-tips",
    "https://www.superior.tips/predictions/february-7-25/omonia-29is-maiou-vs-omonia-nicosia-betting-tips",
    "https://www.superior.tips/predictions/february-7-25/al-ahli-doha-vs-qatar-sc-betting-tips",
    "https://www.superior.tips/predictions/february-7-25/umm-salal-vs-al-sadd-betting-tips",
    "https://www.superior.tips/predictions/february-7-25/al-duhail-sc-vs-al-wakrah-betting-tips",
    "https://www.superior.tips/predictions/february-7-25/northeast-united-vs-mumbai-city-betting-tips"
]

match_data = []

def scrape_match_data(url):
    # Send a GET request to the webpage
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract team performance metrics
        team_stats = {}
        team_stats_sections = soup.find_all('div', class_='team-stats')
        for stats in team_stats_sections:
            team_name_tag = stats.find('h3', class_='team-name')
            team_name = team_name_tag.text.strip() if team_name_tag else "Unknown"
            stat_items = stats.find_all('div', class_='stat-item')
            metrics = {}
            for item in stat_items:
                stat_name_tag = item.find('div', class_='stat-name')
                stat_value_tag = item.find('div', class_='stat-value')
                stat_name = stat_name_tag.text.strip() if stat_name_tag else "Unknown"
                stat_value = stat_value_tag.text.strip() if stat_value_tag else "Unknown"
                metrics[stat_name] = float(stat_value) if stat_name == "Average Goals per Game" else stat_value
            team_stats[team_name] = metrics

        # Extract recent matches
        recent_matches = {}
        recent_matches_sections = soup.find_all('div', class_='team-matches')

        for matches in recent_matches_sections:
            team_name_tag = matches.find('h3', class_='team-name')
            team_name = team_name_tag.text.strip() if team_name_tag else "Unknown"
            match_items = matches.find_all('div', class_='match-item')
            recent_matches[team_name] = []
            for match in match_items:
                home_team_tag = match.find('div', class_='team home')
                away_team_tag = match.find('div', class_='team away')
                score_tag = match.find('div', class_='score')
                home_team = home_team_tag.text.strip() if home_team_tag else team_name
                away_team = away_team_tag.text.strip() if away_team_tag else team_name
                score = score_tag.text.strip() if score_tag else "Unknown"
                recent_matches[team_name].append((home_team, score, away_team))

        # Extract head-to-head records
        head_to_head = []
        head_to_head_section = soup.find('section', class_='head-to-head-section')
        if head_to_head_section:
            match_items = head_to_head_section.find_all('div', class_='match-item')
            team_names = [team.text.strip() for team in head_to_head_section.find_all('h3', class_='team-name')]
            for match in match_items:
                home_team_tag = match.find('div', class_='team home')
                away_team_tag = match.find('div', class_='team away')
                score_tag = match.find('div', class_='score')
                home_team = home_team_tag.text.strip() if home_team_tag else "Unknown"
                away_team = away_team_tag.text.strip() if away_team_tag else "Unknown"
                score = score_tag.text.strip() if score_tag else "Unknown"

                # Replace "Unknown" with the appropriate team names
                if len(team_names) >= 2:
                    if home_team == "Unknown":
                        home_team = team_names[1] if away_team == team_names[0] else team_names[0]
                    if away_team == "Unknown":
                        away_team = team_names[1] if home_team == team_names[0] else team_names[0]

                head_to_head.append((home_team, score, away_team))

        # Extract prediction insights
        prediction_insight_section = soup.find('div', class_='prediction-card')
        if prediction_insight_section:
            prediction_text_tag = prediction_insight_section.find('p', class_='explanation-text')
            prediction_text = prediction_text_tag.text.strip() if prediction_text_tag else ""

            prediction_score_tag = prediction_insight_section.find('span', class_='main-prediction')
            prediction_score = prediction_score_tag.text.strip() if prediction_score_tag else ""

            confidence_level_tag = prediction_insight_section.find('span', class_='prediction-alt')
            confidence_level = confidence_level_tag.text.strip() if confidence_level_tag else ""

            win_rate_tag = prediction_insight_section.find('div', class_='probability-orb')
            win_rate = win_rate_tag.text.strip() if win_rate_tag else ""

            win_rates_tags = prediction_insight_section.find_all('div', class_='win-rate')
            win_rates_text = [rate.text.strip() for rate in win_rates_tags]

            # Extract best bets
            best_bets_tags = prediction_insight_section.find_all('span', class_='best-bet-chip')
            best_bets = [bet.text.strip() for bet in best_bets_tags]

            # Extract alternative predictions
            alt_prediction_container = prediction_insight_section.find('div', class_='alt-prediction-container')
            alt_predictions = []
            if alt_prediction_container:
                alt_predictions_tags = alt_prediction_container.find_all('span', class_='alt-prediction')
                alt_predictions = [pred.text.strip() for pred in alt_predictions_tags]
        else:
            prediction_text = ""
            prediction_score = ""
            confidence_level = ""
            win_rate = ""
            win_rates_text = []
            best_bets = []
            alt_predictions = []

        # Extract date, time, and country
        date_time_tag = soup.find('div', class_='date-time date-time-dark')
        date_time = date_time_tag.text.strip() if date_time_tag else "Unknown"

        country_tag = soup.find('span', class_='country-name')
        country = country_tag.text.strip() if country_tag else "Unknown"

        # Extract match names
        match_name_tag = soup.find('h2', class_='text-subtitle-1')
        match_name = match_name_tag.text.strip().split('|')[0].strip() if match_name_tag else "Unknown"

        # Function to calculate match outcomes using Poisson distribution
        def calculate_match_outcomes(team1_stats, team2_stats):
            # Estimate lambda for Poisson distribution
            lambda_team1 = team1_stats["Average Goals per Game"]
            lambda_team2 = team2_stats["Average Goals per Game"]

            # Calculate Poisson probabilities for a range of scores
            max_goals = 5  # Maximum number of goals to consider
            score_probs = {}
            for i in range(max_goals + 1):
                for j in range(max_goals + 1):
                    prob = poisson.pmf(i, lambda_team1) * poisson.pmf(j, lambda_team2)
                    score_probs[(i, j)] = prob

            # Get the top 3 most likely scores
            sorted_scores = sorted(score_probs.items(), key=lambda item: item[1], reverse=True)
            top_scores = sorted_scores[:3]

            # Calculate 1X2 probabilities
            prob_1 = sum(prob for (i, j), prob in score_probs.items() if i > j)
            prob_X = sum(prob for (i, j), prob in score_probs.items() if i == j)
            prob_2 = sum(prob for (i, j), prob in score_probs.items() if i < j)

            # Calculate BTTS probability
            prob_btts_yes = sum(prob for (i, j), prob in score_probs.items() if i > 0 and j > 0)
            prob_btts_no = 1 - prob_btts_yes

            # Calculate Over/Under probabilities
            over_under_probs = {}
            for k in range(4):
                prob_over = sum(prob for (i, j), prob in score_probs.items() if i + j > k + 0.5)
                prob_under = 1 - prob_over
                over_under_probs[f"Over {k + 0.5}"] = prob_over
                over_under_probs[f"Under {k + 0.5}"] = prob_under

            # Calculate Double Chance probabilities
            prob_1X = prob_1 + prob_X
            prob_12 = prob_1 + prob_2
            prob_X2 = prob_X + prob_2

            return {
                "top_scores": top_scores,
                "1X2": {"1": prob_1, "X": prob_X, "2": prob_2},
                "BTTS": {"Yes": prob_btts_yes, "No": prob_btts_no},
                "Over/Under": over_under_probs,
                "Double Chance": {"1X": prob_1X, "12": prob_12, "X2": prob_X2}
            }

        # Predict possible correct scores and other metrics
        team_names = list(team_stats.keys())
        if len(team_names) >= 2:
            predictions = calculate_match_outcomes(team_stats[team_names[0]], team_stats[team_names[1]])

            return {
                "country": country,
                "date_time": date_time,
                "match_name": match_name,
                "recent_matches": recent_matches,
                "head_to_head": head_to_head,
                "prediction_score": f"{prediction_score} or {', '.join(alt_predictions)}" if alt_predictions else prediction_score,
                "confidence_level": confidence_level,
                "win_rate": win_rate,
                "win_rates_text": win_rates_text,
                "prediction_text": prediction_text,
                "top_scores": predictions["top_scores"],
                "1X2": predictions["1X2"],
                "BTTS": predictions["BTTS"],
                "Over/Under": predictions["Over/Under"],
                "Double Chance": predictions["Double Chance"],
                "team_names": team_names,
                "best_bets": best_bets,
                "alt_predictions": alt_predictions,
                "team_stats": team_stats  # Include team stats in the returned data
            }
        else:
            return {
                "country": country,
                "date_time": date_time,
                "match_name": match_name,
                "recent_matches": recent_matches,
                "head_to_head": head_to_head,
                "prediction_score": prediction_score,
                "confidence_level": confidence_level,
                "win_rate": win_rate,
                "win_rates_text": win_rates_text,
                "prediction_text": prediction_text,
                "top_scores": [],
                "1X2": {},
                "BTTS": {},
                "Over/Under": {},
                "Double Chance": {},
                "team_names": team_names,
                "best_bets": best_bets,
                "alt_predictions": alt_predictions,
                "team_stats": team_stats  # Include team stats in the returned data
            }
    else:
        return None

def load_match_data():
    global match_data
    match_data = []
    for index, url in enumerate(urls):
        data = scrape_match_data(url)
        if data:
            match_data.append(data)

@app.route('/')
def index():
    return render_template('index.html', match_data=match_data)

@app.route('/match/<int:match_id>')
def match(match_id):
    if 0 <= match_id < len(match_data):
        data = match_data[match_id]
        return render_template('match.html', data=data)
    else:
        return "Invalid selection.", 404

@app.route('/refresh')
def refresh():
    # Reload match data
    threading.Thread(target=load_match_data).start()
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Load match data in a separate thread to avoid blocking the main thread
    threading.Thread(target=load_match_data).start()
    app.run(debug=False)
