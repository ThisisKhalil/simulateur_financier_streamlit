import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

st.set_page_config(page_title="Simulateur Financier", layout="centered")
st.title("💸 Simulateur Financier")

# === UTILS ===
def calcul_ir(revenu):
    if revenu <= 5000:
        return 0
    elif revenu <= 20000:
        return (revenu - 5000) * 0.10
    elif revenu <= 40000:
        return 1500 + (revenu - 20000) * 0.20
    elif revenu <= 60000:
        return 1500 + 4000 + (revenu - 40000) * 0.30
    else:
        return 1500 + 4000 + 6000 + (revenu - 60000) * 0.38

st.header("1️⃣ Revenus")
salaire_brut = st.number_input("Salaire brut de base (MAD)", min_value=0.0, step=100.0)
primes = st.number_input("Primes mensuelles (MAD)", min_value=0.0, step=100.0)
heures_sup = st.number_input("Heures supplémentaires / mois", min_value=0.0, step=1.0)
taux_horaire = st.number_input("Taux horaire des heures sup (MAD/h)", min_value=0.0, step=10.0)

revenu_avant_ir = salaire_brut + primes + (heures_sup * taux_horaire)
cnss = revenu_avant_ir * 0.15
amo = revenu_avant_ir * 0.05
formation = revenu_avant_ir * 0.01
revenu_imposable = revenu_avant_ir - cnss
ir = calcul_ir(revenu_imposable)
salaire_net = revenu_avant_ir - (cnss + amo + formation + ir)

st.success(f"Salaire Net : {salaire_net:.2f} MAD")

st.header("2️⃣ Crédits")
mensualite_immobilier = st.number_input("Mensualité crédit immobilier (MAD)", min_value=0.0, step=100.0)
duree_immobilier = st.number_input("Durée restante crédit immobilier (mois)", min_value=0, step=1)
mensualite_voiture = st.number_input("Mensualité crédit voiture (MAD)", min_value=0.0, step=100.0)
duree_voiture = st.number_input("Durée restante crédit voiture (mois)", min_value=0, step=1)
taux_interet = st.number_input("Taux d'intérêt annuel (%)", min_value=0.0, step=0.1) / 100

total_immobilier = mensualite_immobilier * duree_immobilier
interet_immobilier = total_immobilier * taux_interet
total_voiture = mensualite_voiture * duree_voiture
interet_voiture = total_voiture * taux_interet

st.header("3️⃣ Dépenses et Épargne")
autres_depenses = st.number_input("Autres dépenses mensuelles (MAD)", min_value=0.0, step=100.0)
total_depenses = mensualite_immobilier + mensualite_voiture + autres_depenses
epargne = salaire_net - total_depenses

if epargne < 0:
    st.error(f"❗ Déficit budgétaire : {-epargne:.2f} MAD")
else:
    st.success(f"✅ Épargne mensuelle : {epargne:.2f} MAD")

st.header("4️⃣ Conseils d'investissement")
if epargne < 1000:
    st.info("💡 Conseil : commence par épargner davantage, pense à un livret d'épargne simple.")
elif epargne < 5000:
    st.info("💡 Conseil : pense à des investissements modestes comme les fonds communs ou un petit projet.")
else:
    st.info("🚀 Conseil : tu peux envisager la bourse ou lancer un projet personnel solide.")

# Projection
st.header("5️⃣ Projection sur 12 mois")
inflation = 0.02
augmentation_salaire = 0.03

mois = [f"M{i+1}" for i in range(12)]
epargne_projection = []
epargne_projection_reelle = []
salaire_evolutif = salaire_net

for i in range(12):
    salaire_evolutif *= (1 + augmentation_salaire)
    epargne_i = salaire_evolutif - total_depenses
    epargne_projection.append(epargne_i)
    epargne_projection_reelle.append(epargne_i / ((1 + inflation) ** i))

# Graphique ligne
fig, ax = plt.subplots()
ax.plot(mois, epargne_projection, marker='o', label="Épargne nominale")
ax.plot(mois, epargne_projection_reelle, marker='s', label="Épargne réelle (inflation)")
ax.set_title("📈 Projection Épargne sur 12 Mois")
ax.set_xlabel("Mois")
ax.set_ylabel("MAD")
ax.legend()
ax.grid(True)
st.pyplot(fig)

# Graphique camembert
st.subheader("Répartition des Dépenses")
labels = ['Crédit Immo', 'Crédit Voiture', 'Autres Dépenses', 'Épargne']
values = [mensualite_immobilier, mensualite_voiture, autres_depenses, max(epargne, 0)]
fig2, ax2 = plt.subplots()
ax2.pie(values, labels=labels, autopct='%1.1f%%')
ax2.set_title("Répartition des Dépenses")
ax2.axis('equal')
st.pyplot(fig2)

# Résumé Excel
st.header("📁 Export Excel")
resume_df = pd.DataFrame({
    "Détail": [
        "Salaire Net", "Total Dépenses", "Épargne",
        "Crédit Immo Total", "Intérêt Immo",
        "Crédit Voiture Total", "Intérêt Voiture",
        "Impôt sur le Revenu (IR)", "Cotisations Sociales"
    ],
    "Montant (MAD)": [
        salaire_net, total_depenses, epargne,
        total_immobilier, interet_immobilier,
        total_voiture, interet_voiture,
        ir, cnss + amo + formation
    ]
})

buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
    resume_df.to_excel(writer, sheet_name='Résumé', index=False)
    pd.DataFrame({
        "Catégorie": labels,
        "Montant (MAD)": values
    }).to_excel(writer, sheet_name='Répartition Dépenses', index=False)
    pd.DataFrame({
        "Mois": mois,
        "Épargne nominale": epargne_projection,
        "Épargne réelle (inflation)": epargne_projection_reelle
    }).to_excel(writer, sheet_name='Projection Épargne', index=False)
    writer.close()

st.download_button(
    label="📥 Télécharger Résumé Excel",
    data=buffer,
    file_name="resume_financier.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
