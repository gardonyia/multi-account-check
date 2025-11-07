import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Többszörös fiókellenőrző", page_icon="🔍")

st.title("🔍 TPRO - Multi Account Checker")

st.markdown("### 📂 1. lépés: Töltsd fel a **Korábban törölt játékosok** .CSV fájlt")

deleted_file = st.file_uploader("Korábban töröltek CSV feltöltése", type="csv")

if deleted_file:
    try:
        deleted_df = pd.read_csv(deleted_file, sep=None, engine="python")
        deleted_df.columns = [c.strip().lower() for c in deleted_df.columns]

        if 'personal id' not in deleted_df.columns:
            st.error("❌ A feltöltött fájlban nincs 'Personal ID' vagy 'Personal Id' oszlop.")
        else:
            deleted_df['personal id'] = (
                deleted_df['personal id']
                .astype(str)
                .str.replace(r'_adatved|_adatve|_adatv', '', regex=True)
            )

            st.success("✅ Deleted Players fájl sikeresen beolvasva és megtisztítva.")

            st.markdown("### 📂 2. lépés: Töltsd fel a **Tegnap regisztráltak** .CSV fájlt")
            new_file = st.file_uploader("Tegnap regisztráltak CSV feltöltése", type="csv")

            if new_file:
                try:
                    new_df = pd.read_csv(new_file, sep=None, engine="python")
                    new_df.columns = [c.strip().lower() for c in new_df.columns]

                    if not {'personal id', 'user id'}.issubset(new_df.columns):
                        st.error("❌ A feltöltött fájlban nincs 'Personal ID' és 'User ID' oszlop.")
                    else:
                        total_new = new_df['personal id'].nunique()
                        # Összevetjük a két fájlt Personal ID alapján
matches = new_df[new_df['Personal ID'].isin(deleted_df['Personal ID'])]

# A régi (törölt) User ID-kat hozzárendeljük az újhoz
merged = pd.merge(
    matches,
    deleted_df[['Personal ID', 'User ID']],
    on='Personal ID',
    how='left',
    suffixes=('_new', '_old')
)

# Ha több törölt User ID is volt ugyanahhoz a Personal ID-hoz, azokat összevonjuk
merged_grouped = merged.groupby(
    ['Personal ID', 'User ID_new'], as_index=False
).agg({'User ID_old': lambda x: ', '.join(x.astype(str).unique())})

# Megmutatjuk az eredményt
st.dataframe(merged_grouped)

# Excel exporthoz
output = BytesIO()
with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
    merged_grouped.to_excel(writer, index=False, sheet_name='Találatok')
st.download_button(
    label="📊 Eredmények letöltése Excel formátumban",
    data=output.getvalue(),
    file_name="multi_account_check_results.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
                        match_count = matches.shape[0]

                        st.markdown(f"### 📊 Eredmény")
                        st.write(f"👤 **Új regisztrációk száma:** {total_new}")
                        st.write(f"⚠️ **Korábban töröltek között megtaláltak:** {match_count}")

                        if match_count > 0:
                            st.markdown("### 📋 Egyező felhasználók")
                            st.dataframe(matches[['user id', 'personal id']])

                            # Excel exportálás
                            output = BytesIO()
                            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                                matches.to_excel(writer, index=False, sheet_name='Egyezések')

                            st.download_button(
                                label="📥 Eredmények letöltése Excelben",
                                data=output.getvalue(),
                                file_name="egyezesek.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )

                except Exception as e:
                    st.error(f"⚠️ Hiba történt a második fájl feldolgozásakor: {e}")

    except Exception as e:
        st.error(f"⚠️ Hiba történt az első fájl feldolgozásakor: {e}")




