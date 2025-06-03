import streamlit as st
import pandas as pd
import numpy as np

st.title("Crashout Strategy Optimizer")

st.sidebar.header("Input Parameters")
budget = st.sidebar.number_input("Total Budget ($)", min_value=1.0, value=140.0, step=1.0)
initial_stake = st.sidebar.number_input("Starting Bet ($)", min_value=0.01, value=0.60, step=0.01)
cashout = st.sidebar.number_input("Cashout Multiplier", min_value=1.01, value=1.39, step=0.01)
multiplier = st.sidebar.number_input("Loss Multiplier", min_value=1.01, value=3.50, step=0.01)
num_losses = st.sidebar.slider("Consecutive Losses Before Win", min_value=1, max_value=10, value=5)

st.header("1. Loss Streak Table")
stakes = []
cumulative_loss = 0.0

for i in range(num_losses + 1):
    bet = initial_stake * (multiplier ** i)
    if i < num_losses:
        cumulative_loss += bet
    payout = bet * cashout
    profit = payout - cumulative_loss - bet if i == num_losses else None
    stakes.append({
        "Round": i + 1,
        "Bet ($)": round(bet, 4),
        "Cumulative Loss ($)": round(cumulative_loss, 4) if i < num_losses else "-",
        "Payout on Win ($)": round(payout, 4),
        "Net Profit if Win Here ($)": round(profit, 4) if profit is not None else "-"
    })

st.dataframe(pd.DataFrame(stakes))

st.header("2. Max Starting Stake for Budget")

def geometric_sum(mult, n):
    return sum([mult ** i for i in range(n)])

sum_multipliers = geometric_sum(multiplier, num_losses)
max_starting_stake = budget / sum_multipliers
st.write(f"Maximum starting stake within ${budget} for {num_losses} losses: **${round(max_starting_stake, 4)}**")

st.header("3. Minimum Safe Multiplier")

def find_min_safe_multiplier(init, cashout, losses, target_profit=0.01):
    for m in np.arange(1.01, 5.0, 0.01):
        total_loss = sum([init * (m ** i) for i in range(losses)])
        final_bet = init * (m ** losses)
        payout = final_bet * cashout
        profit = payout - total_loss - final_bet
        if profit >= target_profit:
            return round(m, 4), round(profit, 4)
    return None, None

safe_mult, safe_profit = find_min_safe_multiplier(initial_stake, cashout, num_losses)

if safe_mult:
    st.write(f"Minimum safe multiplier to guarantee profit after {num_losses} losses and a win: **{safe_mult}x**, profit: **${safe_profit}**")
else:
    st.write("No safe multiplier found within range")
