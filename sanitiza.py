import pandas as pd

# Carregar os CSVs
planilha1 = pd.read_csv("planilha1.csv", header=None, names=["nome", "telefone", "cidade"])
planilha2 = pd.read_csv("planilha2.csv", header=None, names=["nome", "telefone", "cidade"])

# Concatenar as planilhas
# Colocamos planilha2 depois para que ela tenha prioridade nas duplicatas
planilha_completa = pd.concat([planilha1, planilha2])

# Remover duplicatas com base em nome + telefone, mantendo a última ocorrência (planilha2)
planilha3 = planilha_completa.drop_duplicates(subset=["nome", "telefone", "cidade"], keep="last")

# Mostrar resultado
print(planilha3)

# Salvar CSV final
planilha3.to_csv("planilha3.csv", index=False)
