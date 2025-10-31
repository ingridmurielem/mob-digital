import pandas as pd
from ipywidgets import FileUpload, Button, VBox, Label
from IPython.display import display
from io import StringIO

# Interface
label1 = Label("📄 Selecione a Planilha 1 (antiga):")
upload1 = FileUpload(accept='.csv', multiple=False)

label2 = Label("📄 Selecione a Planilha 2 (nova):")
upload2 = FileUpload(accept='.csv', multiple=False)

button = Button(description="🔄 Gerar Planilha Final", button_style='success')
output_label = Label()

def process_files(_):
    if not upload1.value or not upload2.value:
        output_label.value = "⚠️ Selecione as duas planilhas antes de continuar!"
        return

    # Ler CSVs
    file1 = list(upload1.value.values())[0]
    file2 = list(upload2.value.values())[0]
    df1 = pd.read_csv(StringIO(file1['content'].decode('utf-8')))
    df2 = pd.read_csv(StringIO(file2['content'].decode('utf-8')))

    # Garantir colunas iguais
    if not all(df1.columns == df2.columns):
        output_label.value = "❌ As planilhas devem ter as mesmas colunas!"
        return

    # === Identificar coluna de telefone ===
    possible_keys = [col for col in df1.columns if "fone" in col.lower() or "tel" in col.lower()]
    if not possible_keys:
        output_label.value = "❌ Nenhuma coluna de telefone encontrada! Renomeie uma coluna para 'Telefone'."
        return

    telefone_col = possible_keys[0]

    # Padronizar coluna de telefone (remover espaços e deixar apenas dígitos)
    df1[telefone_col] = df1[telefone_col].astype(str).str.replace(r'\D', '', regex=True)
    df2[telefone_col] = df2[telefone_col].astype(str).str.replace(r'\D', '', regex=True)

    # Remover duplicados dentro da própria planilha, mantendo o último registro
    df1 = df1.drop_duplicates(subset=[telefone_col], keep='last')
    df2 = df2.drop_duplicates(subset=[telefone_col], keep='last')

    # === Detectar divergências ===
    merged_compare = df1.merge(df2, on=telefone_col, how='inner', suffixes=('_antigo', '_novo'))

    base_cols = [col for col in df1.columns if col != telefone_col]

    diff_mask = merged_compare.apply(
        lambda row: any(
            str(row[f"{col}_antigo"]).strip().lower() != str(row[f"{col}_novo"]).strip().lower()
            for col in base_cols
        ),
        axis=1
    )

    changed_rows = merged_compare.loc[diff_mask, [telefone_col] + [f"{col}_antigo" for col in base_cols] + [f"{col}_novo" for col in base_cols]]

    # === Mesclar, priorizando planilha nova ===
    # Removemos da antiga os telefones que já estão na nova
    df1_sem_duplicados = df1[~df1[telefone_col].isin(df2[telefone_col])]
    merged_df = pd.concat([df2, df1_sem_duplicados], ignore_index=True)

    # === Relatório ===
    total_antiga = len(df1)
    total_nova = len(df2)
    total_final = len(merged_df)
    novas_linhas = len(df2[~df2[telefone_col].isin(df1[telefone_col])])
    atualizadas = len(changed_rows)
    duplicatas_removidas = len(df1[df1[telefone_col].isin(df2[telefone_col])]) - atualizadas

    relatorio = f"""
📊 RELATÓRIO DE MUDANÇAS
────────────────────────────
🔹 Registros na planilha antiga: {total_antiga}
🔹 Registros na planilha nova: {total_nova}
🔹 Total na planilha final: {total_final}

🆕 Novos contatos adicionados: {novas_linhas}
🔁 Contatos atualizados (mesmo telefone, dados diferentes): {atualizadas}
♻️ Contatos idênticos substituídos sem mudança: {duplicatas_removidas}
"""

    # === Salvar resultados ===
    merged_df.to_csv("planilha_final.csv", index=False)
    with open("relatorio_mudancas.txt", "w", encoding="utf-8") as f:
        f.write(relatorio)

    if not changed_rows.empty:
        changed_rows.to_csv("linhas_divergentes.csv", index=False)

    mensagem_final = "✅ Planilha final gerada com sucesso!\n"
    mensagem_final += "📁 Arquivo: planilha_final.csv\n📄 Relatório: relatorio_mudancas.txt"
    if not changed_rows.empty:
        mensagem_final += "\n⚠️ Linhas com divergências salvas em: linhas_divergentes.csv"

    output_label.value = mensagem_final

# Ligar botão
button.on_click(process_files)

# Exibir interface
display(VBox([label1, upload1, label2, upload2, button, output_label]))
