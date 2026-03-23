import pandas as pd

# Answers to the 10 reference problems
answers = {
    "0e644e": 336,
    "26de63": 32951,
    "424e18": 21818,
    "42d360": 32193,
    "641659": 57447,
    "86e8e5": 8687,
    "92ba6a": 50,
    "9c1c5f": 580,
    "a295e9": 520,
    "dd7f5e": 160
}

# Create a dataframe and save to recurring.parquet
df = pd.DataFrame(list(answers.items()), columns=['id', 'answer'])
df.to_parquet('recurring.parquet')
print("recurring.parquet created with 10 entries.")
