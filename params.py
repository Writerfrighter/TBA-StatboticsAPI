team_number = 492  # Your team number
allowed_file_extensions = ["xlsx", "xlsx"]  # Used for data processing

upload_folder = "scouting_data"  # Directory for where the folders are updated
download_folder = "processed_data"  # Directory where processed data is stored and where users download data

#
# Data-correction/Completion
#

auto_replace_team_names = True  # Enable autocorrect for invalid team numbers
team_number_threshold = 2  # Threshold for characters when finding team replacements

location_dependent_comparisions = [
    # {
    #     "tba_format_name": "autoChargeStationRobot%",
    #     "xlsx_name": "Auto Engaged Docked State",
    #     "xslx_tba_pairs": {
    #         "None Docked": "None",
    #         "Alliance Member Docked": "None",
    #         "Docked": "Docked",
    #         "Docked and Engaged": "Engaged"
    #     }
    # },
    # {
    #     "tba_format_name": "endGameChargeStationRobot%",
    #     "xlsx_name": "Endgame Robot State",
    #     "xlsx_tba_pairs": {
    #         "No Points": "None",
    #         "Docked": "Docked",
    #         "Engaged": "Engaged",
    #         "Parked": "Park"
    #     }
    # },
    # TODO: Must depend on other variables/values.
    {
        "index": 4,
        "tba_format_name": "mobilityRobot%",
        "xlsx_name": "Left Community",
        "xlsx_tba_pairs": {True: "Yes", False: "No"},
    },
]

length_of_list_comparisons = [
    {"index": 16, "tba_name": "links", "xlsx_name": "Teleop Links"},
]  # (Index in xlsx that the value is in, list name as on TBA, xlsx Header)

value_comparisons = [
    # {
    #     "tba_name": "autoGamePieceCount",
    #     "xlsx_data": [
    #         {"index": 6, "xlsx_name": "Auto Scored Low"},
    #         {"index": 7, "xlsx_name": "Auto Scored Med"},
    #         {"index": 8, "xlsx_name": "Auto Scored High"},
    #     ],
    # }, Won't work since sum over teams
]  # (value name as on TBA, [(Index in xlsx that value is in, xlsx Header), ...)])


bonuses = [
    {
        "index": 24,
        "tba_name": "activationBonusAchieved",
        "xlsx_name": "Endgame Sustainability Bonus",
    },
    {
        "index": 23,
        "tba_name": "coopertitionCriteriaMet",
        "xlsx_name": "Endgame Coopertition Bonus",
    },
    {
        "index": 22,
        "tba_name": "sustainabilityBonusAchieved",
        "xlsx_name": "Endgame Activation Bonus",
    },
]  # (Index in xlsx that the bonus is, Bonus names as on TBA, xlsx Header)
