team_number = 492  # Your team number
allowed_file_extensions = ["csv", "xlsx"]  # Used for data processing

upload_folder = "scouting_data"  # Directory for where the folders are updated
download_folder = "processed_data"  # Directory where processed data is stored and where users download data

scouting_based_on_signs = False  # Wether or not the scouting data robot numbers were based on their alliance number
bonuses = [
    (24, "activationBonusAchieved", "Endgame Sustainability Bonus"),
    (23, "coopertitionCriteriaMet", "Endgame Coopertition Bonus"),
    (22, "sustainabilityBonusAchieved", "Endgame Activation Bonus"),
]  # (Index in xlsx that the bonus is, Bonus names as on TBA, CSV Header)
auto_replace_team_names = True  # Enable autocorrect for invalid team numbers
team_number_threshold = 2  # Threshold for characters when finding team replacements
