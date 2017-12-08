import pandas as pd
import numpy as np


# Converting the moneyline to a payout ratio that can be multiplied by the number of units for profit number
def convert_ml(ml):
    if ml < 0:
        payout_ratio = 100. / abs(ml)
    else:
        payout_ratio = ml / 100.
    return payout_ratio


# Sometimes Bovada does not have lines, replacing those with the optimistic lines
def correct_bov(row):
    if row["BovLine"] == 0.1:
        to_return = pd.Series({"TrueBovLine":row["OptLine"],
                               "TrueBovPayout":row["OptPayout"]})
    else:
        to_return = pd.Series({"TrueBovLine":row["BovLine"],
                               "TrueBovPayout":row["BovPayout"]})
    return to_return


# Applied to each row (game) in the dataset
def calculate_system_game(row, line_type, threshold=-4):
    if row["%sLine" % line_type] >= threshold and row["Away-B2B-Indicator"] == 1:
        game = 1  # Counting the number of games that fit the system requirements (boolean statement above)
        win = int(row["Home-1stHalf"] - row["Away-1stHalf"] + row["%sLine" % line_type] > 0)
        loss = int(row["Home-1stHalf"] - row["Away-1stHalf"] + row["%sLine" % line_type] < 0)
        push = int(row["Home-1stHalf"] - row["Away-1stHalf"] + row["%sLine" % line_type] == 0)
        if win == 1:
            profit = convert_ml(row["%sPayout" % line_type]) * 1.0
        elif loss == 1:
            profit = -1.0
        else:  # A push
            profit = 0.0
    else:
        game, win, loss, push, profit = 0, 0, 0, 0, 0
    return pd.Series({"Games":game,
                      "Wins":win,
                      "Losses":loss,
                      "Push":push,
                      "Profit":profit})

if __name__ == "__main__":
    years = [12, 13, 14, 15, 16, 17]
    full_df = pd.DataFrame()  # For keeping track of the cumulative results

    for year in years:
        year_string = "%d%d" % (year, year+1)
        input_filepath = "C:/Users/robsc/Documents/Data and Stats/ScrapedData/NBA/HalfSpreads%s.csv" % year_string
        output_filepath = "C:/Users/robsc/Documents/Data and Stats/ScrapedData/NBA/SystemResults%s.csv" % year_string
        sdata = pd.read_csv(input_filepath, encoding='latin1')

        # Adding in useful columns calculated from data
        sdata["Away-1stHalf"] = sdata["Away-1stQuarter"] + sdata["Away-2ndQuarter"]
        sdata["Home-1stHalf"] = sdata["Home-1stQuarter"] + sdata["Home-2ndQuarter"]
        sdata[["TrueBovLine", "TrueBovPayout"]] = sdata.apply(correct_bov, axis=1)

        # Calculating the number of games that fit as well as win/loss/profit counts
        OptAll = sdata.apply(calculate_system_game, axis=1, line_type="Opt", threshold=-999)
        OptThreshold = sdata.apply(calculate_system_game, axis=1, line_type="Opt", threshold=-4)
        BovAll = sdata.apply(calculate_system_game, axis=1, line_type="Bov", threshold=-999)
        BovThreshold = sdata.apply(calculate_system_game, axis=1, line_type="Bov", threshold=-4)
        PesAll = sdata.apply(calculate_system_game, axis=1, line_type="Pes", threshold=-999)
        PesThreshold = sdata.apply(calculate_system_game, axis=1, line_type="Pes", threshold=-4)

        sdata["Optimistic-CProfit-All"] = np.cumsum(OptAll["Profit"])
        sdata["Optimistic-CProfit-Threshold"] = np.cumsum(OptThreshold["Profit"])

        sdata.to_csv("C:/Users/robsc/Documents/Data and Stats/ScrapedData/NBA/HalfSpreads%s-Profit.csv" % year_string)

        # Summing up the individual counts of rows to get season totals for each system
        system_list = [OptAll.sum(), OptThreshold.sum(), BovAll.sum(), BovThreshold.sum(), PesAll.sum(), PesThreshold.sum()]
        summary_df = pd.DataFrame(system_list, index=["Optimistic-All", "Optimistic-Threshold", "Bovada-All", "Bovada-Threshold", "Pessimistic-All", "Pessimistic-Threshold"])
        summary_df["WinPercent"] = summary_df["Wins"] / (summary_df["Wins"] + summary_df["Losses"])
        summary_df["Games-NoPush"] = summary_df["Games"] - summary_df["Push"]

        summary_df.to_csv(output_filepath)

        if full_df.shape[0] == 0:
            full_df = summary_df.copy()
        else:
            full_df += summary_df

    full_df["WinPercent"] = full_df["Wins"] / full_df["Games-NoPush"]
    print(full_df)
    full_df.to_csv("C:/Users/robsc/Documents/Data and Stats/ScrapedData/NBA/SystemResultsL5.csv")




